from CmdSerialPort import CmdSerialPort
import pyboard as pyboard
from lc_util import logger_get
import time

logger = logger_get(__name__)

class PythonUart(object):
    """
    A class to represent an embedded Python UART.
    """

    def __init__(
        self,
        port_name: str,
        rx_delimiter=b"\n>>> ",
        baud_rate=115200,
        wait_for_bytes_delay_seconds=0.005,
    ):
        """
        Create a CmdSerialPort instance and configure it for REPL use.
        """
        logger.debug(f"Init PythonUart {port_name}")
        self.__python_uart = None
        self.__python_raw_repl_uart = None
        self.__port_name = port_name
        self.__baud_rate = baud_rate
        self.__wait_for_bytes_delay_seconds = wait_for_bytes_delay_seconds

        try:
            self.__python_uart = CmdSerialPort()
            self.__python_uart.set_rx_delimiter(rx_delimiter)
            self.__python_uart.open(self.__port_name, self.__baud_rate)
            logger.info(f"Opened Python Uart {port_name}")
        except:
            self.__python_uart = None
            raise Exception("Unable to create and configure PythonUart")

    @property
    def python_uart(self):
        """Python Port Instance"""
        return self.__python_uart

    @property
    def python__port_name(self):
        """Python Port Name (i.e. COM9)"""
        return self.__port_name

    @property
    def python_raw_repl_uart(self) -> pyboard.Pyboard:
        """Python Raw REPL UART Instance"""
        return self.__python_raw_repl_uart

    def open_raw_repl_uart(self):
        self.__python_raw_repl_uart = pyboard.Pyboard(
            self.__port_name, self.__baud_rate
        )
        self.python_raw_repl_uart.enter_raw_repl(False)

    def close_raw_repl_uart(self):
        self.__python_raw_repl_uart.exit_raw_repl()
        # Wait for bytes to go out UART before closing
        time.sleep(self.__wait_for_bytes_delay_seconds)
        self.__python_raw_repl_uart.close()

    def open_repl_uart(self):
        self.python_uart.open(self.__port_name, self.__baud_rate)

    def close_repl_uart(self):
        self.python_uart.close()

    def upload_py_file(self, src: str, dst: str):
        """
        Upload a python file to the board file system using the raw REPL UART.

        Args:
            src (str): Path to file to upload
            dst (str): Destination path on board
        """
        self.python_raw_repl_uart.fs_put(src, dst)

    def quit_running_app(self):
        """Quit the running app on the board."""
        # ctrl-C twice: interrupt any running program
        self.python_uart.port.write(b"\r\x03\x03")
        time.sleep(self.__wait_for_bytes_delay_seconds)


