#
# This contains the base class for MicroPython boards and its subclasses.
#
from board import Board, ComPort, BoardConfig, ComPortType, ComPortSource, DebugProbeType
from dvk_probe import DvkProbe
from jlink_probe import JLinkProbe
from probe import Probe
from python_uart import PythonUart
from lc_util import logger_setup, logger_get
from zephyr_uart import ZephyrUart
import time
import serial.tools.list_ports as list_ports
import operator
import itertools

logger = logger_get(__name__)


class MicroPythonBoard(Board, PythonUart, ZephyrUart):
    """
    A class to represent a generic MicroPython Board.
    A user can use board config files to find any board that supports MircoPython.
    """
    #: :meta hide-value:
    #:
    #: Amount of time to wait after resetting board.
    BOOT_TIME_SECONDS = 6

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

        detected_ports = list_ports.comports()
        if len(detected_ports) < 0:
            logger.info("No serial ports detected")
            return boards

        if len(boards_conf) > 0:
            probes = Probe.get_connected_probes(with_comports=False)
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
                        x for x in detected_ports if x.serial_number == port.sn]
                    # Sort by location and device to make sure the ports are in
                    # order by lowest USB port index to largest.
                    # This is important because the REPL port is the first port enumerated.
                    matching_ports.sort(
                        key=operator.attrgetter('location', 'device'))
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
                if "probe" in board:
                    bprobe = board.probe
                    if "sn" not in bprobe:
                        continue
                    for p in probes:
                        if p.id == bprobe.sn:
                            probe = p
                            probes.remove(p)
                            break
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
        self._probe = probe
        self._user_board_name = board_name
        py_repl = self._repl.device
        zephyr_shell = ""
        if self._zephyr:
            zephyr_shell = self._zephyr.device
        self.__ports = {"python": py_repl, "zephyr_shell": zephyr_shell}

    def __str__(self):
        s = f"{self.board_name} {self._user_board_name} {self._repl.sn} [{self._repl.name}]: {self._repl.device}"
        if self._zephyr:
            s += f", [{self._zephyr.name}]: {self._zephyr.device}"
        return s

    def open_and_init_board(self):
        if self._probe:
            self._probe.open()
        self.open_ports()
        self.reset_module()
        self._initialized = True

    def close_ports(self):
        self.python_uart.close()
        if self._zephyr and self.zephyr_uart:
            self.zephyr_uart.close()

    def open_ports(self):
        PythonUart.__init__(self, self._repl.device)
        if self._zephyr:
            ZephyrUart.__init__(self, self._zephyr.device)

    def close_ports_and_reset(self, reset_probe: bool = True):
        self.close_ports()
        if self._probe:
            if reset_probe:
                self._probe.reboot()
            self._probe.close()

    def reset_module(self):
        """Hard reset the module with the debug probe if available, otherwise soft reset.
        """
        if self._probe:
            self._probe.reset_target()
            time.sleep(MicroPythonBoard.BOOT_TIME_SECONDS)
        else:
            self.soft_reset_module(False)

    def soft_reset_module(self, wait_response: bool = True):
        """Soft reset the module by sending Ctrl-D to the Python REPL."""
        resp = None
        if self._repl.source.casefold() == ComPortSource.BOARD.name.casefold():
            if wait_response:
                resp = self.python_uart.send(
                    b'\x04', MicroPythonBoard.BOOT_TIME_SECONDS)
            else:
                self.python_uart.send_raw(b'\x04')
                time.sleep(MicroPythonBoard.BOOT_TIME_SECONDS)
        else:
            self.python_uart.send_raw(b'\x04')
            self.close_ports()
            time.sleep(MicroPythonBoard.BOOT_TIME_SECONDS)
            self.open_ports()
        return resp

    @property
    def ports(self) -> dict:
        """Get the repl and zephyr shell serial port devices.
        This property is for compatibility with :func:`Board.get_by_com_port`.

        Returns:
            Dictionary of port names and devices
        """
        return self.__ports


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
        detected_ports = list_ports.comports()
        if len(detected_ports) < 0:
            return boards

        # Find the serial ports with matching VID and PID.
        matching_ports = [
            x for x in detected_ports if x.vid == BL654UsbDongle.USB_VID and x.pid == BL654UsbDongle.USB_PID]
        # Sort by location and device to make sure the ports are in
        # order by lowest USB port index to largest.
        # This is important because the REPL port is the first port enumerated.
        matching_ports.sort(
            key=operator.attrgetter('location', 'device'))

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
