from lc_util import logger_setup, logger_get
import argparse
import program_using_commander_cli
import program_using_pyocd
import program_using_nrfutil
import yaml
import re
import os
import time
import subprocess
import concurrent.futures
import requests
import shutil
import board_config_util

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

def download_image_file(config, base: str, image_type: str, image_name: str):
    """
    This function downloads the image file from a URL specified in the configuration.
    It is used as a fallback if the image file is not found in the specified base directory.

    :param config: Parsed station config file
    :param base: Base directory to store the downloaded image
    :param image_type: Type of the image
    :param image_name: Name of the image to be downloaded

    :returns: A list of tuples (filename, version) for each file found or None if no files
        are found.
    """
    output = None

    # Fetch the information about the image name from the config data
    image_name_info = config['images'][image_type]['allowed'][image_name]

    # Make sure that we have a valid filename list
    if type(image_name_info['filename']) is list:
        # If the filename is a list, use it as is
        pass
    elif type(image_name_info['filename']) is str:
        # If the filename is not a list, make it into one
        image_name_info['filename'] = [ image_name_info['filename'] ]
    else:
        # Make the filename list empty
        image_name_info['filename'] = []

    # Make sure that we have a valid URL list
    if type(image_name_info['url']) is list:
        # If the URL is a list, use it as is
        pass
    elif type(image_name_info['url']) is str:
        # If the URL is not a list, make it into one
        image_name_info['url'] = [ image_name_info['url'] ]
    else:
        # Make the URL list empty
        image_name_info['url'] = []

    # Filename list and URL list should be the same length
    if len(image_name_info['filename']) != len(image_name_info['url']):
        logger.error(f"Filename and URL lists are not the same length for image {image_name}")
        return None

    # Iterate through the URL list and download each file
    for url, filename in zip(image_name_info['url'], image_name_info['filename']):
        # Fetch the file from the URL
        dl_filename = None
        try:
            dl_filename = os.path.join(base, os.path.basename(url))
            logger.debug(f"Downloading image from {url} to {dl_filename}")

            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(dl_filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            logger.debug("Download complete")
        except requests.RequestException as e:
            logger.error(f"Failed to fetch image from URL {url}: {e}")
            continue

        if dl_filename:
            # Match the filename against the filename pattern
            m = re.match(filename, dl_filename)
            if m:
                # Convert "2.1.99.12345678" to "2.1.99+12345678"
                version = re.sub(r'^(\d+\.\d+\.\d+)\.(\d+)$', r'\1+\2', m.group(1))

                # Create the output list if it doesn't exist
                if output is None:
                    output = []

                # Add the downloaded file to the output list
                output.append((dl_filename, version))

    return output

def execute_board_steps(board):
    """
    Execute the programming steps for a given board.

    :param board: The board configuration containing the steps to execute.

    :returns: tuple[str, bool, str]: A tuple containing the board name, success
      status, and log output.
    """
    output_log = [ ]
    for step in board['steps']:
        action = step['action']
        if action == "command":
            for cmd in step['cmd']:
                success = False
                for attempt in range(NUM_PROGRAMMING_RETRIES):
                    output_log.append(f"{board['name']}: Attempt {attempt + 1}: Running command: {' '.join(cmd)}")

                    try:
                        result = subprocess.run(cmd,
                                                check=True,
                                                capture_output=True,
                                                text=True
                                                )
                        output_log.append(f"{board['name']}: STDOUT: {result.stdout}")
                        if result.stderr:
                            output_log.append(f"{board['name']}: STDERR: {result.stderr}")
                        success = True
                        break

                    except subprocess.CalledProcessError as e:
                        output_log.append(f"{board['name']}: Attempt {attempt + 1}: Error occurred.")
                        output_log.append(f"{board['name']}: STDOUT: {e.stdout}")
                        output_log.append(f"{board['name']}: STDERR: {e.stderr}")
                        if attempt < NUM_PROGRAMMING_RETRIES - 1:
                            output_log.append(f"{board['name']}: Retrying...")
                            time.sleep(1)  # Short delay before retrying

                    except FileNotFoundError as e:
                        output_log.append(f"{board['name']}: Fatal error: Command not found: {e.filename}")
                        return (board['name'], False, "\n".join(output_log))

                if not success:
                    output_log.append(f"{board['name']}: All attempts failed.")
                    return (board['name'], False, "\n".join(output_log))

        elif action == "wait":
            wait_time = step['time']
            output_log.append(f"{board['name']}: Waiting for {wait_time} seconds")
            time.sleep(wait_time)

        else:
            output_log.append(f"{board['name']}: Unknown action {action} in board steps")
            return (board['name'], False, "\n".join(output_log))

    output_log.append(f"{board['name']}: All steps completed successfully")
    return (board['name'], True, "\n".join(output_log))

def program_boards(test: bool, config_file: str, images: str, binary_base: str, release_base: str, tmp_dir: str):
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
    :param tmp_dir: Pathname to the directory where temporary files
      should be stored
    """
    # Convert the images string into a list
    image_list = re.split(r'[\s,]+', images)

    # Parse the station config YAML file
    with open(config_file, 'r') as stream:
        config = yaml.safe_load(stream)

    # Loop to program each board in the list
    for board in config['boards']:
        logger.debug("Programming board {}".format(board['name']))

        # Prepare a list of operations to perform
        board['steps'] = [ ]

        # Set up defaults for script output values
        board['last_version'] = None

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
                # Find a filename for the image to program. Search in this order:
                # 1. The current build under test
                # 2. The released build
                # 3. Download the image from a URL
                files = board_config_util.find_image_file(config, binary_base, image_type, image_name)
                if files is None:
                    files = board_config_util.find_image_file(config, release_base, image_type, image_name)
                if files is None:
                    files = download_image_file(config, tmp_dir, image_type, image_name)
                if files is None:
                    logger.error("Failed to find a valid image file for board {} image name {}".
                                    format(board['name'], image_name))
                    print("{},{},{}".format(board['name'], None, False))
                    return

                for f in files:
                    logger.debug(f"Programming file {f[0]}")
                    logger.debug(f"Version number {f[1]}")

                    # Update the most recent version
                    board['last_version'] = f[1]

                    # Set up the parameters for the programming function
                    params = {'file_path': f[0], 'serial_number': str(probe['sn'])}
                    if "family" in probe:
                        params['device'] = probe['family']
                    if "mass_erase" in probe:
                        params['mass_erase'] = convert_to_bool(probe['mass_erase'])
                    if "unlock" in probe:
                        params['unlock'] = convert_to_bool(probe['unlock'])

                    probe_type = probe['type'].casefold()
                    if "lyra24" in board['name'] or re.match(r'^rs26\d$', board['name']):
                        board['steps'].append({"action": "command",
                            "cmd": program_using_commander_cli.program_lyra24_cmd(**params)})
                    elif "brd2911a" in board['name'] or "brd2708a" in board['name']:
                        board['steps'].append({"action": "command",
                            "cmd": program_using_commander_cli.program_sl917_cmd(**params)})
                    elif probe_type == "dvkprobe" or probe_type == "usb_swd":
                        board['steps'].append({"action": "command",
                            "cmd": program_using_pyocd.program_with_dvk_probe_cmd(**params)})
                    elif probe_type == "jlink":
                        board['steps'].append({"action": "command",
                            "cmd": program_using_nrfutil.program_nrfutil_cmd(**params)})
                    else:
                        logger.error(f"Unsupported probe type {probe_type}")
                        break

                # If the image has a wait step, perform the wait
                image_name_info = config['images'][image_type]['allowed'][image_name]
                if 'wait' in image_name_info:
                    board['steps'].append({"action": "wait",
                        "time": image_name_info['wait']})

    # If we are not in test mode, perform the programming now
    if not test:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(config['boards'])) as executor:
            future_to_board = {executor.submit(execute_board_steps, board): board for board in config['boards']}
            for future in concurrent.futures.as_completed(future_to_board):
                board_name, success, log = future.result()
                board = future_to_board[future]
                if not success:
                    logger.error(f"{board_name}: Programming failed")
                    logger.error(log)
                    board['program_status'] = False
                else:
                    logger.info(f"{board_name}: Programming succeeded")
                    logger.info(log)
                    board['program_status'] = True
    else:
        # Simulate successful programming in test mode
        for board in config['boards']:
            board['program_status'] = True 
    
    # Print the programming results
    for board in config['boards']:
        # Print the board, the expected version number, and the result
        print("{},{},{}".format(board['name'], board['last_version'], board['program_status']))

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

    # Create a temporary directory to store downloaded images
    tmp_dir = os.path.join(os.getcwd(), "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    try:
        # Program the boards using the provided arguments
        program_boards(args.test, args.config_file, args.images, args.binary_base, args.release_base, tmp_dir)
    finally:
        # Clean up the temporary directory
        shutil.rmtree(tmp_dir, ignore_errors=True)
