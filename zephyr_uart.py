from CmdSerialPort import CmdSerialPort
from lc_util import logger_get

logger = logger_get(__name__)

class ZephyrUart(object):
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
        self.__zephyr_uart = None
        self.__port_name = port_name

        try:
            self.__zephyr_uart = CmdSerialPort()
            self.__zephyr_uart.set_rx_delimiter(rx_delimiter)
            self.__zephyr_uart.open(self.__port_name, baud_rate)
            logger.info(f"Opened Zephyr Uart {port_name}")
        except:
            self.__zephyr_uart = None
            raise Exception("Unable to create and configure ZephyrUart")

    @property
    def zephyr_uart(self):
        """Zephyr UART Port Instance"""
        return self.__zephyr_uart

    @property
    def zephyr_port_name(self):
        """Zephyr UART Port Name (i.e. COM10)"""
        return self.__port_name
