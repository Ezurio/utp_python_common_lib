import serial
import threading
import logging


class SerialPort():
    """Base serial port implementation.
    Receives bytes from the serial port and places them in a queue.
    The queue is cleared after if the bytes remain in the queue for
    _clear_queue_timeout_sec amount of time.
    """
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    CLEAR_QUEUE_TIMEOUT_DEFAULT = 5

    def __init__(self):
        self._port = None
        self._rx_queue = []
        self._stop_threads = False
        self._clear_queue_timeout_sec = SerialPort.CLEAR_QUEUE_TIMEOUT_DEFAULT
        self._queue_monitor_event = threading.Event()
        self._bytes_received = threading.Event()
        self._monitor_rx_queue = False

    def __queue_monitor_timer_expired(self):
        self._queue_monitor_event.set()

    def __queue_monitor(self):
        while not self._stop_threads:
            self._queue_monitor_event.wait()
            self._queue_monitor_event.clear()
            size = len(self._rx_queue)
            if size > 0:
                logging.debug(f'Clear RX queue ({size})')
                self.clear_rx_queue()

    def __pause_queue_monitor(self):
        self._monitor_rx_queue = False
        self._queue_monitor_timer.cancel()

    def __resume_queue_monitor(self):
        self._monitor_rx_queue = True
        self._queue_monitor_timer = threading.Timer(
            self._clear_queue_timeout_sec, self.__queue_monitor_timer_expired)
        self._queue_monitor_timer.start()

    def __serial_port_rx_thread(self):
        while not self._stop_threads:
            try:
                bytes = self._port.read(1)
                for byte in bytes:
                    self._rx_queue.append(byte)
                    # logging.debug(
                    #     f'[{self._port.name}] RX: {hex(byte)} ({len(self._rx_queue)})')
                    self._bytes_received.set()
                    if self._monitor_rx_queue and not self._queue_monitor_timer.is_alive():
                        self.__resume_queue_monitor()
            except:
                pass

    def set_queue_timeout(self, timeout_sec: float):
        """Set the RX byte queue cleanup timeout

        Args:
            timeout_sec (float): Time in seconds
        """
        self._clear_queue_timeout_sec = timeout_sec

    def open(self, portName: str, baud: int, rtsCts: bool = False):
        """Open the serial port and start processing threads

        Args:
            portName (str): COM port name or device
            baud (int): baud rate
            rtsCts (bool, optional): Enable RTS/CTS flow control. Defaults to False.
        """
        if self._port and self._port.is_open:
            return

        self._port = serial.Serial(portName, baud, rtscts=rtsCts)
        self._port.timeout = None
        self._port.reset_input_buffer()
        self._port.reset_output_buffer()
        self.clear_rx_queue()
        self.signal_bytes_received()
        self._stop_threads = False
        self.__resume_queue_monitor()
        # The serial port RX thread reads all bytes received and places them in a queue
        threading.Thread(target=self.__serial_port_rx_thread,
                         daemon=True).start()
        # The queue monitor thread clears stray RX bytes if they are not processed for
        # clear_queue_timeout_sec amount of time
        threading.Thread(target=self.__queue_monitor, daemon=True).start()

    def clear_rx_queue(self):
        """Clear all received bytes from the queue
        """
        self._rx_queue.clear()

    def send(self, data: bytes):
        """Send bytes out the serial port

        Args:
            data (bytes): data to send
        """
        self.__pause_queue_monitor()
        if isinstance(data, str):
            data = bytes(data, 'utf-8')
        logging.debug(f'[{self._port.name}] TX: {data}')
        self._port.write(data)
        self.__resume_queue_monitor()

    def close(self):
        """Close the serial port and stop all threads
        """
        self._stop_threads = True
        self.__pause_queue_monitor()
        self._queue_monitor_event.set()
        self._bytes_received.set()
        if self._port and self._port.is_open:
            self._port.close()
            logging.debug(f'closed {self._port.name}')
        self.clear_rx_queue()

    def get_rx_queue(self):
        return self._rx_queue

    def is_queue_empty(self):
        if len(self._rx_queue) > 0:
            return False
        else:
            True

    def wait_for_bytes_received(self, timeout_sec: float = None):
        """Wait for bytes to be received on the serial port

        Args:
            timeout_sec (float, optional): Time in seconds to wait. Defaults to None.

        Returns:
            _type_: True if signaled, False if timed out
        """
        return self._bytes_received.wait(timeout_sec)

    def signal_bytes_received(self):
        """Signal that bytes have been received
        """
        self._bytes_received.clear()

    @property
    def port(self):
        """Serial port object"""
        return self._port
