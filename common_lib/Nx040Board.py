import logging
import time
from common_lib.DvkProbe import DvkProbe
from common_lib.CmdSerialPort import CmdSerialPort

ERR_OK = 0
ERR_BOARD_NOT_FOUND = -1


class Nx040Board(DvkProbe):
    """A class to represent the NX040 DVK Board.

    Args:
        DvkProbe (Object): Inherit from DvkProbe.
    """

    BOOT_TIME_SECONDS = 2
    DEFAULT_BAUD_RATE = 115200
    PY_REPL_RX_DELIMITER = b'\n>>> '
    ZEPHYR_SHELL_RX_DELIMITER = b'\n\x1b[1;32muart:~$ '

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
            board.probe = probe
            if not probe.ports[0].location:
                logging.warning(
                    f'No COM port location found for board {probe.id}, assuming zephyr port {probe.ports[0].device}')

            board.zephyr_port_name = probe.ports[0].device
            board.python_port_name = probe.ports[1].device
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

    def open_and_init_board(self):
        """
        Opens the DvkProbe, and resets the Module.
        The DvkProbe can then be accessed via instance.probe.
        """
        # open dvk probe
        logging.info(f"Opening Dvk Probe ID {self.probe.id}")
        self.probe.open(self.probe.id)
        if (not self.probe.is_open):
            raise Exception(
                f"Unable to open Dvk Probe at {self.probe.id}")

        # open python UART
        self.python_uart = CmdSerialPort()
        self.python_uart.set_rx_delimiter(Nx040Board.PY_REPL_RX_DELIMITER)
        self.python_uart.open(self.python_port_name,
                              Nx040Board.DEFAULT_BAUD_RATE)

        # open Zephyr UART
        self.zephyr_uart = CmdSerialPort()
        self.zephyr_uart.set_rx_delimiter(Nx040Board.ZEPHYR_SHELL_RX_DELIMITER)
        self.zephyr_uart.open(self.zephyr_port_name,
                              Nx040Board.DEFAULT_BAUD_RATE)

        # reset the module
        self.probe.reset_device()

        time.sleep(Nx040Board.BOOT_TIME_SECONDS)

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

    def __init__(self):
        self._probe = super().__init__()
        self._zephyr_port_name = ""
        self._python_port_name = ""
        self._zephyr_uart = ""
        self._python_uart = ""

    @property
    def probe(self):
        """Pico Probe / Dvk Probe"""
        return self._probe

    @probe.setter
    def probe(self, p: DvkProbe):
        self._probe = p

    @property
    def zephyr_port_name(self):
        """Zephyr UART Port Name (i.e. COM10)"""
        return self._zephyr_port_name

    @zephyr_port_name.setter
    def zephyr_port_name(self, p: str):
        self._zephyr_port_name = p

    @property
    def python_port_name(self):
        """Python Port Name (i.e. COM10)"""
        return self._python_port_name

    @python_port_name.setter
    def python_port_name(self, p: str):
        self._python_port_name = p

    @property
    def zephyr_uart(self):
        """Zephyr UART Port Instance"""
        return self._zephyr_uart

    @zephyr_uart.setter
    def zephyr_uart(self, u: CmdSerialPort):
        self._zephyr_uart = u

    @property
    def python_uart(self):
        """Python Port Instance"""
        return self._python_uart

    @python_uart.setter
    def python_uart(self, u: CmdSerialPort):
        self._python_uart = u
