import logging
import time
from common_lib.DvkProbe import DvkProbe
from common_lib.CmdSerialPort import CmdSerialPort
import common_lib.pyboard as pyboard

ERR_OK = 0
ERR_BOARD_NOT_FOUND = -1


class Nx040Board(DvkProbe):
    """A class to represent the NX040 DVK Board.

    Args:
        DvkProbe (Object): Inherit from DvkProbe.
    """

    BOOT_TIME_SECONDS = 3
    DEFAULT_BAUD_RATE = 115200
    PY_REPL_RX_DELIMITER = b'\n>>> '
    ZEPHYR_SHELL_RX_DELIMITER = b'\nuart:~$ '
    WAIT_FOR_BYTES_DELAY_SEC = 0.005

    @staticmethod
    def get_board():
        """Helper method to get a single board, or prompt user to select a board
        in the case of multiples.

        Returns:
        Board to connect to.
        """
        board = None
        boards = Nx040Board.get_connected_boards()
        if len(boards) == 0:
            raise Exception(
                f"Error!  No Boards found.")

        choice = 0
        if len(boards) > 1:
            print("Which board do you want to use?")
            for i, board in enumerate(boards):
                print(f"{i}: {board.probe.id}")
            choice = int(input("Enter the number of the board: "))
        if choice > (len(boards) - 1):
            raise Exception(
                f"Error!  Invalid Board Number.")

        return boards[choice]

    @staticmethod
    def get_connected_boards() -> list['Nx040Board']:
        """Get a list of all connected boards.

        Returns:
            List: List of boards
        """
        boards = []
        for probe in DvkProbe.get_connected_probes():
            board = Nx040Board()
            board._probe = probe
            if not probe.ports[0].location:
                logging.warning(
                    f'No COM port location found for board {probe.id}, assuming zephyr port {probe.ports[0].device}')

            board._zephyr_port_name = probe.ports[0].device
            board._python_port_name = probe.ports[1].device
            boards.append(board)
        return boards

    @staticmethod
    def get_board_by_com_port(com_port: str):
        """Get a board that uses the specified COM port.

        Returns:
            Nx040Board: board or None if not found
        """
        for board in Nx040Board.get_connected_boards():
            if board.zephyr_port_name == com_port or board.python_port_name == com_port:
                return board
        return None

    def __init__(self):
        self._probe = super().__init__()
        self._zephyr_port_name = ""
        self._python_port_name = ""
        self._zephyr_uart = None
        self._python_uart = None
        self._python_raw_repl_uart = None
        self._is_initialized = False

    def open_and_init_board(self):
        """
        Opens the DvkProbe, UARTs, and resets the Module.
        The DvkProbe and UARTs can then be accessed via the class properties.
        """
        # open dvk probe
        logging.info(f"Opening Dvk Probe ID {self.probe.id}")
        self.probe.open(self.probe.id)
        if (not self.probe.is_open):
            raise Exception(
                f"Unable to open Dvk Probe at {self.probe.id}")

        # open python UART
        self._python_uart = CmdSerialPort()
        self.python_uart.set_rx_delimiter(Nx040Board.PY_REPL_RX_DELIMITER)
        self.python_uart.open(self.python_port_name,
                              Nx040Board.DEFAULT_BAUD_RATE)

        # open Zephyr UART
        self._zephyr_uart = CmdSerialPort()
        self.zephyr_uart.set_rx_delimiter(Nx040Board.ZEPHYR_SHELL_RX_DELIMITER)
        self.zephyr_uart.open(self.zephyr_port_name,
                              Nx040Board.DEFAULT_BAUD_RATE)

        # reset the module
        self.reset_module()
        self._is_initialized = True

    def close_ports_and_reset(self):
        """
        Close all UARTs and reset the probe and module
        Note:  Resetting the probe resets the IO and the module.
        """
        if self.python_uart:
            self.python_uart.close()
        if self.zephyr_uart:
            self.zephyr_uart.close()
        if self.probe:
            self.probe.reboot()
            self.probe.close()

    @property
    def probe(self):
        """Pico Probe / Dvk Probe"""
        return self._probe

    @property
    def zephyr_port_name(self):
        """Zephyr UART Port Name (i.e. COM10)"""
        return self._zephyr_port_name

    @property
    def python_port_name(self):
        """Python Port Name (i.e. COM10)"""
        return self._python_port_name

    @property
    def zephyr_uart(self):
        """Zephyr UART Port Instance"""
        return self._zephyr_uart

    @property
    def python_uart(self):
        """Python Port Instance"""
        return self._python_uart

    @property
    def is_initialized(self):
        return self._is_initialized

    @property
    def python_raw_repl_uart(self) -> pyboard.Pyboard:
        """Python Raw REPL UART Instance"""
        return self._python_raw_repl_uart

    def open_raw_repl_uart(self):
        self._python_raw_repl_uart = pyboard.Pyboard(
            self.python_port_name, Nx040Board.DEFAULT_BAUD_RATE)
        self.python_raw_repl_uart.enter_raw_repl(False)

    def close_raw_repl_uart(self):
        self.python_raw_repl_uart.exit_raw_repl()
        # Wait for bytes to go out UART before closing
        time.sleep(Nx040Board.WAIT_FOR_BYTES_DELAY_SEC)
        self.python_raw_repl_uart.close()

    def open_repl_uart(self):
        self.python_uart.open(self.python_port_name,
                              Nx040Board.DEFAULT_BAUD_RATE)

    def close_repl_uart(self):
        self.python_uart.close()

    def upload_py_file(self, src: str, dst: str):
        """Upload a python file to the board file system using the raw REPL UART.

        Args:
            src (str): Path to file to upload
            dst (str): Destination path on board
        """
        self.python_raw_repl_uart.fs_put(src, dst)

    def quit_running_app(self):
        """Quit the running app on the board."""
        # ctrl-C twice: interrupt any running program
        self.python_uart.port.write(b"\r\x03\x03")
        time.sleep(Nx040Board.WAIT_FOR_BYTES_DELAY_SEC)

    def reset_module(self):
        """Reset the module."""
        self.probe.reset_device()
        time.sleep(Nx040Board.BOOT_TIME_SECONDS)
