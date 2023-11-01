import threading
import logging

from common_lib.SerialPort import SerialPort


class CmdSerialPort(SerialPort):
    """Command serial port implementation sends command strings with a delimiter.
    Command responses are processed with a separate delimiter and placed in a queue.

    Args:
        SerialPort (object): Inherit from SerialPort
    """
    DEFAULT_DELIMITER = b'\r'

    def __init__(self):
        super().__init__()
        self._cmd_received_event = threading.Event()
        self._stop_cmd_threads = False
        self._temp_cmd = []
        self._cmd_rx_queue = []
        self._tx_delimiter = CmdSerialPort.DEFAULT_DELIMITER
        self._rx_delimiter = CmdSerialPort.DEFAULT_DELIMITER
        self._consume_echo = True
        self._clear_cmd_queue_timeout_sec = SerialPort.CLEAR_QUEUE_TIMEOUT_DEFAULT
        self._cmd_queue_monitor_event = threading.Event()
        self._monitor_cmd_rx_queue = False

    def __cmd_rx_thread(self):
        while not self._stop_cmd_threads:
            try:
                if self.wait_for_bytes_received():
                    rx_bytes = self.get_rx_queue()
                    while len(rx_bytes) > 0:
                        byte = rx_bytes.pop(0)
                        self._temp_cmd.append(byte)
                        d_len = len(self._rx_delimiter)
                        # If the delimiter is found, process the response
                        if (len(self._temp_cmd) >= d_len) and (bytes(self._temp_cmd[-d_len::]) == self._rx_delimiter):
                            cmd = bytes(self._temp_cmd).decode(
                                'utf-8', 'ignore')
                            # Remove the delimiter from the response
                            cmd = cmd.replace(
                                self._rx_delimiter.decode('utf8'), '')
                            # Remove any leading or trailing whitespace
                            cmd = cmd.strip()
                            logging.debug(
                                f'[{self._port.name}] CMD RX: {cmd}')
                            self._cmd_rx_queue.append(cmd)
                            self._temp_cmd = []
                            self._cmd_received_event.set()
                            if self._monitor_cmd_rx_queue and not self._cmd_queue_monitor_timer.is_alive():
                                self.__resume_cmd_queue_monitor()
                    self.signal_bytes_received()
            except:
                pass

    def __cmd_queue_monitor_timer_expired(self):
        self._cmd_queue_monitor_event.set()

    def __cmd_queue_monitor(self):
        while not self._stop_cmd_threads:
            self._cmd_queue_monitor_event.wait()
            self._cmd_queue_monitor_event.clear()
            size = len(self._cmd_rx_queue)
            if size > 0:
                self.clear_cmd_rx_queue()

    def __pause_cmd_queue_monitor(self):
        self._monitor_cmd_rx_queue = False
        self._cmd_queue_monitor_timer.cancel()

    def __resume_cmd_queue_monitor(self):
        self._monitor_cmd_rx_queue = True
        self._cmd_queue_monitor_timer = threading.Timer(
            self._clear_cmd_queue_timeout_sec, self.__cmd_queue_monitor_timer_expired)
        self._cmd_queue_monitor_timer.daemon = True
        self._cmd_queue_monitor_timer.start()

    def open(self, portName: str, baud: int, rtsCts: bool = False):
        """Open the serial port and start processing threads

        Args:
            portName (str): COM port name or device
            baud (int): baud rate
            rtsCts (bool, optional): Enable RTS/CTS flow control. Defaults to False.
        """
        super().open(portName, baud, rtsCts)
        self._stop_cmd_threads = False
        self.clear_cmd_rx_queue()
        self._temp_cmd = []
        self.__resume_cmd_queue_monitor()
        # The cmd RX thread packages bytes received into response and places them in a queue
        threading.Thread(target=self.__cmd_rx_thread,
                         daemon=True).start()
        # The queue monitor thread clears stray responses if they are not processed for
        # _clear_cmd_queue_timeout_sec amount of time
        threading.Thread(target=self.__cmd_queue_monitor, daemon=True).start()

    def close(self):
        """Close the serial port and stop all threads
        """
        self._stop_cmd_threads = True
        self.__pause_cmd_queue_monitor()
        self._cmd_queue_monitor_event.set()
        super().close()

    def send(self, msg: str, timeout: float = 1.0, clear_queue: bool = True) -> str:
        """Send a command out the serial port and wait for a response

        Args:
            msg (str): Command string
            timeout (float, optional): Time to wait for a response in seconds. Defaults to 1.0.
            clear_queue (bool, optional): Clear the receive queue before sending the command. Defaults to True.

        Returns:
            string: Response string received
        """
        resp = None
        consume_echo = self._consume_echo
        if clear_queue:
            self.clear_cmd_rx_queue()

        self.__pause_cmd_queue_monitor()
        self._cmd_received_event.clear()
        if isinstance(msg, str):
            tx = bytes(msg, 'utf-8')
        elif isinstance(msg, bytes):
            tx = msg
            consume_echo = False
        else:
            raise Exception(
                f'[{self._port.name}] Invalid message type [{type(msg)}]')
        super().send(b''.join([tx, self._tx_delimiter]))
        if self._cmd_received_event.wait(timeout):
            resp = self._cmd_rx_queue.pop()
            if consume_echo:
                if msg not in resp:
                    self.__resume_cmd_queue_monitor()
                    raise Exception(
                        f'Echo mismatch. Expected: [{msg}], Received: [{resp}]')
                else:
                    resp = resp.replace(msg, '').strip()
        else:
            self.__resume_cmd_queue_monitor()
            raise Exception(
                f'[{self._port.name}] No response to command [{msg}]: [{bytes(self._temp_cmd)}]')

        self.__resume_cmd_queue_monitor()
        return resp

    def set_tx_delimiter(self, delimiter: bytes):
        """Set byte string that is used to delimit send commands

        Args:
            delimiter (bytes): the delimiter
        """
        self._tx_delimiter = delimiter

    def set_rx_delimiter(self, delimiter: bytes):
        """Set byte string that is used to delimit received commands

        Args:
            delimiter (bytes): the delimiter
        """
        self._rx_delimiter = delimiter

    def clear_cmd_rx_queue(self):
        """Clear all received responses from the queue
        """
        logging.debug(
            f'[{self._port.name}] Clear CMD RX queue ({len(self._cmd_rx_queue)})')
        self._cmd_rx_queue = []
        self._temp_cmd = []

    def consume_echo(self, consume: bool):
        """Enable/disable consuming echo from the response

        Args:
            consume (bool): True to consume echo, False to ignore echo
        """
        self._consume_echo = consume

    def read(self) -> bytes:
        """Read bytes from the serial port

        Returns:
            bytes: bytes read from the serial port
        """
        self.__pause_cmd_queue_monitor()
        num_bytes = len(self._temp_cmd)
        rx = bytes(self._temp_cmd[:num_bytes])
        del self._temp_cmd[:num_bytes]
        self.__resume_cmd_queue_monitor()

        return rx

    def wait_for_response(self, timeout: float = 1.0) -> str | None:
        """Wait for a response to be received

        Args:
            timeout (float, optional): Time to wait for a response in seconds. Defaults to 1.0.

        Returns:
            str: None if no response received, otherwise the response string
        """
        self.__pause_cmd_queue_monitor()
        self._cmd_received_event.clear()

        if len(self._cmd_rx_queue) > 0:
            resp = self._cmd_rx_queue.pop()
        elif self._cmd_received_event.wait(timeout):
            resp = self._cmd_rx_queue.pop()
        else:
            resp = None
        self.__resume_cmd_queue_monitor()

        return resp
