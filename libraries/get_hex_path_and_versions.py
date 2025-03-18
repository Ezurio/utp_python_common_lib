#!/usr/bin/env python3

import argparse
from lc_util import logger_setup, logger_get
import os
import subprocess
import re

logger = logger_get(__name__)


def get_hex_path_and_versions(build_dir: str, board_name: str, suffix: str = "", hex_name: str = "merged.hex"):
    """ 
    Helper function to find the hex file for a board in the build directory.
    Extract short version number and long version number from the folder name.
    This makes assumptions about the folder structure and naming conventions.
    """
    partial_folder_name = board_name + suffix

    # From the build directory,
    # recursively find a folder with the partial name of the board (using regex).
    result = subprocess.run(
        ['find', build_dir, '-type', 'd', '-regex',
            f'.*{partial_folder_name}.*'],
        stdout=subprocess.PIPE,
        text=True
    )
    sub_folder = result.stdout.strip()
    logger.debug(f"{sub_folder=}")

    # For Zephyr builds, the above "find" will likely return at least 4 directories
    # because of the nested zephyr directory and because of "PUBLIC" vs. private
    # artifacts:
    #   ./build/canvas_python_firmware_2.1.99.1742314610/mg100/build.mg100_2.1.99.1742314610/
    #   ./build/canvas_python_firmware_2.1.99.1742314610/mg100/build.mg100_2.1.99.1742314610/zephyr/
    #   ./build/canvas_python_firmware_PUBLIC_2.1.99.1742314610/mg100/build.mg100_2.1.99.1742314610/
    #   ./build/canvas_python_firmware_PUBLIC_2.1.99.1742314610/mg100/build.mg100_2.1.99.1742314610/zephyr/
    #
    # For Lyra builds, the above "find" will likely return a single directory:
    #     lyra24_p10_mcuboot_0.1.99_1721932245
    #
    # For SL917 builds, where the board name might not be fully unique, the "find"
    # may return multiple directories:
    #     brd2911a_0.0.99_1721932245
    #     brd2911ap_0.0.99_1721932245

    if len(sub_folder) == 0:
        logger.error(
            f"Build folder with partial name {partial_folder_name} not found")
        empty = ""
        print(f"{empty},{empty},{empty}")
        return empty, empty, empty

    # Convert the result into a list. The list MAY have just one entry.
    sub_folder_list = sub_folder.split('\n')
    logger.debug(f"Original sub-folder list: {sub_folder_list}")

    # Separate each list entry into its component parts
    hex_paths = {}
    for folder in sub_folder_list:
        # Look for a version number plus timestamp, separated by either a '.' or an '_'
        m = re.search(r"(.*)_(\d+\.\d+\.\d+)[\._](\d+)", folder)
        if m:
            groups = m.groups()
            if len(groups) == 3:
                board = os.path.basename(groups[0])
                version = groups[1]
                timestamp = groups[2]
                if "build." in board:
                    board = board.split("build.")[1]
                hex_paths[folder] = [ board, version, timestamp ]
                logger.debug("Found board {} version {} timestamp {}".format(board, version, timestamp))

    # Attempt to find the programming file that we need
    logger.debug("Looking for board {}, file name {}".format(partial_folder_name, hex_name))
    short_version = None
    long_version = None
    hex_path = None
    for folder in hex_paths:
        # Only use a directory that matches our board name exactly
        if hex_paths[folder][0] != partial_folder_name:
            continue

        # Check to see if the directory contains the file we need
        if os.path.exists(os.path.join(folder, hex_name)):
            hex_path = os.path.join(folder, hex_name)
            short_version = hex_paths[folder][1]
            long_version = hex_paths[folder][1] + "+" + hex_paths[folder][2]
            break

    # Values must be printed to use them in a GitHub action
    print(f"{hex_path},{short_version},{long_version}")

    return hex_path, short_version, long_version


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Find programming hex file full path and extract version number')

    parser.add_argument('--debug', action='store_true', default=False,
                        help="Enable verbose debug messages")
    parser.add_argument('-o', '--output_dir', required=True,
                        help="Build output directory")
    parser.add_argument('-b', '--board_name', required=True, help="Board name")
    parser.add_argument('-s', '--board_name_suffix',
                        default="", help="Board name suffix")
    parser.add_argument('-f', '--file_name',
                        default="merged.hex", help="Programming file name")
    args = parser.parse_args()

    logger = logger_setup(__file__, args.debug)

    if "bl5340" in args.board_name.casefold():
        if args.file_name == "merged.hex":
            args.file_name = "merged_domains.hex"

    get_hex_path_and_versions(build_dir=args.output_dir, board_name=args.board_name,
                              suffix=args.board_name_suffix, hex_name=args.file_name)
