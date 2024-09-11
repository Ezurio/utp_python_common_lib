#
# This contains the base class for AT boards and its simple subclasses.
#
from board import Board, BoardConfig
from jlink_probe import JLinkProbe
from at_uart import AtUart
from lc_util import logger_setup, logger_get
import time

logger = logger_get(__name__)


class AtBoard(Board):
    """
    This is the base class for AT Boards.
    """
    #: Amount of time to wait after resetting board.
    BOOT_TIME_SECONDS = 3

    def __init__(self, probe: JLinkProbe):
        super().__init__()
        print(f"debug probe ports ID: {probe.ports}")
        self.probe = JLinkProbe(probe.id, probe.description,
                                probe.ports, probe.family)
        self.at_uart = AtUart(probe.ports['at'])

    def open_and_init_board(self):
        self.probe.open()
        self.at_uart.open()
        self._initialized = True
        self.at_uart.consume_echo(False)

    @classmethod
    def get_specified(cls, boards_conf: list[BoardConfig]) -> list['AtBoard']:
        """
        Get a list of all connected AT boards.

        Args:
            boards_conf (list[BoardConfig]): List of board configs to search for and create.

        Returns:
            list['AtBoard']: List of connected AT boards
        """
        boards = list()
        # Only return boards with a J-Link probe if they are in the board config list
        for boards_conf in boards_conf:
            # Ensure that this single port is of AT type and it serial number matches the probe
            if len(boards_conf.ports) == 1 and boards_conf.ports[0].type == 'at':
                probes = JLinkProbe.get_connected_probes(
                    family=boards_conf.probe.family, uart_interface_type="at")
                for p in probes:
                    if p.id == boards_conf.probe.sn:
                        boards.append(AtBoard(p))
                        break
        return boards

    def close_ports(self):
        self.at_uart.close()


if __name__ == "__main__":
    logger = logger_setup(__file__)

    boards = AtBoard.get_connected()
    logger.info(f"AT boards found: {len(boards)}")
    for b in boards:
        logger.debug(dir(b))
        logger.info(b)
        b.open_and_init_board()
        logger.debug(dir(b))
