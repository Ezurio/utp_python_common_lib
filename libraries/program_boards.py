from lc_util import logger_setup, logger_get
import argparse
from program_using_commander_cli import program_lyra24, program_sl917
from program_using_pyocd import program_with_dvk_probe, program_with_usb_swd
from program_using_nrfjprog import program_nrf
import yaml
import re
import os

logger = logger_get(__name__)

def find_image_file(config, binary_base: str, image_type: str, image_name: str):
    """
    This function files the programming image file for a particular image
    type based on the selected image name

    :param config: Parsed station config file
    :param image_type: Type of the image
    :param image_name: Name of the image to be programmed
    """
    # Fetch the information about the image name from the config data
    image_name_info = config['images'][image_type]['allowed'][image_name]

    # Start by trying to match the filename
    if image_name_info['filename']:
        for dirpath, dirnames, filenames in os.walk(binary_base):
            for f in filenames:
                path = os.path.join(dirpath, f)
                m = re.match(image_name_info['filename'], path)
                if m:
                    # Convert "2.1.99.12345678" to "2.1.99+12345678"
                    version = re.sub(r'^(\d+\.\d+\.\d+)\.(\d+)$', r'\1+\2', m.group(1))
                    return (path, version)

    # If we get here, none of the methods worked
    return (None, None)


def program_boards(config_file: str, images: str, binary_base: str):
    """
    This function will program all of the boards for a single test station.
    The station config is used to define the list of boards as well as the
    image types supported for each board.

    The images parameter to this function is used to override the default
    image name(s) used during programming. The image names in this list are
    "consumed" as they are used. An example of how this works is:

    * An example image list is set to "foo"
    * There are two boards in the station, each of which can allow "foo"
      as a valid image name.
    * When the first board is programmed, it takes "foo" from the image
      list and uses that as the image name to program. "foo" is removed
      from the list.
    * When the second board is programmed, the image list is now empty,
      so the default image name will be used to program the second board.

    :param config_file: Path to the station config file
    :param images: A comma-separated list of image names that will be
      used to override the default image for each board
    :param binary_base: Pathname to the directory where binary images
      are located
    """

    # Convert the images string into a list
    image_list = re.split(r'[\s,]+', images)

    # Parse the station config YAML file
    with open(config_file, 'r') as stream:
        config = yaml.safe_load(stream)

    # Loop to program each board in the list
    for board in config['boards']:
        logger.debug("Programming board {}".format(board['name']))

        # Loop to use each debug probe connected to the board
        for probe in board['probes']:
            logger.debug("Using probe {}".format(probe['sn']))

            image_type = probe['image']
            image = config['images'][image_type]

            # Get the list of image name options for this image
            image_name_choices = list(image['allowed'].keys())

            # Filter our incoming image list based on the choices available
            image_name_list = [i for i in image_list if i in image_name_choices]

            # If there are no choices, use the default
            if len(image_name_list) == 0:
                image_name = config['images'][image_type]['default']
            else:
                # Pick the first one that we find
                image_name = image_name_list[0]

                # Remove it from the list so we don't use it again
                image_list.remove(image_name)
            logger.debug(f"Selected image name {image_name}")

            # Find a filename for the image to program
            filename, version = find_image_file(config, binary_base, image_type, image_name)
            if filename is None or version is None:
                logger.error("Failed to find a valid image file for board {} image name {}".
                        format(board['name'], image_name))
                print("{},{},{}".format(board['name'], None, False))
                continue

            logger.debug(f"Programming file {filename}")
            logger.debug(f"Version number {version}")

            serial_number = str(probe['sn'])
            probe_type = probe['type'].casefold()

            # Add optional parameters that may not be in config file
            params = {'file_path': filename, 'serial_number': serial_number}
            if "family" in probe:
                params['device'] = probe['family']
            if "mass_erase" in probe:
                params['mass_erase'] = convert_to_bool(probe['mass_erase'])
            if "unlock" in probe:
                params['unlock'] = convert_to_bool(probe['unlock'])

            # The Lyra24, RS2xx, and SL917 systems have JLink probes, but 
            # simplicity commander-cli is used to program them.
            ok = False
            if "lyra24" in board['name'] or "rs2xx" in board['name']:
                ok = program_lyra24(**params)
            elif "brd2911a" in board['name'] or "brd2708a" in board['name']:
                ok = program_sl917(**params)
            elif probe_type == "dvkprobe":
                ok = program_with_dvk_probe(**params)
            elif probe_type == "usb_swd":
                ok = program_with_usb_swd(**params)
            elif probe_type == "jlink":
                ok = program_nrf(**params)
            else:
                logger.error(f"Unsupported probe type {probe_type}")

            # Print the board, the expected version number, and the result
            print("{},{},{}".format(board['name'], version, ok))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Program all station boards')

    parser.add_argument('--debug', action='store_true', default=False,
                        help="Enable verbose debug messages")
    parser.add_argument('-c', '--config_file', required=True,
                        help="The configuration file that describes the boards")
    parser.add_argument('-b', '--binary_base', required=True,
                        help="Base pathname for binary programming files")
    parser.add_argument('-i', '--images', required=False, default="",
                        help="The list of image names for programming, overriding the defaults")
    args = parser.parse_args()

    logger = logger_setup(__file__, args.debug)

    program_boards(args.config_file, args.images, args.binary_base)
