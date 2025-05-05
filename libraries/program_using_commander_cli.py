from lc_util import logger_setup, logger_get
import platform
import subprocess

logger = logger_get(__name__)


if platform.system() == "Linux":
    # 'Permission denied: [Errno 13]' will occur if the full path isn't used.
    PROGRAM_PATH = "/usr/local/bin/commander-cli/commander-cli"
elif platform.system() == "Windows":
    PROGRAM_PATH = "commander-cli.exe"
elif platform.system() == "Darwin":
    logger.info("macOS: If programming Lyra boards, make sure to install commander-cli and include it in your PATH")
    PROGRAM_PATH = "Commander-cli.app"
else:
    raise Exception("Unsupported OS")

def unlock_device(serial_number: str, device: str):
    try:
        cmd = [PROGRAM_PATH, "device", "unlock", "--serialno", serial_number]
        if len(device) > 0:
            cmd.append("--device")
            cmd.append(device)

        logger.info(f"Unlock command: {' '.join(cmd)}")

        result = subprocess.run(cmd,
                                check=True,
                                capture_output=True,
                                text=True
                                )

        logger.debug(f"Unlock output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error may have occurred: {e.stderr} {e.stdout}")
        return False
    except PermissionError as e:
        logger.error(f"Permission denied: {e}")
        return False


def program_lyra24(file_path: str, serial_number: str, device="", mass_erase=True, unlock=False):
    """Flash a firmware file to a device using Simplicity commander-cli."""
    try:
        if unlock:
            unlock_device(serial_number, device)

        cmd = [PROGRAM_PATH, "flash", "--timestamp", "--serialno", serial_number, file_path]

        # Add optional arguments
        if len(device) > 0:
            cmd.insert(-1, "--device")
            cmd.insert(-1, device)

        if mass_erase:
            cmd.insert(-1, "--masserase")

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

def program_sl917(file_path: str, serial_number: str, device="SiWG917Y111MGABA",
        mass_erase=False, unlock=False):
    """Flash a firmware file to a device using Simplicity commander-cli."""
    try:
        cmd = [PROGRAM_PATH, "flash", "--timestamp",
               "--serialno", serial_number, file_path]

        # Add optional arguments

        if device != "":
            cmd.insert(-1, "--device")
            cmd.insert(-1, device)

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
