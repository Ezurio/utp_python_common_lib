from lc_util import logger_get

logger = logger_get(__name__)


class Board(object):
    """
    This is the base class for different boards.

    It contains methods for common functions and stubs for those that must
    be implemented by subclasses.
    """

    def __init__(self):
        self.__initialized = False

    def __del__(self):
        try:
            self.close_ports()
        except:
            pass

    @property
    def board_name(self):
        """
        Board names match the class name.
        """
        return self.__class__.__name__

    @property
    def is_initialized(self):
        return self.__initialized

    @property
    def _initialized(self):
        return self.__initialized

    @_initialized.setter
    def _initialized(self, v: bool):
        """
        Allow subclass to set flag after it has completed initialization.
        """
        self.__initialized = v

    @classmethod
    def get_connected(cls, allow_list=list()) -> list:
        """
        Look for all boards in the current scope.

        Args:
            allow_list: A list of class names that can be used to filter results. Any empty list allows all subclasses.
        
        Returns:
            list: List of connected boards
        """
        if type(allow_list) == str:
            raise ValueError("Allow list must be list not str")

        boards = list()
        for subclass in cls.__subclasses__():
            logger.debug(subclass.__name__)
            boards.extend(subclass.get_connected(allow_list))

        return boards

    @staticmethod
    def get_single():
        """
        Helper method to get a single board, or prompt user to select a board
        in the case of multiples.

        Returns:
            Board to connect to.
        """
        board = None
        boards = Board.get_connected()
        if len(boards) == 0:
            raise Exception(f"Error!  No Boards found.")

        choice = 0
        if len(boards) > 1:
            print("Which board do you want to use?")
            for i, board in enumerate(boards):
                print(f"{i}: {board}")
            choice = int(input("Enter the number of the board: "))
        if choice > (len(boards) - 1):
            raise Exception(f"Error!  Invalid Board Number.")

        return boards[choice]

    @staticmethod
    def get_by_com_port(com_port: str):
        """
        Get a board that uses the specified COM port.

        Returns:
            board or None if not found
        """
        for board in Board.get_connected():
            for _, port in board.ports.items():
                logger.debug(f"{_} {port}")
                try:
                    if port == com_port:
                        return board
                except:
                    pass

        return None

    def open_and_init_board(self):
        """
        Opens the probe, UARTs, and resets the module.
        The probe and UARTs can then be accessed via the class properties.
        \n
        One purpose of this function is to defer some operations until
        after board discovery. However, some boards may not be able to be
        identified without connecting to them.
        """
        raise NotImplementedError

    def close_ports(self):
        """
        Close all UARTs. Boards may have different UARTs.
        """
        raise NotImplementedError

    def close_ports_and_reset(self):
        """
        Close all UARTs and reset the probe and module.
        Note: Resetting the probe resets the IO and the module.
        """
        self.close_ports()
        self.reset_probe()
        self.close()

    def reset_module(self):
        """
        Reset the module using the debug probe.
        """
        raise NotImplementedError

    def soft_reset_module(self):
        """
        Send end-of-transmission character to the board using Python UART
        """
        raise NotImplementedError
