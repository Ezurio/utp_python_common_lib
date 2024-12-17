import intelhex
import io
import logging
import HciSerialPort as hci
import hci.command as hci_cmd


class HciProgrammer():

    MINIDRIVER_LOAD_ADDR = 0x00270400
    MINI_DRIVER_MAX_SIZE = 15 * 1024
    SS_ADDR = 0x500000
    SS_LEN = 0x1400
    DS_ADDR = 0x501400
    FLASH_SIZE = 256 * 1024
    LAUNCH_FIRMWARE_ADDR = 0x00000000
    HCI_DEFAULT_BAUDRATE = 115200
    HCI_FLASH_FIRMWARE_BAUDRATE = 3000000

    def __init__(self, mini_driver: str = '', port: str = '', baud_rate: int = 0, chip_erase: bool = False):
        self.mini_driver_path = mini_driver
        self.hci_port = hci.HciSerialPort()
        self.com_port = port
        self.baud_rate = baud_rate
        self.chip_erase_enable = chip_erase

    def __load_mini_driver(self):
        """Loads the mini driver into RAM to provide chip erase, change baud and CRC functions

        Raises:
            Exception: raise exception on error
        """
        self.hci_port.send_hci_reset()
        self.hci_port.send_download_minidriver()
        minidriver_bin = io.BytesIO()
        if intelhex.hex2bin(self.mini_driver_path, minidriver_bin, start=self.MINIDRIVER_LOAD_ADDR, size=self.MINI_DRIVER_MAX_SIZE, pad=self.hci_port.RAM_PAD):
            raise Exception('Could not convert minidriver to binary')
        self.hci_port.write_ram(self.MINIDRIVER_LOAD_ADDR,
                                minidriver_bin, self.hci_port.RAM_PAD)
        self.hci_port.send_launch_ram(self.MINIDRIVER_LOAD_ADDR)
        pass

    def init(self, mini_driver: str, port: str, baud_rate: int, chip_erase: bool = False):
        self.__init__(mini_driver, port, baud_rate, chip_erase)

    def open_com_init_mini_driver(self):
        self.hci_port.open(self.com_port, self.baud_rate)
        self.__load_mini_driver()

    def chip_erase(self):
        """Erase entire flash contents
        """
        logging.info('Performing chip erase...')
        self.hci_port.send_chip_erase()
        logging.info('Chip erase finished')

    def program_firmware(self, baud_rate: int = HCI_DEFAULT_BAUDRATE, file_path: str | None = None, chip_erase_enable: bool = False):
        """Program the firmware file

        Args:
            baud_rate (int): Baud rate to program the firmware at
            file_path (str): Path to firmware file (hex or hcd)

        Raises:
            Exception: raise exception on error
        """
        if chip_erase_enable or file_path:
            logging.info('Loading minidriver...')
            self.open_com_init_mini_driver()
        else:
            logging.info('No firmware or chip erase specified, exiting')
            return

        if chip_erase_enable:
            self.chip_erase()

        if file_path:
            is_hex = False
            # Get file extension from path
            file_ext = file_path.split('.')[-1].casefold()
            if file_ext == 'hex':
                is_hex = True
            elif file_ext != 'hcd':
                raise Exception('Invalid file extension, must be .hex or .hcd')

            if baud_rate != self.HCI_DEFAULT_BAUDRATE:
                logging.info(f'Changing baud to {baud_rate}')
                self.hci_port.change_baud_rate(baud_rate)

            if is_hex:
                logging.info('Programming firmware...')
                # Write SS section
                if chip_erase_enable:
                    logging.info("Writing SS section...")
                    ss_bin = io.BytesIO()
                    if intelhex.hex2bin(file_path, ss_bin, start=self.SS_ADDR, size=self.SS_LEN, pad=self.hci_port.FLASH_PAD):
                        raise Exception('Could not create SS binary')
                    self.hci_port.write_ram(self.SS_ADDR, ss_bin, verify=True)

                # Write DS section
                logging.info("Writing DS section...")
                ds_bin = io.BytesIO()
                ds_len = self.FLASH_SIZE-self.SS_LEN
                if intelhex.hex2bin(file_path, ds_bin, start=self.DS_ADDR, size=ds_len, pad=self.hci_port.FLASH_PAD):
                    raise Exception('Could not create DS binary')
                self.hci_port.write_ram(self.DS_ADDR, ds_bin, verify=True)
                self.hci_port.send_launch_ram(self.LAUNCH_FIRMWARE_ADDR)
            else:
                logging.info('Programming HCD file...')
                # read in file_path as binary
                firmware_bin = []
                with open(file_path, 'rb') as f:
                    firmware_bin = f.read()

                data_index = 0
                total_bytes = remaining_bytes = len(firmware_bin)

                while remaining_bytes > 0:
                    payload_len = firmware_bin[data_index + 2]
                    payload_start = data_index + 2 + 1
                    data_len = payload_len + 3
                    cmd_opcode = firmware_bin[data_index + 1]
                    cmd_opcode = cmd_opcode << 8
                    cmd_opcode |= firmware_bin[data_index]
                    logging.debug(f'Write HCD cmd {hex(cmd_opcode)}')
                    (success, payload) = self.hci_port.send_command_wait_response(hci_cmd.CommandPacket(
                        cmd_opcode, firmware_bin[payload_start: (payload_start + payload_len)]))
                    if not success:
                        raise Exception(
                            f'No response for {hex(cmd_opcode)} at index {data_index}')
                    data_index += data_len
                    remaining_bytes -= data_len
                    logging.debug(
                        f'HCD progress: {data_index}/{total_bytes} ({round(data_index/total_bytes*100, 1)}%)')

            logging.info('Finished programming!')
            self.hci_port.close()
