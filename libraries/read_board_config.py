import yaml
import logging
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
from board import BoardConfig, Properties

DEFAULT_CONFIG_FILE = "board_config.yml"


class InvalidPropertyError(Exception):
    pass


class ContinueOuterLoop(Exception):
    pass


class MatchNotFound(Exception):
    pass


def valid_properties(properties: list) -> bool:
    """Check if a list of properties is valid.

    Args:
        properties (list): list of properties

    Returns:
        bool: True if valid
    """
    if not properties:
        return True

    try:
        for p in properties:
            if isinstance(p, str):
                if not hasattr(Properties, p):
                    raise InvalidPropertyError(f"Invalid property: {p}")
            elif isinstance(p, list):
                for x in p:
                    if not hasattr(Properties, x):
                        raise InvalidPropertyError(f"Invalid property: {x}")
            else:
                raise InvalidPropertyError(
                    f"Invalid property type {type(p)} for {p}")

        return True

    except InvalidPropertyError:
        return False


def read_board_config(board_config_file=DEFAULT_CONFIG_FILE, desired_properties: list = None):
    """Read a board configuration file and return a list of BoardConfig objects.

    Args:
        board_config_file (str, optional): A board config file that
        list board hardware configurations. Defaults to "board_config.yml".

        desired_properties (list, optional): A list of properties 
        that boards must have to be included in output. Defaults to None. 
        Properties are case insensitive.
        Can be a list of lists when a board must have all properties in a sublist.
        If desired properties is a lists of lists, then the order of the output list
        will match the order of the input list.
    Returns:
        list[BoardConfig]: list of boards
    """

    boards = list[BoardConfig]()

    # If Robot framework passes and empty string, then use the default file name
    if not board_config_file:
        board_config_file = DEFAULT_CONFIG_FILE

    # Single board tests provide a list.
    # Multi-board tests provovide a lists of lists.
    # Convert all properties to upper case. Output is a list of lists.
    if desired_properties:
        new_list = list()
        if all(isinstance(i, list) for i in desired_properties):
            for sublist in desired_properties:
                if isinstance(sublist, list):
                    sublist = [item.upper() for item in sublist]
                    new_list.append(sublist)
        elif not all(isinstance(i, list) for i in desired_properties):
            sub = list()
            for p in desired_properties:
                sub.append(p.upper())
            new_list.append(sub)
        else:
            raise RuntimeError("Invalid desired properties format")

        desired_properties = new_list
        valid_properties(desired_properties)
        logging.debug(f"Desired properties: {desired_properties}")

    try:
        with open(board_config_file, 'r') as stream:
            dictionary = yaml.load(stream, Loader)
            board_configurations = dictionary['boards']
            if not desired_properties:
                return [BoardConfig(b) for b in board_configurations]

            
            # Find a board with all desired properties, the order of the input list matters.
            for sublist in desired_properties:
                for b in board_configurations:
                    properties = b['properties']
                    if properties:
                        properties = [item.upper() for item in properties]
                        valid_properties(properties)
                        logging.debug(f"actual properties: {properties}")
                        if all(x in properties for x in sublist):
                            logging.info(
                                f"Board {b['name']} has all desired properties")
                            boards.append(BoardConfig(b))
                            board_configurations.remove(b)
                            break

    except FileNotFoundError:
        logging.warn(f"No {board_config_file} file found")
    except Exception as e:
        print(e)
        raise e

    return boards
