from lc_util import logger_get
import subprocess
from pathlib import Path

logger = logger_get(__name__)

NETWORK_CORE = "network"
NETWORK_CORE_FILE_NAME = "CPUNET"


def program_nrfutil(file_path: str, serial_number: str, device="", mass_erase=False, unlock=True):
    """Flash a firmware file to a device using a J-Link (on board device or external probe).

    Args:
        file_path (str): Path to the firmware file to be flashed.
        serial_number (str): Serial number of the device to be programmed.
        device (str, optional): Device name or identifier. Defaults to "".
        mass_erase (bool, optional): Whether to perform a mass erase before programming. Defaults to False.
        unlock (bool, optional): Whether to unlock the device before programming. Defaults to True.
    """
    try:
        recover_cmd = ["nrfutil", "device", "recover",
                       "--serial-number", serial_number]
        reset_cmd = ["nrfutil", "device", "reset",
                     "--serial-number", serial_number]
        program_cmd = ["nrfutil", "device", "program", "--serial-number", serial_number,
                       "--firmware", file_path]
        options = ["--options", "verify=VERIFY_READ"]

        recover_device = unlock

        # If it is network core firmware, program the network core
        if NETWORK_CORE_FILE_NAME in Path(file_path).name:
            net_core = ["--core", NETWORK_CORE]
            program_cmd.extend(net_core)
            # Do not recover the network core because that will clear the application core
            recover_device = False

        if recover_device:
            result = subprocess.run(recover_cmd,
                                    check=True,
                                    capture_output=True,
                                    text=True
                                    )
            logger.debug(f"Recover output: {result.stdout}")

        if mass_erase:
            options.append("chip_erase_mode=ERASE_ALL")

        program_cmd.extend(options)
        logger.info(f"Running command: {' '.join(program_cmd)}")

        # Raise an exception if the command fails,
        # capture stdout and stderr, and return them as strings
        result = subprocess.run(program_cmd,
                                check=True,
                                capture_output=True,
                                text=True
                                )

        logger.debug(f"Program output: {result.stdout}")

        # Reset after programming so that the new firmware is run
        result = subprocess.run(reset_cmd,
                                check=True,
                                capture_output=True,
                                text=True
                                )
        logger.debug(f"Reset output: {result.stdout}")

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
