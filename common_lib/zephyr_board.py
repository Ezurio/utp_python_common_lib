#
# This contains the base class for Zephyr boards and its simply subclasses.
#
from board import Board
from dvk_probe import DvkProbe
from python_uart import PythonUart
from lc_util import logger_setup, logger_get
from zephyr_uart import ZephyrUart
import time

logger = logger_get(__name__)


class ZephyrBoard(Board, DvkProbe, PythonUart, ZephyrUart):
    """
    A class to represent a generic Zephyr Board.
    """
    #: :meta hide-value:
    #:
    #: Amount of time to wait after resetting board.
    BOOT_TIME_SECONDS = 3

    @staticmethod
    def get_connected(allow_list=list()) -> list['ZephyrBoard']:
        """ Get a list of all connected boards.

        Returns:
            list['ZephyrBoard']: List of connected boards
        """
        boards = []
        for probe in DvkProbe.get_connected_probes():
            # todo filter on board name
            boards.append(ZephyrBoard(probe))
        return boards

    def __init__(self, probe: DvkProbe):
        super().__init__()
        DvkProbe.__init__(self, probe.id, probe.description, probe.ports)

    def open_and_init_board(self):
        self.open()
        ZephyrUart.__init__(self, self.ports['zephyr_shell'])
        PythonUart.__init__(self, self.ports['python'])
        self.reset_module()
        self._initialized = True

    def close_ports(self):
        self.zephyr_uart.close()
        self.python_uart.close()
        
    def reset_module(self):
        self.reset_probe()
        time.sleep(ZephyrBoard.BOOT_TIME_SECONDS)

    def soft_reset_module(self):
        """Soft reset the module by sending Ctrl-D to the Python REPL."""
        return self.python_uart.send(b'\x04', ZephyrBoard.BOOT_TIME_SECONDS)

class Nx040Board(ZephyrBoard):
    """
    A class to represent the NX040 DVK Board.

    Args:
        ZephyrBoard (Board): Zephyr Board base class
    """
    def __init__(self, probe):
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
