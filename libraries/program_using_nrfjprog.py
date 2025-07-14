from lc_util import logger_setup, logger_get
import platform
import subprocess

logger = logger_get(__name__)

FAMILY_VALUES = ["NRF51", "NRF52", "NRF53", "NRF91"]


def program_nrfjprog(file_path: str, serial_number: str, device="", mass_erase=False, unlock=True, erase_qspi=False):
    """Flash a firmware file to a device using a J-Link (on board device or external probe).

    Args:
        unlock (bool, optional): For Nordic, this means recover the device. Defaults to True.
    """
    try:
        cmd = ["nrfjprog", "-s", serial_number,
               "--program", file_path, "--verify"]

        if unlock:
            cmd.append("--recover")
        elif mass_erase:
            cmd.append("--chiperase")
        else:
            cmd.append("--sectorerase")

        # Device shouldn't be needed when using nrfjprog
        # Try to convert config file value to a valid command line option
        if device != "":
            for d in FAMILY_VALUES:
                if d.casefold() in device.casefold():
                    cmd.append("--family")
                    cmd.append(d)
                    break

        if erase_qspi:
            cmd.append("--qspieraseall")

        # Reset after programming so that the new firmware is run
        cmd.append("--reset")

        logger.info(f"Running command: {' '.join(cmd)}")

        # Raise an exception if the command fails,
        # capture stdout and stderr, and return them as strings
        result = subprocess.run(cmd,
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
