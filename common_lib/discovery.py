from board import Board
from lc_util import logger_setup
# Class method requires boards to be in scope
from lyra_board import LyraBoard
from zephyr_board import ZephyrBoard

def get_connected_boards(allow_list=list()):
    return Board.get_connected(allow_list)

