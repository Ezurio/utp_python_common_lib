from CmdSerialPort import CmdSerialPort
import platform
import pyboard as pyboard
from lc_util import logger_get
import time

logger = logger_get(__name__)

verbose_port_logging = False


class PythonUart(CmdSerialPort):
    """
    A class to represent an embedded Python UART.
    """

    def __init__(
        self,
        port_name: str,
        rx_delimiter=b"\n>>> ",
        baud_rate=115200,
        wait_for_bytes_delay_seconds=0.005
    ):
        """
        Create a CmdSerialPort instance and configure it for REPL use.
        """
        logger.debug(f"Init PythonUart {port_name}")
        super().__init__()
        self.__raw_repl = None
        self.__rs2xx_protocol = None
        self.__port_name = port_name
        self.__baud_rate = baud_rate
        self.__wait_for_bytes_delay_seconds = wait_for_bytes_delay_seconds
        # The RS2xx may be in a low power state and needs dummy characters to wake up
        self.__can_sleep = False
        self.__flush_count_sleep = 3
        self.__flush_delay = 0.5
        self.__delimiter_found_when_opened = False

        try:
            self.set_rx_delimiter(rx_delimiter)
        except:
            raise Exception("Unable to create and configure PythonUart")

    @property
    def port_name(self):
        """Python Port Name (i.e. COM9)"""
        return self.__port_name

    @property
    def can_sleep(self):
        return self.__can_sleep

    @can_sleep.setter
    def can_sleep(self, value):
        self.__can_sleep = value

    def wrapped_open(self, delay_after_open_seconds=0.1, flush_count=0, flush_delay=0.5):
        """Wrap the CmdSerialPort open method for debugging and error handling.

        Args:
            delay_after_open_seconds (float, optional): Delay after opening.
            Can be used to allow device to finish booting.

            flush_count (int, optional): Number of flushes (send '\r') to perform.
            This is done to try and ensure that the first command sent to the device
            is successful. Defaults to 0. If zero and the device can_sleep, then
            flush_count_sleep is used.

            flush_delay (float, optional): Delay between each flush. Defaults to 0.5.

        """
        try:
            self.open(self.__port_name, self.__baud_rate)
            if verbose_port_logging:
                logger.info(self.port)
            logger.debug(f"Opened Python Uart {self.__port_name}")
        except:
            raise RuntimeError(
                f"Unable to open Python Uart {self.__port_name}")

        time.sleep(delay_after_open_seconds)
        self.__delimiter_found_when_opened = False
        if flush_count > 0:
            self.__delimiter_found_when_opened = self.flush_rx(flush_count, flush_delay)
        elif self.__can_sleep:
            self.__delimiter_found_when_opened = self.flush_rx(
                self.__flush_count_sleep, self.__flush_count_delay)

    @property
    def delimiter_found_when_opened(self):
        return self.__delimiter_found_when_opened
    
    @property
    def rs2xx_protocol(self) -> pyboard.Pyboard:
        """RS2xx Protocol UART Instance"""
        return self.__rs2xx_protocol

    @property
    def raw_repl(self) -> pyboard.Pyboard:
        """Python Raw REPL UART Instance"""
        return self.__raw_repl

    def open_raw_repl_uart(self):
        self.__raw_repl = pyboard.Pyboard(
            self.__port_name, self.__baud_rate)

        self.raw_repl.enter_raw_repl(False)

    def close_raw_repl_uart(self):
        if self.raw_repl:
            if self.raw_repl.in_raw_repl:
                self.raw_repl.exit_raw_repl()
                # Wait for bytes to go out UART before closing
                time.sleep(self.__wait_for_bytes_delay_seconds)
            if self.raw_repl.serial and self.raw_repl.serial.is_open:
                self.raw_repl.close()

    def open_repl_uart(self):
        self.wrapped_open()

    def close_repl_uart(self):
        self.close()
        logger.debug(f"Closed Python Uart {self.port_name}")

    def quit_running_app(self):
        """Send ctrl-c twice: interrupt any running program"""
        self.send_raw(b"\r\x03\x03")
        time.sleep(self.__wait_for_bytes_delay_seconds)

    def rs2xx_repl_ready(self) -> bool:
        """ Unless app.wakeup() has been sent to the RS2xx, the UART may be shutdown. 
        This function will repeatedly send '\r' to the RS2xx to wake it up using
        flush_count_sleep and flush_delay.

        Returns:
            bool: True if '>>>' prompt is received, False otherwise.
        """
        return self.flush_rx(self.__flush_count_sleep, self.__flush_delay)

    def open_rs2xx_protocol_uart(self):
        """Enter RS2xx Protcol Mode"""
        raise NotImplementedError

    def close_rs2xx_protocol_uart(self):
        """Exit RS2xx Protocol Mode"""
        raise NotImplementedError

    def configure_sleep(self, flush_count: int, delay: float):
        """ Enable and configure wake up from sleep parameters """
        self.__can_sleep = True
        self.__flush_count_sleep = flush_count
        self.__flush_delay = delay
