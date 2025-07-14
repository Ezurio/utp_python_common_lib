from lc_util import logger_get
import subprocess

logger = logger_get(__name__)


def program_nrfutil(file_path: str, serial_number: str, device="", mass_erase=False, unlock=True):
    """Flash a firmware file to a device using a J-Link (on board device or external probe).

    Args:
        unlock (bool, optional): For Nordic, this means recover the device. Defaults to True.
    """
    try:
        recover_cmd = ["nrfutil", "device", "recover",
                       "--serial-number", serial_number]
        reset_cmd = ["nrfutil", "device", "reset",
                     "--serial-number", serial_number]
        program_cmd = ["nrfutil", "device", "program", "--serial-number", serial_number,
                       "--firmware", file_path]
        options = ["--options", "verify=VERIFY_READ"]

        if unlock:
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
