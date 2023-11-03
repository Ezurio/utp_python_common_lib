import logging
import time
from common_lib.DvkProbe import DvkProbe
from common_lib.HciSerialPort import HciSerialPort
from common_lib.HciProgrammer import HciProgrammer
from common_lib.EzSerialPort import EzSerialPort

ERR_OK = 0
ERR_BOARD_NOT_FOUND = -1


class If820Board(DvkProbe):

    BT_DEV_WAKE = DvkProbe.GPIO_16
    BT_HOST_WAKE = DvkProbe.GPIO_17
    CP_ROLE = DvkProbe.GPIO_18
    CYSPP = DvkProbe.GPIO_19
    LP_MODE = DvkProbe.GPIO_20
    CONNECTION = DvkProbe.GPIO_21
    BOOT_DELAY = 1

    @staticmethod
    def get_board():
        """Helper method to get a single board, or prompt user to select a board
        in the case of multiples.

        Returns:
        Board to connect to.
        """
        board = None
        boards = If820Board.get_connected_boards()
        if len(boards) == 0:
            raise Exception(
                f"Error!  No Boards found.")

        choice = 0
        if len(boards) > 1:
            print("Which board do you want to use?")
            for i, board in enumerate(boards):
                print(f"{i}: {board.probe.id}")
            choice = int(input("Enter the number of the board: "))
        if choice > (len(boards) - 1):
            raise Exception(
                f"Error!  Invalid Board Number.")

        return boards[choice]

    @staticmethod
    def get_connected_boards() -> list['If820Board']:
        """Get a list of all connected boards.

        Returns:
            List: List of IF820 boards
        """
        boards = []
        for probe in DvkProbe.get_connected_probes():
            board = If820Board()
            board._probe = probe
            if not probe.ports[0].location:
                logging.warning(
                    f'No COM port location found for board {probe.id}, assuming HCI port {probe.ports[0].device}')

            board._hci_port_name = probe.ports[0].device
            board._puart_port_name = probe.ports[1].device
            boards.append(board)
        return boards

    @staticmethod
    def get_board_by_com_port(com_port: str):
        """Get a board that uses the specified COM port.

        Returns:
            If820Board: IF820 board or None if not found
        """
        for board in If820Board.get_connected_boards():
            if board.hci_port_name == com_port or board.puart_port_name == com_port:
                return board
        return None

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
        self.probe.open(self.probe.id)
        if (not self.probe.is_open):
            raise Exception(
                f"Unable to open Dvk Probe at {self.probe.id}")

        # reset dvk and module
        res = self.reset_module(wait_for_boot)
        time.sleep(If820Board.BOOT_DELAY)
        self._is_initialized = True
        return res[1]

    def close_ports_and_reset(self, reset_probe: bool = True):
        """Close all UART ports and reset the probe and module

        Args:
            reset_probe (bool, optional): Resetting the probe resets the IO and the module.. Defaults to True.
        """
        if self.hci_uart:
            self.hci_uart.close()
        if self.p_uart:
            self.p_uart.close()
        if self.probe:
            if reset_probe:
                self.probe.reboot()
            self.probe.close()
        self._is_initialized = False

    def __init__(self):
        self._probe = super().__init__()
        self._hci_port_name = ""
        self._puart_port_name = ""
        self._hci_uart = None
        self._p_uart = None
        self._is_initialized = False

    @property
    def probe(self):
        """Pico Probe / Dvk Probe"""
        return self._probe

    @property
    def hci_port_name(self):
        """HCI UART Port Name (i.e. COM10)"""
        return self._hci_port_name

    @property
    def puart_port_name(self):
        """PUART Port Name (i.e. COM10)"""
        return self._puart_port_name

    @property
    def hci_uart(self):
        """HCI UART Port Instance"""
        return self._hci_uart

    @property
    def p_uart(self):
        """PUART Port Instance"""
        return self._p_uart

    @property
    def is_initialized(self):
        return self._is_initialized

    def enter_hci_download_mode(self, port: str = str()) -> int:
        """Put the board into HCI download mode.

        Parameters:
            port (str): Optional: HCI COM port. If not specified (None) and there is more than one
            board is connected, the user will be prompted to select a board.

        Returns:
            int: 0 if successful, negative error code if not successful
        """
        board = self
        if port:
            board_found = self.get_board_by_com_port(port)
            if board_found:
                board = board_found
            else:
                logging.error(f"Board not found with port {port}")
                return ERR_BOARD_NOT_FOUND

        self._hci_uart = HciSerialPort()
        logging.debug(f"Opening HCI port {board.hci_port_name}")
        self.hci_uart.open(board.hci_port_name,
                           HciProgrammer.HCI_DEFAULT_BAUDRATE)
        board.probe.open()
        board.probe.reset_device()
        board.probe.close()
        self.hci_uart.close()
        return ERR_OK

    def flash_firmware(self, minidriver: str, firmware: str, chip_erase: bool = False) -> int:
        res = self.enter_hci_download_mode()
        if res != ERR_OK:
            raise Exception("Failed to enter HCI download mode")

        self.hci_programmer = HciProgrammer(minidriver, self.hci_port_name,
                                            HciProgrammer.HCI_DEFAULT_BAUDRATE, chip_erase)
        self.hci_programmer.program_firmware(
            HciProgrammer.HCI_FLASH_FIRMWARE_BAUDRATE, firmware, chip_erase)
        return ERR_OK

    def cancel_flash_firmware(self):
        self.hci_programmer.hci_port.close()

    def reset_module(self, wait_for_boot: bool = True) -> tuple:
        """Reset the module.

        Args:
            wait_for_boot (bool, optional): Wait for the boot event. Defaults to True.

        Returns:
            tuple: (err code - 0 for success else error, Packet object)
        """
        self.probe.reset_device()
        ez_rsp = (0, None)
        if wait_for_boot:
            ez_rsp = self.p_uart.wait_event(self.p_uart.EVENT_SYSTEM_BOOT)
            If820Board.check_if820_response(
                self.p_uart.EVENT_SYSTEM_BOOT, ez_rsp)
        return ez_rsp

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
