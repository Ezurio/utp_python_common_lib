import logging
import time
from ifx_firmware_cfg import ifx_firmware_cfg
from dvk_probe import DvkProbe
from HciSerialPort import HciSerialPort
from HciProgrammer import HciProgrammer
from SerialPort import SerialPort

ERR_OK = 0
ERR_BOARD_NOT_FOUND = -1


class IfxBoard(DvkProbe):
    BOOT_DELAY = 1

    @staticmethod
    def get_board():
        """Helper method to get a single board, or prompt user to select a board
        in the case of multiples.

        Returns:
            IfxBoard: Board to connect to.
        """
        boards = IfxBoard.get_connected_boards()
        if len(boards) == 0:
            raise Exception(
                f"Error! No boards found.")

        choice = 0
        if len(boards) > 1:
            print("Which board do you want to use?")
            for i, board in enumerate(boards):
                print(f"{i}: {board.probe.id}")
            choice = int(input("Enter the number of the board: "))
        if choice > (len(boards) - 1):
            raise Exception(
                f"Error! Invalid board number.")

        return boards[choice]

    @staticmethod
    def get_connected_boards() -> list['IfxBoard']:
        """Get a list of all connected boards.

        Returns:
            List: List of IFX boards
        """
        boards = []
        for probe in DvkProbe.get_connected_probes():
            board = IfxBoard(probe)
            boards.append(board)
        return boards

    @staticmethod
    def get_board_by_com_port(com_port: str):
        """Get a board that uses the specified COM port.

        Returns:
            IfxBoard: IFX board or None if not found
        """
        for board in IfxBoard.get_connected_boards():
            if board.hci_port_name == com_port or board.puart_port_name == com_port:
                return board
        return None

    def __init__(self, probe: DvkProbe = None):
        if probe is None:
            self._probe = super().__init__("")
            self._hci_port_name = ""
            self._puart_port_name = ""
        else:
            self._probe = probe
            self._hci_port_name = probe.ports['uart0']
            self._puart_port_name = probe.ports['uart1']

        self._hci_uart = None
        self._p_uart = None
        self._is_initialized = False

    def open_and_init_board(self, wait_for_boot: bool = True):
        """Opens the HCI UART at the default baud rate,
        opens the DvkProbe, and resets the device.

        Args:
            wait_for_boot (bool, optional): Wait for the boot delay. Defaults to True.
        """
        # open HCI port
        if self.hci_uart:
            self.hci_uart.close()
        self._hci_uart = HciSerialPort()
        logging.debug(f"Opening HCI port {self.hci_port_name}")
        self.hci_uart.open(self.hci_port_name,
                           HciProgrammer.HCI_DEFAULT_BAUDRATE)

        # open dvk probe
        logging.info(f"Opening Dvk Probe ID {self.probe.id}")
        self.probe.open()
        if (not self.probe.is_open):
            raise Exception(
                f"Unable to open Dvk Probe at {self.probe.id}")

        # reset dvk and module
        self.reset_module(wait_for_boot)
        self._is_initialized = True

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

    def enter_hci_download_mode(self, fw_cfg: ifx_firmware_cfg, port: str = None) -> int:
        """Put the board into HCI download mode.

        Args:
            fw_cfg (ifx_firmware_cfg): Firmware configuration parameters
            port (str): Optional: HCI COM port. If not specified (None) the existing board port will be used.

        Returns:
            int: 0 if successful, negative error code if not successful
        """
        board = self
        if port:
            board_found = board.get_board_by_com_port(port)
            if board_found:
                board = board_found
            else:
                logging.error(f"Board not found with port {port}")
                return ERR_BOARD_NOT_FOUND

        logging.info(f"Entering HCI download mode on board {board.probe.id}")
        if board.hci_uart:
            board.hci_uart.close()
        board._hci_uart = HciSerialPort()
        logging.debug(f"Opening HCI port {board.hci_port_name}")
        board.hci_uart.open(board.hci_port_name,
                           fw_cfg.hci_default_baudrate)
        board.probe.open()
        board.probe.reset_target()
        board.probe.close()
        board.hci_uart.close()
        return ERR_OK

    def flash_firmware(self, minidriver: str, firmware: str, fw_cfg: ifx_firmware_cfg, chip_erase: bool = False) -> int:
        """Flash firmware to the device over HCI.
        Args:
            minidriver (str): minidriver file path
            firmware (str): firmware file path
            fw_cfg (ifx_firmware_cfg): firmware configuration
            chip_erase (bool, optional): whether to perform chip erase. Defaults to False.
        Returns:
            int: result code
        """
        res = self.enter_hci_download_mode(fw_cfg, None)
        if res != ERR_OK:
            raise Exception("Failed to enter HCI download mode")

        self.hci_programmer = HciProgrammer(minidriver, self.hci_port_name,
                                            fw_cfg.hci_default_baudrate, chip_erase, fw_cfg)
        self.hci_programmer.program_firmware(
            fw_cfg.hci_flash_baudrate, firmware, chip_erase, fw_cfg)
        return ERR_OK

    def cancel_flash_firmware(self):
        if hasattr(self, 'hci_programmer') and self.hci_programmer:
            self.hci_programmer.hci_port.close()

    def reset_module(self, wait_for_boot: bool = True):
        """Reset the module.

        Args:
            wait_for_boot (bool, optional): Wait for the boot event. Defaults to True.
        """
        self.probe.reset_target()
        if wait_for_boot:
            time.sleep(IfxBoard.BOOT_DELAY)

    def reconfig_puart(self, baud: int):
        """Reconfigure the PUART baud rate.

        Args:
            baud (int): Baud rate to set
        """
        if self.p_uart:
            self.p_uart.close()
            self.p_uart.open(
                self.puart_port_name, baud)

    def open_hci_uart_raw(self, baud: int):
        """Open the HCI UART as a raw serial port.

        Args:
            baud (int): Baud rate to set
        """
        if self.hci_uart:
            self.hci_uart.close()
        self._hci_uart = SerialPort()
        self.hci_uart.open(
            self.hci_port_name, baud)
