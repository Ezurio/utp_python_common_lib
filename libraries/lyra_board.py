#
# This contains the base class for Lyra boards and its simple subclasses.
#
from board import Board, BoardConfig
from jlink_probe import JLinkProbe
from python_uart import PythonUart
from lc_util import logger_setup, logger_get
import time

logger = logger_get(__name__)


class LyraBoard(Board, JLinkProbe, PythonUart):
    """
    This is the base class for Lyra Boards.
    """
    #: The family is used by the debug probe so that it knows the base kind of
    #: device it is communicating with.
    FAMILY = "Cortex-M33"
    #: The manufacturer name is used to qualify the debug probe as possibly
    #: being connected to a Lyra module.
    MANUFACTURER = "EnergyMicro"
    #: :meta hide-value:
    #:
    #: The part number address is read to obtain a part number string.
    #: It must be defined by the subclass.
    MODULE_PART_NUMBER_ADDR = 0
    #: :meta hide-value:
    #:
    #: A string representation of the module's part number.
    #: It must be defined by the subclass.
    MODULE_PART_NUMBER = ""
    #: Amount of time to wait after resetting board.
    BOOT_TIME_SECONDS = 3

    def __init__(self, probe: JLinkProbe):
        super().__init__()
        JLinkProbe.__init__(self, probe.id, probe.description,
                            probe.ports, probe.family)

        if self.MODULE_PART_NUMBER == "":
            raise NotImplementedError("Subclass must define part number")

    def __str__(self):
        return super().__str__() + f", {self.MODULE_PART_NUMBER}"

    @property
    def module(self):
        """
        Part number string assigned by Silicon Labs.
        """
        return self.MODULE_PART_NUMBER

    def open_and_init_board(self):
        self.open()
        PythonUart.__init__(self, self.ports['python'])
        self.reset_module()
        self._initialized = True

    @staticmethod
    def read_part_number(probe: JLinkProbe, address, max_name_length=26) -> str:
        """
        Read Device Information memory (ASCII) and convert result into a string.

        Args:
            probe (JLinkProbe): JLinkProbe object
            address (int): Address to read
            max_name_length (int): Maximum length of string to read

        Returns:
            str: Part number string
        """
        s = str()
        try:
            s = JLinkProbe.memory_read_as_string(
                probe, address, max_name_length)
            logger.debug(f"Part number: {s}")
        except:
            logger.error("Couldn't read part number")

        return s

    @classmethod
    def get_connected(cls, allow_list=list()) -> list['LyraBoard']:
        """
        Get a list of all connected boards.

        Args:
            allow_list (list[str]): List of board names to allow.
            If empty, all boards with a J-Link probe are allowed.

        Returns:
            list['LyraBoard']: List of connected boards
        """
        if type(allow_list) == str:
            raise ValueError("Allow list must be list not str")

        boards = list()
        for p in JLinkProbe.get_connected_probes(LyraBoard.FAMILY):
            for subclass in cls.__subclasses__():
                if len(allow_list) == 0 or any(subclass.__name__ in x for x in allow_list):
                    if subclass.MANUFACTURER in p.description:
                        dev_info = LyraBoard.read_part_number(
                            p, subclass.MODULE_PART_NUMBER_ADDR)
                        # If the part number matches, then
                        # create an instance of that type.
                        if subclass.MODULE_PART_NUMBER in dev_info:
                            b = subclass(p)
                            boards.append(b)
                            break
                        else:
                            logger.debug(
                                f"{subclass.MODULE_PART_NUMBER} not in {dev_info}")

        return boards

    def close_ports(self):
        self.python_uart.close()

    def reset_module(self):
        self.reset_target()
        time.sleep(LyraBoard.BOOT_TIME_SECONDS)

    def soft_reset_module(self):
        return self.python_uart.send(b'\x04', LyraBoard.BOOT_TIME_SECONDS)

    def close_ports_and_reset(self, reset_probe: bool = True):
        self.close_ports()
        self.reset_module()
        self.close()
        self._initialized = False
#
# Subclasses are a Python compatible name of the board
#


class Lyra24P_10dBm(LyraBoard):
    """
    Lyra24P module with 10 dBm output.
    """
    #:
    MODULE_PART_NUMBER = "BGM240PB22VNA"
    #:
    MODULE_PART_NUMBER_ADDR = 0x0FE08130

    def __init__(self, probe):
        super().__init__(probe)


class Lyra24P_20dBm(LyraBoard):
    """
    Lyra24P module with 20 dBm output.
    """
    #:
    MODULE_PART_NUMBER = "BGM240PB32VNA"
    #:
    MODULE_PART_NUMBER_ADDR = 0x0FE08130

    def __init__(self, probe):
        super().__init__(probe)


class Lyra24P_20dBm_RF(LyraBoard):
    """
    Lyra24P module with 20 dBm output and rf pin.
    """
    #:
    MODULE_PART_NUMBER = "BGM240PB32VNN"
    #:
    MODULE_PART_NUMBER_ADDR = 0x0FE08130

    def __init__(self, probe):
        super().__init__(probe)


class Lyra24S_10dBm(LyraBoard):
    """
    Lyra24S module with 10 dBm output.
    """
    #:
    MODULE_PART_NUMBER = "BGM240SB22VNA"
    #:
    MODULE_PART_NUMBER_ADDR = 0x0FE08130

    def __init__(self, probe):
        super().__init__(probe)


if __name__ == "__main__":
    logger = logger_setup(__file__)

    boards = LyraBoard.get_connected()
    logger.info(f"Lyra boards found: {len(boards)}")
    for b in boards:
        logger.debug(dir(b))
        logger.info(b)
        b.open_and_init_board()
        logger.debug(dir(b))
