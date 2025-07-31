import os
import re

def newest_image(old: tuple, new: tuple):
    """
    This function compares two image tuples and returns the newest one.
    Assumes the version number is in the format "major.minor.patch+timestamp".

    :param old: The old image tuple (filename, version)
    :param new: The new image tuple (filename, version)

    :returns: The newest image tuple
    """
    def parse_version(version: str):
        """
        Parse a version string in the format "major.minor.patch+timestamp" into a tuple.
        """
        match = re.match(r"(\d+)\.(\d+)\.(\d+)\+(\d+)", version)
        if not match:
            raise ValueError(f"Invalid version string format: '{version}'. Expected format is 'major.minor.patch+timestamp'.")
        major, minor, patch, timestamp = match.groups()
        return int(major), int(minor), int(patch), int(timestamp)

    if old is None:
        return new
    elif new is None:
        return old
    else:
        old_version = parse_version(old[1])
        new_version = parse_version(new[1])
        return new if new_version > old_version else old

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

    # Check each of the filename patterns in the filename list
    for filename in image_name_info['filename']:
        # Search all of the files in our base directory for a match against
        # the filename pattern
        newest_match = None
        for dirpath, dirnames, filenames in os.walk(base):
            for f in filenames:
                path = os.path.join(dirpath, f)
                m = re.match(filename, path)
                if m:
                    # Convert "2.1.99.12345678" to "2.1.99+12345678"
                    version = re.sub(r'^(\d+\.\d+\.\d+)\.(\d+)$', r'\1+\2', m.group(1))

                    # Select this file if it is newer
                    newest_match = newest_image(newest_match, (path, version))

        # Add this filename's file to the output list
        if newest_match:
            if output is None:
                output = []
            output.append(newest_match)

    # Return what we found from above
    return output
