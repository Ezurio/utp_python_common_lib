
class ifx_firmware_cfg:
    def __init__(self, minidriver_load_addr: int = 0,
                 launch_firmware_addr: int = 0,
                 hci_default_baudrate: int = 115200,
                 hci_flash_baudrate: int = 3000000,
                 load_addr_delay: float = 0.5,
                 chip_erase_delay: float = 5.0):
        self.minidriver_load_addr = minidriver_load_addr
        self.launch_firmware_addr = launch_firmware_addr
        self.hci_default_baudrate = hci_default_baudrate
        self.hci_flash_baudrate = hci_flash_baudrate
        self.load_addr_delay = load_addr_delay
        self.chip_erase_delay = chip_erase_delay
