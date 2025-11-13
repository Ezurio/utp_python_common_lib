from lc_util import logger_setup, logger_get
import platform
import subprocess

logger = logger_get(__name__)

def program_with_dvk_probe_cmd(file_path: str, serial_number: str, device="", mass_erase=True, unlock=True):
    cmd = ["pyocd", "flash", "--probe", serial_number, file_path]

    if device != "":
        # J-Link requires suffix but pyocd doesn't.
        device = device.replace("_xxAA", "")
        cmd.insert(-1, "--target")
        cmd.insert(-1, device)
    else:
        raise ValueError("Device type/family must be specified")

    # Add optional arguments before file name
    if not unlock:
        cmd.insert(-1, "-O")
        cmd.insert(-1, "auto_unlock=0")

    if mass_erase:
        cmd.insert(-1, "--erase")
        cmd.insert(-1, "chip")
    else:
        cmd.insert(-1, "--erase")
        cmd.insert(-1, "auto")

    return [ cmd ]

def program_with_dvk_probe(file_path: str, serial_number: str, device="", mass_erase=True, unlock=True):
    """Flash a firmware file to a device using the DVK probe."""
    cmd = program_with_dvk_probe_cmd(file_path, serial_number, device, mass_erase, unlock)
    try:
        for c in cmd:
            logger.info(f"Running command: {' '.join(c)}")

            # Raise an exception if the command fails,
            # capture stdout and stderr, and return them as strings
            result = subprocess.run(c,
                                    check=True,
                                    capture_output=True,
                                    text=True
                                    )

            logger.debug(f"Command output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred: {e.stderr}")
        return False
    except PermissionError as e:
        logger.error(f"Permission denied: {e}")
        return False
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return False
