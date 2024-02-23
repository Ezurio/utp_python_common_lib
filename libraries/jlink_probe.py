from probe import Probe, ProbePorts
from lc_util import logger_setup, logger_get
from pylink.jlink import JLink
import serial.tools.list_ports as list_ports

logger = logger_get(__name__)


class JLinkProbe(Probe):
    """
    Wrapper for the pylink.jlink module that combines probe discovery with
    serial port discovery.
    """

    def __init__(self,
                 id: int,
                 family: str,
                 description: str,
                 ports: ProbePorts):

        super().__init__(id, description, ports)
        self.__family = family
        self.__probe_handle = None

    @property
    def family(self) -> str:
        return self.__family

    def __str__(self):
        return super().__str__() + f", {self.family}"

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
    def get_connected_probes(family: str = "Cortex-M33", uart_interface_type: str = "python") -> list['JLinkProbe']:
        """
        Look for JLink probes.

        Args:
            family (str, optional): The family of the JLink probe. Defaults to "Cortex-M33".

        Returns:
            list['JLinkProbe']: List of JLink probes
        """
        probes = list()
        try:
            ports = JLinkProbe.__list_ports()
        except:
            pass

        if len(ports) == 0:
            logger.info("Zero JLink probes with comports found")
            return probes

        try:
            j_link = JLink()
        except:
            logger.error("Failed to create instance of jlink")

        for emu in j_link.connected_emulators():
            logger.debug(emu)
            try:
                j_link.open(emu.SerialNumber)
            except:
                logger.error(
                    f"Could not open JLink Probe: {emu.SerialNumber}")
                continue

            for i, (device, hwid) in enumerate(ports):
                logger.debug(
                    f"{i}, {device}, {hwid}, {str(emu.SerialNumber)}")
                # The value of the probe's serial number returned by get ports
                # may have leading zeros.
                if str(emu.SerialNumber) in hwid:
                    p = JLinkProbe(emu.SerialNumber,
                                   family,
                                   emu.acProduct.decode(),
                                   {uart_interface_type: device})
                    probes.append(p)

            j_link.close()

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
        if not self.__is_open():
            raise Exception(
                f"Unable to connect to target with probe {self.id}")

    def __is_open(self):
        """
        Read state of JLink probe
        """
        return self.__probe_handle.connected() and self.__probe_handle.target_connected()

    def close(self):
        self.__probe_handle.close()

    def reset_target(self):
        self.__probe_handle.reset(halt=False)

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


if __name__ == "__main__":
    logger = logger_setup(__file__)

    probes = JLinkProbe.get_connected_probes()
    logger.info(f"Number of J-Link probes with comports found: {len(probes)}")
    for b in probes:
        logger.info(b)
