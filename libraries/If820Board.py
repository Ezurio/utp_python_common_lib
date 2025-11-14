import logging
import time
from dvk_probe import DvkProbe
from EzSerialPort import EzSerialPort
from ifx_board import IfxBoard
from ifx_firmware_cfg import ifx_firmware_cfg

IF820_FW_CFG = ifx_firmware_cfg(minidriver_load_addr=0x00270400,
                                launch_firmware_addr=0x00000000,
                                hci_default_baudrate=115200,
                                hci_flash_baudrate=3000000,
                                load_addr_delay=0.5,
                                chip_erase_delay=1.0)


class If820Board(IfxBoard):

    BT_DEV_WAKE = DvkProbe.GPIO_16
    BT_HOST_WAKE = DvkProbe.GPIO_17
    CP_ROLE = DvkProbe.GPIO_18
    CYSPP = DvkProbe.GPIO_19
    LP_MODE = DvkProbe.GPIO_20
    CONNECTION = DvkProbe.GPIO_21

    @staticmethod
    def get_board():
        """Helper method to get a single board, or prompt user to select a board
        in the case of multiples.

        Returns:
        Board to connect to.
        """
        return If820Board(IfxBoard.get_board())

    @staticmethod
    def get_connected_boards() -> list['If820Board']:
        """Get a list of all connected boards.

        Returns:
            List: List of IF820 boards
        """
        boards = []
        for board in IfxBoard.get_connected_boards():
            new_board = If820Board(board)
            boards.append(new_board)
        return boards

    @staticmethod
    def get_board_by_com_port(com_port: str):
        """Get a board that uses the specified COM port.

        Returns:
            If820Board: IF820 board or None if not found
        """
        board = IfxBoard.get_board_by_com_port(com_port)
        if board is None:
            return None
        return If820Board(board)

    @staticmethod
    def check_if820_response(request: str, response):
        if response[0] == 0:
            logging.info(f'{request} Result: {response}')
        else:
            raise Exception(f'{request} Result: {response}')

    @staticmethod
    def if820_mac_addr_response_to_mac_as_string(response) -> str:
        response.reverse()
        str_mac = bytearray(response).hex()
        return str_mac

    def __init__(self, parent: IfxBoard | None = None):
        if parent is None:
            super().__init__()
        else:
            super().__init__(parent.probe)

    def open_and_init_board(self, wait_for_boot: bool = True) -> object | None:
        """Opens the IF820 PUART at the default baud rate,
        opens the DvkProbe, and resets the IF280 Module.

        Args:
            wait_for_boot (bool, optional): Wait for the boot event. Defaults to True.

        Returns:
            object | None: Returns the boot event packet if wait_for_boot is True, else None
        """
        # open ez-serial port
        self._p_uart = EzSerialPort()
        logging.info(f'EZ-Serial Port: {self.puart_port_name}')
        self.p_uart.open(
            self.puart_port_name, self.p_uart.IF820_DEFAULT_BAUD)

        # open dvk probe
        logging.info(f"Opening Dvk Probe ID {self.probe.id}")
        self.probe.open()
        if (not self.probe.is_open):
            raise Exception(
                f"Unable to open Dvk Probe at {self.probe.id}")

        # reset dvk and module
        res = self.reset_module(wait_for_boot)
        time.sleep(If820Board.BOOT_DELAY)
        self._is_initialized = True
        return res[1]

    def reset_module(self, wait_for_boot: bool = True) -> tuple:
        """Reset the module.

        Args:
            wait_for_boot (bool, optional): Wait for the boot event. Defaults to True.

        Returns:
            tuple: (err code - 0 for success else error, Packet object)
        """
        self.probe.reset_target()
        ez_rsp = (0, None)
        if wait_for_boot:
            ez_rsp = self.p_uart.wait_event(self.p_uart.EVENT_SYSTEM_BOOT)
            If820Board.check_if820_response(
                self.p_uart.EVENT_SYSTEM_BOOT, ez_rsp)
        return ez_rsp

    def enter_hci_download_mode(self, fw_cfg: ifx_firmware_cfg = IF820_FW_CFG, port: str = None) -> int:
        """Put the board into HCI download mode.
        Args:
            fw_cfg (ifx_firmware_cfg): Firmware configuration parameters
            port (str): Optional: HCI COM port. If not specified (None) the existing board port will be used.
        Returns:
            int: result code
        """
        return super().enter_hci_download_mode(fw_cfg, port)

    def flash_firmware(self, minidriver: str, firmware: str, fw_cfg: ifx_firmware_cfg = IF820_FW_CFG, chip_erase: bool = False, verify: bool = False) -> int:
        """Flash firmware to the device over HCI.

        Args:
            minidriver (str): minidriver file path
            firmware (str): firmware file path
            fw_cfg (ifx_firmware_cfg, optional): firmware configuration. Defaults to IF820_FW_CFG.
            chip_erase (bool, optional): whether to perform chip erase. Defaults to False.
            verify (bool, optional): verify firmware while flashing with CRC checks. Defaults to False.
        Returns:
            int: result code
        """
        return super().flash_firmware(minidriver, firmware, fw_cfg, chip_erase, verify)
    def stop_advertising(self):
        """Stop BLE advertising.
        """
        cmd = self.p_uart.CMD_GAP_STOP_ADV
        If820Board.check_if820_response(cmd, self.p_uart.send_and_wait(cmd))
        cmd = self.p_uart.EVENT_GAP_ADV_STATE_CHANGED
        If820Board.check_if820_response(cmd, self.p_uart.wait_event(cmd))

    def wait_for_ble_connection(self) -> object:
        """Wait for a BLE connection to be made.

        Returns:
            object: BLE connection event packet
        """
        cmd = self.p_uart.EVENT_GAP_CONNECTED
        res = self.p_uart.wait_event(cmd)
        If820Board.check_if820_response(cmd, res)
        return res[1]
