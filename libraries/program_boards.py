from lc_util import logger_setup, logger_get
import argparse
from program_using_commander_cli import program_lyra24, program_sl917
from program_using_pyocd import program_with_dvk_probe, program_with_usb_swd
from program_using_nrfjprog import program_nrf
import yaml
import re
import os
import time

# Number of times to try failed programming
NUM_PROGRAMMING_RETRIES = 3

logger = logger_get(__name__)

def convert_to_bool(value: str) -> bool:
    """
    Convert a string to a boolean.

    :param value: The string to convert
    :returns: The boolean value
    """
    return value.lower() in ("yes", "true", "t", "1")

def find_image_file(config, base: str, image_type: str, image_name: str):
    """
    This function finds the programming image file(s) for a particular image
    type based on the selected image name

    :param config: Parsed station config file
    :param image_type: Type of the image
    :param image_name: Name of the image to be programmed

    :returns: A list of tuples (filename, version) for each file found or None if no files
        are found.
    """
    output = None
    
    # Fetch the information about the image name from the config data
    image_name_info = config['images'][image_type]['allowed'][image_name]

    # Start by trying to match the filename
    if type(image_name_info['filename']) is list:
        # If the filename is a list, use it as is
        pass
    elif type(image_name_info['filename']) is str:
        # If the filename is not a list, make it into one
        image_name_info['filename'] = [ image_name_info['filename'] ]
    else:
        # Make the filename list empty
        image_name_info['filename'] = []

    for filename in image_name_info['filename']:
        for dirpath, dirnames, filenames in os.walk(base):
            for f in filenames:
                path = os.path.join(dirpath, f)
                m = re.match(filename, path)
                if m:
                    # Convert "2.1.99.12345678" to "2.1.99+12345678"
                    version = re.sub(r'^(\d+\.\d+\.\d+)\.(\d+)$', r'\1+\2', m.group(1))

                    # Create the output list if it doesn't exist
                    if output is None:
                        output = []

                    # Check to see if we already have this filename
                    skip = False
                    for t in output:
                        if os.path.basename(t[0]) == os.path.basename(path):
                            # We already have this filename, so skip it
                            skip = True
                            break

                    # Add this filename and version to the lists
                    if not skip:
                        output.append((path, version))

    # Return what we found from above
    return output

def program_boards(test: bool, config_file: str, images: str, binary_base: str, release_base: str):
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

    Two directories are provided to this function. Both are to the root of
    a set of binary image files that can match the patterns used in the
    station config. The first path, binary_base, is always searched first.
    The second path, release_base, is used as a backup for when an image
    is needed, but not produced by the current build.

    :param test: True if this is a test run, False if we are actually programming
    :param config_file: Path to the station config file
    :param images: A comma-separated list of image names that will be
      used to override the default image for each board
    :param binary_base: Pathname to the directory where binary images
      are located for the current build under test
    :param release_base: Pathname to the directory where released binary
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

        # Set up defaults for script output values
        last_version = None
        last_result = True

        # Loop to use each debug probe connected to the board
        for probe in board['probes']:
            logger.debug("Using probe {}".format(probe['sn']))

            image_type = probe['image']
            logger.debug(f"Programming image type {image_type}")

            # Get the list of image name options for this image type
            image = config['images'][image_type]
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

            # Start a list of image names that we will need to program
            programming_image_names = [ image_name ]

            # Now that we've selected an image name, check to see if we have a "first" image
            # to also program.
            if 'first' in image and image['first']:
                # image['first'] is an image name, possibly with a variable substitution that 
                # needs to be replaced with the current image name as $(image_name)
                first_image_name = image['first'].replace("$(image_name)", image_name)

                # Add the first image to the start of the list
                programming_image_names.insert(0, first_image_name)
    
            # Check for a "last" image to program
            if 'last' in image and image['last']:
                # image['last'] is an image name, possibly with a variable substitution that
                # needs to be replaced with the current image name as $(image_name)
                last_image_name = image['last'].replace("$(image_name)", image_name)

                # Add the last image to the end of the list
                programming_image_names.append(last_image_name)

            # Iterate through the programming image names and program each one
            for image_name in programming_image_names:
                # Find a filename for the image to program
                files = find_image_file(config, binary_base, image_type, image_name)
                if files is None:
                    files = find_image_file(config, release_base, image_type, image_name)
                if files is None:
                    logger.error("Failed to find a valid image file for board {} image name {}".
                                    format(board['name'], image_name))
                    print("{},{},{}".format(board['name'], None, False))
                    return

                for f in files:
                    logger.debug(f"Programming file {f[0]}")
                    logger.debug(f"Version number {f[1]}")

                    # Update the most recent version
                    last_version = f[1]

                    # In test mode, don't do any programming
                    if test:
                        continue

                    # Set up the parameters for the programming function
                    params = {'file_path': f[0], 'serial_number': str(probe['sn'])}
                    if "family" in probe:
                        params['device'] = probe['family']
                    if "mass_erase" in probe:
                        params['mass_erase'] = convert_to_bool(probe['mass_erase'])
                    if "unlock" in probe:
                        params['unlock'] = convert_to_bool(probe['unlock'])

                    # Program the image using the appropriate programming function
                    retries = NUM_PROGRAMMING_RETRIES 
                    while True:
                        ok = False
                        probe_type = probe['type'].casefold()
                        if "lyra24" in board['name'] or re.match(r'^rs26\d$', board['name']):
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
                            break

                        if ok:
                            logger.debug("Programming successful")
                            break
                        elif retries > 0:
                            logger.info("Programming failed, retrying...")
                            retries -= 1
                        else:
                            logger.error("Programming failed, no retries left")
                            break

                    # Check the result of the programming
                    if not ok and last_result:
                        last_result = False

                # If the image has a wait step, perform the wait
                image_name_info = config['images'][image_type]['allowed'][image_name]
                if 'wait' in image_name_info and not test:
                    logger.debug(f"Waiting {image_name_info['wait']} seconds after programming image {image_name}")
                    time.sleep(image_name_info['wait'])

        # Print the board, the expected version number, and the result
        print("{},{},{}".format(board['name'], last_version, last_result))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Program all station boards')

    parser.add_argument('--debug', action='store_true', default=False,
                        help="Enable verbose debug messages")
    parser.add_argument('-t', '--test', action='store_true', default=False,
                        help="Run in test mode, no programming")
    parser.add_argument('-c', '--config_file', required=True,
                        help="The configuration file that describes the boards")
    parser.add_argument('-b', '--binary_base', required=True,
                        help="Base pathname for build under test programming files")
    parser.add_argument('-r', '--release_base', required=True,
                        help="Base pathname for released programming files")
    parser.add_argument('-i', '--images', required=False, default="",
                        help="The list of image names for programming, overriding the defaults")
    args = parser.parse_args()

    logger = logger_setup(__file__, args.debug)

    program_boards(args.test, args.config_file, args.images, args.binary_base, args.release_base)
