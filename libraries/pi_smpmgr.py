import subprocess
import os
import re

SMPMGR_TIMEOUT = 10 # seconds

def smpmgr_upgrade(device_name: str, file: str, slot: int = 1) -> bool:
    """
    Perform an OTA upgrade of the DUT given by the device name using the specified file.
    
    :param device_name: The name of the device to upgrade. The device should be
      advertising over BLE with this name.
    :param file: The path to the firmware file to use for the upgrade.
    """
    try:
        new_env = os.environ.copy()
        new_env["TERM"] = "dumb"  # Set TERM to dumb to avoid terminal control sequences

        # Run the upgrade command using the smpmgr tool
        result = subprocess.run(
            ["smpmgr", "--timeout", str(SMPMGR_TIMEOUT), "--ble", device_name, "upgrade", "--slot", str(slot), file],
            check=True,
            capture_output=True,
            text=True,
            env=new_env)
        print(f"Upgrade successful: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Upgrade failed: stdout {e.stdout} stderr {e.stderr}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False

def parse_image_state(response: str) -> list:
    """
    Parses the shell command output to extract image state information.

    :param response: The multiline string output from the shell command.

    :returns: A list of tuples containing (version, hash_string) for each
      image state.  The list is indexed by the slot number. Returns an
      empty list if no image states are found.
    """
    # Split the text into sections for each ImageState.
    # We take the parts after the first split, as the part before it is irrelevant.
    image_states_str = response.split("ImageState(")[1:]

    # A dictionary to temporarily store the parsed data {slot: (version, hash)}
    parsed_data = {}

    for state_str in image_states_str:
        # Use regular expressions to find the slot, version, and hash.
        # r"slot=(\d+)" matches 'slot=' followed by one or more digits.
        slot_match = re.search(r"slot=(\d+)", state_str)
        # r"version='(.*?)'" matches 'version=' followed by any characters
        # inside single quotes (non-greedy).
        version_match = re.search(r"version='(.*?)'", state_str)
        # r"hash=HashBytes\(\s*'(.*?)'\s*\)" matches 'hash=HashBytes('
        # followed by an optional space, then a string in single quotes,
        # and an optional space before the closing parenthesis.
        hash_match = re.search(r"hash=HashBytes\(\s*'(.*?)'\s*\)", state_str)

        # Ensure all three pieces of information were found
        if slot_match and version_match and hash_match:
            slot = int(slot_match.group(1))
            version = version_match.group(1)
            hash_str = hash_match.group(1)

            # Correct the version format if necessary
            vsplit = version.split('.')
            if len(vsplit) == 4:
                version = '.'.join(vsplit[0:3]) + '+' + vsplit[3]

            parsed_data[slot] = (version, hash_str)

    # If we parsed any data, convert the dictionary to a list.
    # The list will be indexed by the slot number.
    if parsed_data:
        # Find the highest slot number to determine the size of the list.
        max_slot = max(parsed_data.keys())
        # Create a list of Nones with a length of max_slot + 1.
        result_list = [None] * (max_slot + 1)
        # Populate the list using the slot number as the index.
        for slot, data in parsed_data.items():
            result_list[slot] = data
        return result_list
    else:
        # Return an empty list if no image states were found.
        return []

def smpmgr_get_status(device_name: str) -> list:
    """
    Get the state of the images on the device using the smpmgr tool.

    :param device_name: The name of the device to query. The device should be
      advertising over BLE with this name.

    :returns: A list of tuples containing (version, hash_string) for each
      image state. The list is indexed by the slot number. Returns an empty
      list if no image states are found.
    """
    try:
        new_env = os.environ.copy()
        new_env["TERM"] = "dumb"  # Set TERM to dumb to avoid terminal control sequences

        # Run the status command using the smpmgr tool
        result = subprocess.run(
            ["smpmgr", "--timeout", str(SMPMGR_TIMEOUT), "--ble", device_name, "image", "state-read"],
            check=True,
            capture_output=True,
            text=True,
            env=new_env)
        return parse_image_state(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Status query failed: stdout {e.stdout} stderr {e.stderr}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return []

def smpmgr_confirm(device_name: str, hash_str: str) -> bool:
    """
    Confirm the currently running image on the device using the smpmgr tool.

    :param device_name: The name of the device to confirm. The device should be
      advertising over BLE with this name.
    :param hash_str: The SHA256 hash of the image to confirm.

    :returns: True if the confirmation was successful, False otherwise.
    """
    try:
        new_env = os.environ.copy()
        new_env["TERM"] = "dumb"  # Set TERM to dumb to avoid terminal control sequences

        # Run the confirm command using the smpmgr tool
        result = subprocess.run(
            ["smpmgr", "--timeout", str(SMPMGR_TIMEOUT), "--ble", device_name, "image", "state-write", hash_str, "true"],
            check=True,
            capture_output=True,
            text=True,
            env=new_env)
        print(f"Confirmation result: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Confirmation failed: stdout {e.stdout} stderr {e.stderr}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False

def smpmgr_reset(device_name: str) -> bool:
    """
    Reset the device using the smpmgr tool.

    :param device_name: The name of the device to reset. The device should be
      advertising over BLE with this name.

    :returns: True if the reset was successful, False otherwise.
    """
    try:
        new_env = os.environ.copy()
        new_env["TERM"] = "dumb"  # Set TERM to dumb to avoid terminal control sequences

        # Run the reset command using the smpmgr tool
        result = subprocess.run(
            ["smpmgr", "--timeout", str(SMPMGR_TIMEOUT), "--ble", device_name, "os", "reset"],
            check=True,
            capture_output=True,
            text=True,
            env=new_env)
        print(f"Reset result: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Reset failed: stdout {e.stdout} stderr {e.stderr}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False
