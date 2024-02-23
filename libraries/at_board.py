#
# This contains the base class for AT boards and its simple subclasses.
#
from board import Board, GenericBoard
from jlink_probe import JLinkProbe
from at_uart import AtUart
from lc_util import logger_setup, logger_get
import time

logger = logger_get(__name__)


class AtBoard(Board, JLinkProbe, AtUart):
    """
    This is the base class for AT Boards.
    """
    #: Amount of time to wait after resetting board.
    BOOT_TIME_SECONDS = 3

    def __init__(self, probe: JLinkProbe):
        super().__init__()
        print(f"debug probe ports ID: {probe.ports}")
        JLinkProbe.__init__(self, probe.id, probe.family,
                            probe.description, probe.ports)


    def open_and_init_board(self):
        self.open()
        AtUart.__init__(self, self.ports['at'])
        self._initialized = True
        self.at_uart.consume_echo(False)


    @classmethod
    def get_connected(cls, allow_list=list(), boards_conf: list[GenericBoard] = list()) -> list['AtBoard']:
        """
        Get a list of all connected AT boards.

        Args:
            allow_list (list[str]): List of board names to allow.
            If empty, all boards with a J-Link probes are considered.

            boards_conf (list[GenericBoard]): List of board configs to search for and create.

        Returns:
            list['AtBoard']: List of connected AT boards
        """
        if type(allow_list) == str:
            raise ValueError("Allow list must be list not str")

        boards = list()
        # Only return boards with a J-Link probe if they are in the board config list
        for boards_conf in boards_conf:
            # AT interfaces only have a single port
            if len(boards_conf.ports) == 1:
                # Indicate to the JLinkProbe class that we are looking for AT boards probes
                for p in JLinkProbe.get_connected_probes(boards_conf.probe.family, "at"):
                    # Ensure that this single port is of AT type and it serial number matches the probe
                    if p.id == boards_conf.probe.sn and boards_conf.ports[0].type == 'at':
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


