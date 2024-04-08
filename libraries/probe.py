from lc_util import logger_setup, logger_get
import serial.tools.list_ports as list_ports

logger = logger_get(__name__)

class Probe:
    """
    Base class for debug/programming probe.

    It contains methods that are common to all probes and
    stubs for those that must be implemented by subclasses.
    """
    def __init__(self,
                 id=None | int | str,
                 description: str = "",
                 ports=dict()):

        self.__id = id
        self.__description = description
        self.__ports = ports

    def __str__(self):
        s = f"{self.name} {self.id}"
        for key, value in self.ports.items():
            if value != "":
                s += f", {key.capitalize()} port: {value}"
        return s

    def __del__(self):
        try:
            self.close()
        except:
            pass

    @property
    def id(self):
        return self.__id

    @property
    def ports(self) -> dict:
        return self.__ports

    @property
    def name(self):
        """
        Matches class name.
        """
        return self.__class__.__name__

    @property
    def description(self):
        """
        Detailed name read from probe.
        """
        return self.__description

    @classmethod
    def get_connected_probes(cls, with_comports: bool = True) -> list:
        """
        Look for all probes that are defined in the current scope.
        
        Args:
            with_comports (bool, optional): If True, only return probes with comports. Defaults to True.
        """
        probes = list()
        for subclass in cls.__subclasses__():
            probes.extend(subclass.get_connected_probes(with_comports=with_comports))

        return probes

    def open(self):
        """
        Open the USB connection to the probe and connect to the target.
        """
        raise NotImplementedError

    def close(self):
        """
        Close the probe.
        """
        raise NotImplementedError

    def reset_target(self):
        """
        Reset the target device with the reset line.
        """
        raise NotImplementedError

    def reboot(self):
        """
        Reboot the probe itself.
        """
        raise NotImplementedError

    @staticmethod
    def get_com_port_info(port: str):
        """Get the detailed COM port information for the probe.

        Args:
            port (str): The COM port name

        Returns:
            ListPortInfo: COM port information
        """

        for comport in list_ports.comports():
            if port == comport.device:
                return comport


if __name__ == "__main__":
    logger = logger_setup(__file__)

    probes = Probe.get_connected_probes()
    logger.info(f"Probes found: {len(probes)}")
    for p in probes:
        logger.info(p)
