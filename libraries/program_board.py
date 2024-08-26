from lc_util import logger_setup, logger_get
import argparse
from program_using_commander_cli import program_lyra24
from program_using_pyocd import program_with_dvk_probe
import yaml

logger = logger_get(__name__)


def convert_to_bool(value: str) -> bool:
    """Convert a string to a boolean.

    Args:
        value (str): The string to convert

    Returns:
        bool: The boolean value
    """
    return value.lower() in ("yes", "true", "t", "1")


def program_board(config_file: str, board_to_program: str, hex_path: str, device="", mass_erase=True, unlock=False):
    """ 
    Program a board with a hex file using the configuration file to get 
    the probe type and serial number.
    This doesn't use the Python API to program the board.
    This doesn't require determining the connected boards because 
    if the firmware is not valid, discovery will fail.

    Args:
        config_file (str): The configuration file
        board_to_program (str): The [partial but unique] name of board to program
        hex_path (str): The path to the hex file
        device (str, optional): The part number of the device. If programming fails, this may be required. Defaults to "".
        mass_erase (bool, optional): Mass erase the device. Defaults to False.
        unlock (bool, optional): Unlock the device. Defaults to False.

    Returns:
        Tuple[bool, int, int]: Success, number of boards programmed, number of boards failed

    """
    with open(config_file, 'r') as stream:
        config = yaml.safe_load(stream)

    board_to_program = board_to_program.casefold()
    ok_count = 0
    fail_count = 0
    success = True
    for board in config['boards']:
        ok = False
        try:
            name = board['name'].casefold()
            if board_to_program not in name:
                continue

            probe = board['probe']
            serial_number = str(probe['sn'])
            probe_type = probe['type'].casefold()

            # Add optional parameters that may not be in config file
            params = {'file_path': hex_path, 'serial_number': serial_number}
            if "family" in probe:
                params['device'] = probe['family']
            if "mass_erase" in probe:
                params['mass_erase'] = convert_to_bool(probe['mass_erase'])
            if "unlock" in probe:
                params['unlock'] = convert_to_bool(probe['unlock'])

            if "lyra24" in name:
                ok = program_lyra24(**params)
            elif probe_type == "dvkprobe":
                ok = program_with_dvk_probe(**params)
            elif probe_type == "jlink":
                pass
            else:
                logger.error(f"Unsupported probe type {probe_type}")

        except:
            logger.error(
                f"Valid configuration for {board_to_program} not found")

        if ok:
            ok_count += 1
        else:
            fail_count += 1
            success = False

    # These prints may be used when called in an action
    if success:
        print("Success")
    else:
        print("Failure")

    print(f"{ok_count} {board_to_program} boards programmed with {hex_path}, {fail_count} failed")

    return success, ok_count, fail_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Program board(s) with a hex file')

    parser.add_argument('--debug', action='store_true', default=True,
                        help="Enable verbose debug messages")
    parser.add_argument('-c', '--config_file', required=True,
                        help="The configuration file that describes the boards")
    parser.add_argument('-b', '--board', required=True,
                        help="The partial but unique name of the board(s) to program")
    parser.add_argument('-f', '--hex_file', required=True,
                        help="The absolute path to the hex file")
    args = parser.parse_args()

    logger = logger_setup(__file__, args.debug)

    program_board(args.config_file, args.board, args.hex_file)
