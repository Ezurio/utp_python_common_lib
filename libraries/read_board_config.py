import yaml
import logging
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
from board import GenericBoard


def read_board_config(board_config_file="board_config.yml"):
    """Read a board configuration file and return a list of GenericBoard objects.

    Args:
        board_config_file (str, optional): A board config file that
        list board hardware configurations. Defaults to "board_config.yml".

    Returns:
        list[GenericBoard]: list of boards
    """

    boards = list[GenericBoard]()

    try:
        with open(board_config_file, 'r') as stream:
            dictionary = yaml.load(stream, Loader)
            for b in dictionary['boards']:
                boards.append(GenericBoard(b))
    except FileNotFoundError:
        logging.warn(f"No {board_config_file} file found")
    except Exception as e:
        print(e)
        raise e

    return boards
