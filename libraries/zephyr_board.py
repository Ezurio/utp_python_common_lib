#
# This contains the base class for Zephyr boards and its simply subclasses.
#
from board import Board, BoardConfig
from dvk_probe import DvkProbe
from python_uart import PythonUart
from lc_util import logger_setup, logger_get
from zephyr_uart import ZephyrUart
import time

logger = logger_get(__name__)


class ZephyrBoard(Board):
    """
    A class to represent a generic Zephyr Board that has a DVK Probe.
    """
    #: :meta hide-value:
    #:
    #: Amount of time to wait after resetting board.
    BOOT_TIME_SECONDS = 3

    @classmethod
    def get_connected(cls, allow_list=list()) -> list['ZephyrBoard']:
        """ Get a list of all connected boards.

        Args:
            allow_list (list[str]): List of board names to allow.
            If empty, all boards with a DVK probe are allowed.

        Returns:
            list['ZephyrBoard']: List of connected boards
        """
        boards = []
        for probe in DvkProbe.get_connected_probes():
            # Accept any board that has a DVK probe (e.g., unprogrammed board)
            if len(allow_list) == 0:
                boards.append(ZephyrBoard(probe))
            else:  # Only accept boards that are in the allow list
                try:
                    # Read the board name from the settings
                    probe.open()
                    board_name = probe.read_settings().target_board_name.decode("utf-8")
                    logger.info(f"Found board {board_name}")
                    board_name = board_name.upper().replace(" ", "")
                    probe.close()
                    for subclass in cls.__subclasses__():
                        if any(subclass.__name__ in x for x in allow_list):
                            # The object names must match the board name
                            # (case insensitive and spaces removed) that is read from the settings
                            if subclass.matches_name(board_name):
                                boards.append(subclass(probe))
                                break
                except:
                    pass

        return boards

    #
    # These methods assume that the serial ports come from the probe.
    #

    def __init__(self, probe: DvkProbe):
        super().__init__()
        self.python_uart = PythonUart(probe.ports['python'])
        self.zephyr_uart = ZephyrUart(probe.ports['zephyr_shell'])
        self.__probe = DvkProbe(
            probe.id, probe.description, probe.ports, probe.family)

    @property
    def probe(self):
        return self.__probe

    def open_and_init_board(self):
        self.probe.open()
        self.reset_module()
        self.open_ports()
        self._initialized = True

    def open_ports(self):
        self.python_uart.wrapped_open()
        self.zephyr_uart.wrapped_open()

    def close_ports(self):
        self.zephyr_uart.close()
        self.python_uart.close()

    def reset_module(self):
        self.probe.reset_target()
        time.sleep(ZephyrBoard.BOOT_TIME_SECONDS)

    def soft_reset_module(self):
        """Soft reset the module by sending Ctrl-D to the Python REPL."""
        self.python_uart.send_raw(b'\x04')

    def close_ports_and_reset(self, reset_probe: bool = True):
        self.close_ports()
        if reset_probe:
            self.probe.reboot()
        self.probe.close()
        self._initialized = False


class SeraNX040Dvk(ZephyrBoard):
    """
    A class to represent the NX040 DVK Board.

    Args:
        ZephyrBoard (Board): Zephyr Board base class
    """

    def __init__(self, probe):
        probe.family = "nrf52833"
        super().__init__(probe)


if __name__ == "__main__":
    logger = logger_setup(__file__)

    boards = ZephyrBoard.get_connected()
    logger.info(f"Zephyr boards found: {len(boards)}")
    for b in boards:
        logger.info(b)
        logger.info(b.ports)
        b.open_and_init_board()
        logger.debug(dir(b))
