import intelhex
import io
import logging
import HciSerialPort as hci
import hci.command as hci_cmd
from ifx_firmware_cfg import ifx_firmware_cfg


class HciProgrammer():
    """HCI Programmer class to program firmware via HCI UART interface.
    This class works with Infineon based chipsets.
    """

    HCI_DEFAULT_BAUDRATE = 115200

    def __init__(self,
                 mini_driver: str = '',
                 port: str = '',
                 baud_rate: int = 0,
                 chip_erase: bool = False,
                 fw_cfg: ifx_firmware_cfg = None):
        self.mini_driver_path = mini_driver
        self.hci_port = hci.HciSerialPort()
        self.com_port = port
        self.baud_rate = baud_rate
        self.chip_erase_enable = chip_erase
        self.fw_cfg = fw_cfg

    def __load_mini_driver(self):
        """Loads the mini driver into RAM to provide chip erase, change baud and CRC functions

        Raises:
            Exception: raise exception on error
        """
        self.hci_port.send_hci_reset()
        self.hci_port.send_download_minidriver()
        minidriver_bin = io.BytesIO()
        if intelhex.hex2bin(self.mini_driver_path,
                            minidriver_bin,
                            start=self.fw_cfg.minidriver_load_addr,
                            size=self.fw_cfg.mini_driver_max_size,
                            pad=self.hci_port.RAM_PAD):
            raise Exception('Could not convert minidriver to binary')
        self.hci_port.write_ram(self.fw_cfg.minidriver_load_addr,
                                minidriver_bin, self.hci_port.RAM_PAD)
        self.hci_port.send_launch_ram(self.fw_cfg.minidriver_load_addr)
        pass

    def init(self,
             mini_driver: str,
             port: str,
             baud_rate: int,
             chip_erase: bool = False,
             fw_cfg: ifx_firmware_cfg = None):
        self.__init__(mini_driver, port, baud_rate, chip_erase, fw_cfg)

    def open_com_init_mini_driver(self):
        self.hci_port.open(self.com_port, self.baud_rate)
        self.__load_mini_driver()

    def chip_erase(self):
        """Erase entire flash contents
        """
        logging.info('Performing chip erase...')
        self.hci_port.send_chip_erase()
        logging.info('Chip erase finished')

    def program_firmware(self,
                         baud_rate: int = HCI_DEFAULT_BAUDRATE,
                         file_path: str | None = None,
                         chip_erase_enable: bool = False,
                         fw_cfg: ifx_firmware_cfg = None):
        """Program the firmware file

        Args:
            baud_rate (int): Baud rate to program the firmware at
            file_path (str): Path to firmware file (hex or hcd)
            chip_erase_enable (bool): Enable chip erase before programming
            fw_cfg (ifx_firmware_cfg): Firmware configuration parameters

        Raises:
            Exception: raise exception on error
        """

        if fw_cfg is None and self.fw_cfg is None:
            raise Exception("Firmware configuration not provided")

        if fw_cfg is not None:
            self.fw_cfg = fw_cfg

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
                    if intelhex.hex2bin(file_path,
                                        ss_bin,
                                        start=self.fw_cfg.ss_addr,
                                        size=self.fw_cfg.ss_len,
                                        pad=self.hci_port.FLASH_PAD):
                        raise Exception('Could not create SS binary')
                    self.hci_port.write_ram(
                        self.fw_cfg.ss_addr, ss_bin, verify=True)

                # Write DS section
                logging.info("Writing DS section...")
                ds_bin = io.BytesIO()
                ds_len = self.fw_cfg.flash_size - self.fw_cfg.ss_len
                if intelhex.hex2bin(file_path,
                                    ds_bin,
                                    start=self.fw_cfg.ds_addr,
                                    size=ds_len,
                                    pad=self.hci_port.FLASH_PAD):
                    raise Exception('Could not create DS binary')
                self.hci_port.write_ram(
                    self.fw_cfg.ds_addr, ds_bin, verify=True)
                self.hci_port.send_launch_ram(self.fw_cfg.launch_firmware_addr)
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
