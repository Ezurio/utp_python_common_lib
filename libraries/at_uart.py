from CmdSerialPort import CmdSerialPort
from lc_util import logger_get

logger = logger_get(__name__)

class AtUart(object):
    """
    A class to represent the AT UART interface.
    """

    def __init__(
        self,
        port_name: str,
        rx_delimiter=b"\r",
        baud_rate=115200,
    ):
        """
        Create a CmdSerialPort instance and configure it for AT command use.
        """
        logger.debug(f"Init AT Uart {port_name}")
        self.__at_uart = None
        self.__port_name = port_name

        try:
            self.__at_uart = CmdSerialPort()
            self.__at_uart.set_rx_delimiter(rx_delimiter)
            self.__at_uart.open(self.__port_name, baud_rate)
            logger.info(f"Opened AT Uart {port_name}")
        except:
            self.__at_uart = None
            raise Exception("Unable to create and configure AT Uart")

    @property
    def at_uart(self):
        """AT UART Port Instance"""
        return self.__at_uart

    @property
    def at_port_name(self):
        """AT UART Port Name (i.e. COM10)"""
        return self.__port_name
