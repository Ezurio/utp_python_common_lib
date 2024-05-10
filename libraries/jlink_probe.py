from probe import Probe
from lc_util import logger_setup, logger_get
from pylink.jlink import JLink
from pylink import JLinkInterfaces
import serial.tools.list_ports as list_ports

logger = logger_get(__name__)


class JLinkProbe(Probe):
    """
    Wrapper for the pylink.jlink module that combines probe discovery with
    serial port discovery.
    """

    def __init__(self,
                 id: int,
                 description: str = "",
                 ports=dict(),
                 family: str = ""):

        super().__init__(id, description, ports, family)
        self.__probe_handle = None

    @staticmethod
    def __list_ports(comport_description="JLink CDC UART Port") -> list:
        """
        Return a list of JLink probes that have serial com ports.
        """
        jlink_comport_info = list()
        for comport in list_ports.comports():
            logger.debug(comport)
            if comport_description in str(comport):
                jlink_comport_info.append(
                    tuple([comport.device, comport.hwid]))

        logger.debug(f"com port info: {jlink_comport_info}")
        return jlink_comport_info

    @staticmethod
    def get_connected_probes(family: str = "Cortex-M33", uart_interface_type: str = "python",
                             with_comports: bool = True) -> list['JLinkProbe']:
        """
        Look for JLink probes.

        Args:
            family (str, optional): The family of the JLink probe. Defaults to "Cortex-M33" if 
            with_comports is True. In order to discover com ports connected to a probe, 
            the family must be known.

            uart_interface_type (str, optional): The type of UART interface. Defaults to "python" if 
            with comports is True.

            with_comports (bool, optional): If True, only return probe with at least one comport. 
            When false, ignore comports. Defaults to True.

        Returns:
            list['JLinkProbe']: List of JLink probes
        """
        probes = list()
        try:
            ports = JLinkProbe.__list_ports()
            # Try with name found on Ubuntu and Raspberry Pi OS
            if len(ports) == 0:
                ports = JLinkProbe.__list_ports("J-Link OB - CDC")
        except:
            pass

        if with_comports and len(ports) == 0:
            logger.info("Zero JLink probes with comports found")
            return probes

        try:
            j_link = JLink()
        except:
            logger.error("Failed to create instance of jlink")

        for emu in j_link.connected_emulators():
            logger.debug(emu)
            # If a probe can't be opened, then don't consider it valid.
            try:
                j_link.open(emu.SerialNumber)
                j_link.close()
            except:
                logger.error(
                    f"Could not open JLink Probe: {emu.SerialNumber}")
                continue

            if with_comports:
                for i, (device, hwid) in enumerate(ports):
                    logger.debug(
                        f"{i}, {device}, {hwid}, {str(emu.SerialNumber)}")
                    # The value of the probe's serial number returned by get ports
                    # may have leading zeros.
                    if str(emu.SerialNumber) in hwid:
                        p = JLinkProbe(emu.SerialNumber,
                                       emu.acProduct.decode(),
                                       {uart_interface_type: device},
                                       family)
                        probes.append(p)
                        # For simplicity, only use the first port found.
                        # Can't differentiate port types at this time.
                        break
            else:
                p = JLinkProbe(emu.SerialNumber)
                probes.append(p)

        return probes

    def open(self):
        if self.__probe_handle == None:
            # Handle for probe operations (open DLL)
            self.__probe_handle = JLink()
            # Disable log messages from jlink module
            self.__probe_handle.detailed_log_handler = None
            self.__probe_handle.log_handler = None

        logger.info(f"Opening JLink probe {self.id}")
        if not self.__probe_handle.connected():
            self.__probe_handle.open(self.id)
        if not self.__probe_handle.target_connected():
            self.__probe_handle.connect(chip_name=self.family)
            # Try SWD if JTAG fails
            if not self.__is_open():
                self.__probe_handle.set_tif(JLinkInterfaces.SWD)
                self.__probe_handle.connect(chip_name=self.family)

        if not self.__is_open():
            raise Exception(
                f"Unable to connect to target with probe {self.id}")

    def __is_open(self):
        """
        Read state of JLink probe
        """
        logger.info(
            f"{self.id} {self.family} connected: {self.__probe_handle.connected()} target: {self.__probe_handle.target_connected()}")
        return self.__probe_handle.connected() and self.__probe_handle.target_connected()

    def close(self):
        self.__probe_handle.close()

    def reset_target(self):
        self.__probe_handle.reset(halt=False)

    def reboot(self):
        """
        Reboot the probe itself. Not supported for JLink.
        """
        pass

    def memory_read(self, address=0, length=0, close_after_read=True):
        """
        Read bytes from processor memory.

        Args:
            address (int, optional): Start address. Defaults to 0.
            length (int, optional): Number of bytes to read. Defaults to 0.
            close_after_read (bool, optional): Close the probe after reading. Defaults to True.
        """
        self.open()
        data = self.__probe_handle.memory_read(address, length)
        if close_after_read:
            self.close()
        return data

    def memory_read_as_string(self, address=0, length=0, close_after_read=True):
        """
        Read bytes and convert them into a string.
        Skips over non-printable characters.

        See :meth:`memory_read` for parameter details.
        """
        s = str()
        data = self.memory_read(address, length, close_after_read)
        for c in data:
            if c >= ord(' ') and c <= ord('~'):
                s += chr(c)
        return s

    def program_target(self, file_path: str, addr: any = 0):
        """Program the target with a file.

        Args:
            file_path (str): The file to program
            addr (any, optional): The address to program. Defaults to 0.
        """
        self.__probe_handle.reset()
        self.__probe_handle.flash_file(path=file_path, addr=addr)

if __name__ == "__main__":
    logger = logger_setup(__file__, True)

    probes = JLinkProbe.get_connected_probes()
    logger.info(f"Number of J-Link probes with comports found: {len(probes)}")
    for b in probes:
        logger.info(b)

    with_comports = False
    probes = JLinkProbe.get_connected_probes(with_comports=False)
    logger.info(
        f"Number of J-Link probes IGNORING comports found: {len(probes)}")
    for b in probes:
        logger.info(b)
