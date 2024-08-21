#!/usr/bin/env python3

import argparse
from lc_util import logger_setup, logger_get
import yaml

logger = logger_get(__name__)


def get_boards(config_file: str):
    """ 
    Extract board names for DUTs using names and properties.
    Removes duplicates.

    Args:
        config_file (str): The rack configuration file
    """
    with open(config_file, 'r') as stream:
        config = yaml.safe_load(stream)

    names = []
    for board in config['boards']:
        # only include characters up to the second underscore
        # maybe a list of valid board names would be better (PROD-14154)
        try:
            if "dut" in board['properties']:
                lst = board['name'].casefold().split("_")
                name = lst[0]
                if len(lst) > 1:
                    name += "_" + lst[1]
                if len(lst) > 2 and lst[2] == "dvk":
                    name += "_" + lst[2]
                names.append(name)
        except:
            pass
    
    # remove duplicate names from list
    names = list(dict.fromkeys(names))

    # print list as a string separated by spaces for GitHub action use (shell)
    print(" ".join(names))

    return names


if __name__ == "__main__":
    logger = logger_setup(__file__)

    parser = argparse.ArgumentParser(
        description='Program board(s) with a hex file')

    parser.add_argument('-c', '--config_file', required=True,
                        help="The configuration file that describes the boards")
    args = parser.parse_args()

    get_boards(args.config_file)
