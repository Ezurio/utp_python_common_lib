from board import Board
from lc_util import logger_setup
# Class method requires boards to be in scope
from lyra_board import LyraBoard
from zephyr_board import ZephyrBoard
from micro_python_board import MicroPythonBoard, BL654UsbDongle

def get_connected_boards(allow_list=list(), boards_conf=list()):
    return Board.get_connected(allow_list, boards_conf)

