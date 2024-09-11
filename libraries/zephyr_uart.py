from CmdSerialPort import CmdSerialPort
from lc_util import logger_get

logger = logger_get(__name__)

class ZephyrUart(CmdSerialPort):
    """
    A class to represent the Zephyr Shell UART.
    """

    def __init__(
        self,
        port_name: str,
        rx_delimiter=b"\nuart:~$ ",
        baud_rate=115200,
    ):
        """
        Create a CmdSerialPort instance and configure it for Zephyr Shell use.
        """
        logger.debug(f"Init ZephyrUart {port_name}")
        super().__init__()
        self.__port_name = port_name
        self.__baud_rate = baud_rate
        
        try:
            self.set_rx_delimiter(rx_delimiter)
        except:
            raise Exception("Unable to create and configure ZephyrUart")

    @property
    def port_name(self):
        """Zephyr UART Port Name (i.e. COM10)"""
        return self.__port_name

    def wrapped_open(self):
        """Wrap the CmdSerialPort open method"""
        try:
            self.open(self.__port_name, self.__baud_rate)
            logger.debug(f"Opened Zephyr Uart {self.__port_name}")
        except:
            raise RuntimeError(f"Unable to open Zephyr Uart {self.__port_name}")
