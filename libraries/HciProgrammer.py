import os
import intelhex
import logging
import struct

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

    def __load_hex_file(self,
                        file_path: str,
                        max_packet_size: int = hci.HciSerialPort.WRITE_RAM_MAX_SIZE) -> list[tuple[int, bytes]]:
        """Loads an Intel HEX file and splits it into packets for writing to memory

        Args:
            file_path (str): hex file path
            max_packet_size (int, optional): Maximum size of each packet. Defaults to hci.HciSerialPort.WRITE_RAM_MAX_SIZE.

        Returns:
            list[tuple[int, bytes]]: List of tuples containing address and data packets
        """

        ih = intelhex.IntelHex(file_path)
        packets = []  # list of (start_address, bytes)

        # Each (start, end) defines a contiguous address segment
        for seg_start, seg_end in ih.segments():  # seg_end is exclusive
            buf = bytearray(ih.tobinarray(start=seg_start, end=seg_end-1))

            # Slice into packets of up to 240 bytes — no padding
            for offset in range(0, len(buf), max_packet_size):
                chunk = bytes(buf[offset:offset + max_packet_size])
                packets.append((seg_start + offset, chunk))

        return packets

    def __load_mini_driver(self):
        """Loads the mini driver into RAM to provide chip erase, change baud and CRC functions

        Raises:
            Exception: raise exception on error
        """
        self.hci_port.send_hci_reset()
        self.hci_port.send_download_minidriver()
        hex_packets = self.__load_hex_file(self.mini_driver_path)
        self.hci_port.write_ram(hex_packets)
        self.hci_port.send_launch_ram(
            self.fw_cfg.minidriver_load_addr, delay=self.fw_cfg.load_addr_delay)
        pass

    def init(self,
             mini_driver: str,
             port: str,
             baud_rate: int,
             chip_erase: bool = False,
             fw_cfg: ifx_firmware_cfg = None):
        self.__init__(mini_driver, port, baud_rate, chip_erase, fw_cfg)

    def open_com_init_mini_driver(self):
        """Open the HCI port and load the mini driver
        """
        self.hci_port.open(self.com_port, self.baud_rate)
        self.__load_mini_driver()

    def open_com_init(self):
        """Open the HCI port and send HCI reset
        """
        self.hci_port.open(self.com_port, self.baud_rate)
        self.hci_port.send_hci_reset()

    def chip_erase(self):
        """Erase entire flash contents
        """
        logging.info('Performing chip erase...')
        self.hci_port.send_chip_erase(timeout=self.fw_cfg.chip_erase_delay)
        logging.info('Chip erase finished')

    def program_firmware(self,
                         baud_rate: int = HCI_DEFAULT_BAUDRATE,
                         file_path: str | None = None,
                         chip_erase_enable: bool = False,
                         fw_cfg: ifx_firmware_cfg = None,
                         verify: bool = False):
        """Program the firmware file

        Args:
            baud_rate (int): Baud rate to program the firmware at
            file_path (str): Path to firmware file (hex or hcd)
            chip_erase_enable (bool): Enable chip erase before programming
            fw_cfg (ifx_firmware_cfg): Firmware configuration parameters
            verify (bool): Verify firmware while flashing with CRC checks

        Raises:
            Exception: raise exception on error
        """

        if fw_cfg is None and self.fw_cfg is None:
            raise Exception("Firmware configuration not provided")

        if fw_cfg is not None:
            self.fw_cfg = fw_cfg

        if file_path:
            # Check if file exists
            if not os.path.isfile(file_path):
                raise Exception(f'Firmware file not found: {file_path}')

            is_hex = False
            # Get file extension from path
            file_ext = file_path.split('.')[-1].casefold()
            if file_ext == 'hex':
                is_hex = True
            elif file_ext != 'hcd':
                raise Exception('Invalid file extension, must be .hex or .hcd')

        minidriver_loaded = False
        if chip_erase_enable or file_path:
            if is_hex:
                logging.info('Loading minidriver...')
                self.open_com_init_mini_driver()
                minidriver_loaded = True
            else:
                logging.info(
                    'Skipping minidriver, is .hcd file. Opening HCI port...')
                self.open_com_init()
        else:
            logging.info('No firmware or chip erase specified, exiting')
            return

        if chip_erase_enable:
            if minidriver_loaded:
                self.chip_erase()
            else:
                logging.warning(
                    'Chip erase requested but mini driver not loaded, skipping chip erase')

        if file_path:
            if baud_rate != self.HCI_DEFAULT_BAUDRATE and minidriver_loaded:
                logging.info(f'Changing baud to {baud_rate}')
                self.hci_port.change_baud_rate(baud_rate)

            if is_hex:
                hex_packets = self.__load_hex_file(file_path)
                total_bytes = sum(len(data) for addr, data in hex_packets)
                logging.info(f'Programming firmware... ({total_bytes} bytes)')
                self.hci_port.write_ram(hex_packets, verify=verify)
                self.hci_port.send_launch_ram(
                    self.fw_cfg.launch_firmware_addr, delay=self.fw_cfg.load_addr_delay)
            else:
                logging.info('Programming HCD file...')
                if verify:
                    logging.warning('Verify option ignored for HCD files')
                # Read in file_path as binary
                # HCD file format is a series of HCI commands to be sent to the device
                firmware_bin = []
                with open(file_path, 'rb') as f:
                    firmware_bin = f.read()

                data_index = 0
                total_bytes = remaining_bytes = len(firmware_bin)

                while remaining_bytes > 0:
                    # Each HCD command packet starts with a 3-byte header:
                    #   2 bytes: opcode (little-endian)
                    #   1 byte: payload length
                    # followed by payload_len bytes of payload data
                    header_format = '<HB'
                    header_size = struct.calcsize(header_format)
                    cmd_opcode, payload_len = struct.unpack_from(
                        header_format, firmware_bin, data_index)
                    payload_start = data_index + header_size
                    data_len = payload_len + header_size
                    opcode_str = f'0x{cmd_opcode:04X}'
                    logging.debug(f'Write HCD cmd {opcode_str}')
                    (success, payload) = self.hci_port.send_command_wait_response(hci_cmd.CommandPacket(
                        cmd_opcode, firmware_bin[payload_start: (payload_start + payload_len)]))
                    if not success:
                        raise Exception(
                            f'No response for {opcode_str} at index {data_index}')
                    data_index += data_len
                    remaining_bytes -= data_len
                    logging.debug(
                        f'HCD progress: {data_index}/{total_bytes} ({round(data_index/total_bytes*100, 1)}%)')

            logging.info('Finished programming!')
            self.hci_port.close()
