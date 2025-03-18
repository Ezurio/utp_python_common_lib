#
# This contains the base class for MicroPython boards and its subclasses.
#
from board import Board, ComPort, BoardConfig, ComPortType, ComPortSource, DebugProbeType
from dvk_probe import DvkProbe
from jlink_probe import JLinkProbe
from usb_swd_probe import UsbSwdProbe
from probe import Probe
from python_uart import PythonUart
from lc_util import logger_setup, logger_get
from zephyr_uart import ZephyrUart
import time
import port_helpers
import operator
import itertools
from program_using_commander_cli import program_lyra24, program_sl917

logger = logger_get(__name__)


class MicroPythonBoard(Board):
    """
    A class to represent a generic MicroPython Board.
    A user can use board config files to find any board that supports MicroPython.
    """
    DEFAULT_FLUSH_ATTEMPTS = 3

    @classmethod
    def get_specified(cls, boards_conf: list[BoardConfig]) -> list['MicroPythonBoard']:
        """ Get a list of all connected boards that match the specified board configurations.

        Args:
            boards_conf (list[BoardConfig]): List of board configs to search for and create.
            At a minimum, a board config must contain the serial port config for a REPL port.

            A board config yaml file would look like:
            boards:
              - name: p100_dvk_9517
                ports:
                  - sn: 1649CC3B1086D8A9
                    index: 0
                    type: repl
                    source: device
                    name: Python REPL
                  - sn: 1649CC3B1086D8A9
                    index: 1
                    type: zephyr
                    source: device
                    name: Zephyr shell
                probe:
                  sn: 483067853
                  type: jlink
                  name: P100 DVK Jlink OB
            A minimum board config would look like:
            boards:
              - ports:
                  - sn: 1649CC3B1086D8A9
                    index: 0
                    type: repl
                    source: device


        Returns:
            list['MicroPythonBoard']: List of connected boards
        """

        boards = []

        # Remove ports without a serial number because they are required for matching.
        # This allows membership test below to work correctly.
        # Membership test allows leading zeros in the serial number.
        detected_ports = port_helpers.get_ports()
        if len(detected_ports) < 0:
            logger.info("No valid serial ports detected")
            return boards

        if len(boards_conf) > 0:
            probes = Probe.get_connected_probes(with_comports=False)
            if len(probes) == 0:
                logger.warn("No probes found")
            for board in boards_conf:
                repl = None
                zephyr = None
                probe = None
                name = ""
                if "name" in board:
                    name = board.name
                for port in board.ports:
                    if "sn" not in port:
                        continue
                    if "index" not in port:
                        continue
                    if "type" not in port:
                        continue
                    if "source" not in port:
                        continue
                    # Find the matching ports in the list of detected ports by serial number.
                    # Serial number is the most reliable way to match ports because the device name
                    # can change depending on the order the devices are plugged in.
                    matching_ports = [
                        x for x in detected_ports if str(port.sn) in x.serial_number]
                    # Sort by location and device to make sure the ports are in
                    # order by lowest USB port index to largest.
                    # This is important because the REPL port is the first port enumerated.
                    # On Windows, the location may not be available.
                    try:
                        matching_ports.sort(
                            key=operator.attrgetter('location', 'device'))
                    except:
                        logger.info(
                            "Unable to sort ports by location and device."
                            "If populated, using device field.")
                        for y in matching_ports:
                            if str(port.sn) in y.serial_number:
                                if "device" in port:
                                    y.device = port.device

                    if len(matching_ports) >= (port.index + 1):
                        # Assign the device name to the port
                        port.device = matching_ports[port.index].device
                        if port.type.casefold() == ComPortType.REPL.name.casefold():
                            if "name" not in port:
                                port.name = "Python REPL"
                            repl = port
                        elif port.type.casefold() == ComPortType.ZEPHYR.name.casefold():
                            if "name" not in port:
                                port.name = "Zephyr shell"
                            zephyr = port
                    elif len(boards_conf) > 1:
                        # If there are mulitple boards, then this will most likely occur.
                        # If none of them match, then the board is not connected or
                        # there is a problem in the configuration file.
                        logger.debug("Ports did not match")

                # If the board configuration specifies a probe with a serial number,
                # try to find it in the list of connected probes.
                if "probe" in board:
                    bprobe = board.probe
                    if "sn" in bprobe:
                        for p in probes[:]:
                            if p.id == bprobe.sn:
                                probe = p
                                probes.remove(p)
                                if "family" in bprobe:
                                    probe.family = bprobe.family
                                break
                        if probe is None:
                            logger.warn(
                                f"Matching probe not found for board {name} with serial number {bprobe.sn}")
                if repl:
                    boards.append(MicroPythonBoard(repl, name, zephyr, probe))

        return boards

    def __init__(self, repl: ComPort,
                 board_name: str = "",
                 zephyr: ComPort | None = None,
                 probe: Probe | None = None,
                 id: str = ''):
        super().__init__(id=id)
        self._repl = repl
        self._zephyr = zephyr
        self.__probe = probe
        self._user_board_name = board_name
        self.__ports = dict()
        self.python_uart = PythonUart(self._repl.device)
        self.__ports["python"] = self._repl.device
        if self._zephyr:
            self.zephyr_uart = ZephyrUart(self._zephyr.device)
            self.__ports["zephyr_shell"] = self._zephyr.device
        else:
            self.zephyr_uart = None
            self.__ports["zephyr_shell"] = ""
        self._handle_reset = True
        # Amount of time to wait after resetting board before trying to open com port
        if self.coms_from_device():
            self.__com_port_delay_seconds = Board.DEFAULT_COM_PORT_FROM_DEVICE_DELAY_SECONDS
        else:
            self.__com_port_delay_seconds = Board.DEFAULT_COM_PORT_DELAY_SECONDS
        # Amount of time to wait after opening com port before trying to optionally flush rx buffer
        self.__delay_after_open_seconds = Board.BOOT_TIME_SECONDS
        self.__ports_have_been_opened = False

        if "rs2xx" in self._user_board_name.casefold():
            self.__delay_after_open_seconds = Board.BOOT_TIME_SECONDS_RS2XX

    def __str__(self):
        s = f"{self.board_name} {self._user_board_name} {self._repl.sn} [{self._repl.name}]: {self._repl.device}"
        if self._zephyr:
            s += f", [{self._zephyr.name}]: {self._zephyr.device}"
        return s

    @property
    def user_board_name(self) -> str:
        """
        Name provided in the board configuration file (optional).
        """
        return self._user_board_name

    @property
    def probe(self):
        return self.__probe

    def __open_probe(self):
        if self.probe:
            self.probe.open()
            # When connecting to the device, opening the probe may reset the device.
            # If the ports are part of the device, then a wait is required
            # for microcontroller to boot.
            self.__handle_reset = True

    def open_and_init_board(self):
        self.__handle_reset = True
        self.__open_probe()
        if self.probe:
            self.reset_module(reopen_ports=True)
        else:
            # If there isn't a probe, then the com port must be opened
            # so that a soft reset can be issued.
            self.open_ports()
            self.reset_module(reopen_ports=True)

        self._initialized = True

    def close_ports(self):
        if self.__ports_have_been_opened:
            self.python_uart.close_raw_repl_uart()
            self.python_uart.close()
            if self.zephyr_uart:
                self.zephyr_uart.close()
                logger.info(f"Closed Zephyr Uart {self.zephyr_uart.port_name}")

    def open_ports(self):
        # If the com ports are from the microcontroller (not the board),
        # then the device must boot and setup the USB interface.
        if self.__handle_reset:
            time.sleep(self.__com_port_delay_seconds)
            found = len(
                port_helpers.get_ports_with_serial_number(self._repl.sn))
            if not found:
                raise RuntimeError(
                    f"Could not find serial port for {self._repl.sn}")

        self.python_uart.wrapped_open(
            self.__delay_after_open_seconds, MicroPythonBoard.DEFAULT_FLUSH_ATTEMPTS if self.__handle_reset else 0)
        if self.zephyr_uart:
            self.zephyr_uart.wrapped_open()

        self.__handle_reset = False
        self.__ports_have_been_opened = True

    def close_ports_and_reset(self, reset_probe: bool = True):
        self.reset_module(reopen_ports=False)
        if self.probe:
            if reset_probe:
                self.probe.reboot()
            self.probe.close()
        self._initialized = False

    def reset_module(self, reopen_ports: bool = True):
        """Hard reset the module with the debug probe if available, otherwise soft reset.
        """
        if self.probe:
            self.hard_reset_module(reopen_ports)
        else:
            self.soft_reset_module(reopen_ports)

    def hard_reset_module(self, reopen_ports: bool = True):
        """
        Since the UARTs may be connected to the Python processor's USB interface, 
        the ports are closed and then reopened.
        For simplicity, the com port is always closed first and then opened
        after the reset is issued.
        """
        logger.info("Hard reset module")
        self.__handle_reset = True
        self.close_ports()
        self.probe.reset_target()
        if reopen_ports:
            self.open_ports()

    def soft_reset_module(self, reopen_ports: bool = True):
        """Soft reset the module by sending Ctrl-D to the Python REPL."""
        # If a failure occurred when trying to open raw REPL, then the normal REPL is closed
        # and a reset cannot be sent.
        logger.info("Soft reset module")
        self.__handle_reset = True
        self.python_uart.send_raw(b'\x04')
        self.python_uart.port.flush()
        self.close_ports()
        if reopen_ports:
            self.open_ports()

    def coms_from_device(self) -> bool:
        """ Com ports are from a USB port on the microcontoller """
        return self.repl_from_device() or self.zephyr_from_device()

    def repl_from_board(self) -> bool:
        return self._repl.source.casefold() == ComPortSource.BOARD.name.casefold()

    def repl_from_device(self) -> bool:
        return self._repl.source.casefold() == ComPortSource.DEVICE.name.casefold()

    def zephyr_from_device(self) -> bool:
        if self._zephyr:
            return self._zephyr.source.casefold() == ComPortSource.DEVICE.name.casefold()
        else:
            return False

    @property
    def ports(self) -> dict:
        """Get the repl and zephyr shell serial port devices.
        This property is for compatibility with :func:`Board.get_by_com_port`.

        Returns:
            Dictionary of port names and devices
        """
        return self.__ports

    def program_mcu(self, file_path: str, board_name: str, addr: any = 0):
        """Program the target with a file.

        Args:
            file_path (str): The file to program
            board_name (str): A name that matches the class name (after conversion).
            addr (any): The address to program the file to.
        """
        if not file_path:
            raise ValueError("File path invalid")
        if not board_name:
            raise ValueError("Board name invalid")
        if not self.probe:
            raise RuntimeError("No probe to program with")

        # open_and_init_board may not have been called.
        self.__open_probe()
        if not self.probe.id:
            raise ValueError("Probe ID invalid")

        match = False
        if board_name.casefold() in self._user_board_name.casefold():
            match = True
        elif self.__class__.in_name(board_name):
            match = True

        if not match:
            logger.info("Not programming board because name doesn't match")
            return

        if self._initialized:
            self.close_ports()

        # Python J-link programming doesn't work for Lyra24 or SL917
        if "lyra24".casefold() in board_name.casefold():
            self.probe.close()
            program_lyra24(file_path, str(self.probe.id))
        elif "brd2911a".casefold() in board_name.casefold():
            self.probe.close()
            program_sl917(file_path, str(self.probe.id))
        elif "brd2708a".casefold() in board_name.casefold():
            self.probe.close()
            program_sl917(file_path, str(self.probe.id))
        else:
            self.probe.program_target(file_path, addr)

        if self._initialized:
            self.__handle_reset = True
            self.open_ports()

        logger.info(
            f"Read version to confirm programming for {self._user_board_name}")

# TODO: How do we differentiate between the different boards?
# The USB PID/VID can be used for devices that have a USB interface (Pinnacle 100 DVK and BL5340).
# The MG100 uses an FTDI device so discovery via VID/PID will not work.
# The board config passed to get_connected could have a board property to identify the board.


class Pinnacle100Dvk(MicroPythonBoard):
    """
    A class to represent the Pinnacle 100 DVK Board.
    """

    def __init__(self, repl: ComPort,
                 board_name: str = "",
                 zephyr: ComPort | None = None,
                 probe: Probe | None = None):
        super().__init__(repl, board_name, zephyr, probe)


class MG100(MicroPythonBoard):
    """
    A class to represent the MG100.
    """

    def __init__(self, repl: ComPort,
                 board_name: str = "",
                 zephyr: ComPort | None = None,
                 probe: Probe | None = None):
        super().__init__(repl, board_name, zephyr, probe)


class BL5340Dvk(MicroPythonBoard):
    """
    A class to represent the BL5340 DVK Board.
    """

    def __init__(self, repl: ComPort,
                 board_name: str = "",
                 zephyr: ComPort | None = None,
                 probe: Probe | None = None):
        super().__init__(repl, board_name, zephyr, probe)


class BL654UsbDongle(MicroPythonBoard, Board):
    """
    A class to represent the BL654 USB Dongle.
    """

    USB_VID = 0x3016
    USB_PID = 0x0003

    def __init__(self, repl: ComPort,
                 board_name: str = '',
                 zephyr: ComPort | None = None,
                 probe: Probe | None = None,
                 id: str = ''):
        super().__init__(repl, board_name, zephyr, probe, id)

    @classmethod
    def get_connected(cls, allow_list=list()) -> list['BL654UsbDongle']:
        """ Get a list of all connected boards.

        Args:
            allow_list (list[str]): List of board names to allow.
            Since this isn't subclassed, the allow list isn't used.

        Returns:
            list['BL654UsbDongle']: List of connected boards
        """

        boards = []
        detected_ports = port_helpers.get_ports()
        if len(detected_ports) < 0:
            return boards

        # Find the serial ports with matching VID and PID.
        matching_ports = [
            x for x in detected_ports if x.vid == BL654UsbDongle.USB_VID and x.pid == BL654UsbDongle.USB_PID]
        # Sort by location and device to make sure the ports are in
        # order by lowest USB port index to largest.
        # This is important because the REPL port is the first port enumerated.
        try:
            matching_ports.sort(
                key=operator.attrgetter('location', 'device'))
        except:
            logger.info("Unable to sort BL6554 USB ports")

        # Group the matching ports by serial number and create a board for each group.
        for k, g in itertools.groupby(matching_ports, key=lambda x: x.serial_number):
            ports = list(g)
            repl_index = 0
            zephyr_index = 1
            repl_port = ports[repl_index]
            zephyr_port = ports[zephyr_index]
            repl = ComPort({
                "sn": repl_port.serial_number,
                "index": repl_index,
                "type": ComPortType.REPL.name.casefold(),
                "source": ComPortSource.DEVICE.name.casefold(),
                "name": "Python REPL",
                "device": repl_port.device
            })
            zephyr = ComPort({
                "sn": zephyr_port.serial_number,
                "index": zephyr_index,
                "type": ComPortType.ZEPHYR.name.casefold(),
                "source": ComPortSource.DEVICE.name.casefold(),
                "name": "Zephyr shell",
                "device": zephyr_port.device
            })
            boards.append(BL654UsbDongle(repl=repl, zephyr=zephyr, id=k))

        return boards
