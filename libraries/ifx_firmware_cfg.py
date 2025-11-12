
class ifx_firmware_cfg:
    def __init__(self, minidriver_load_addr: int = 0,
                 mini_driver_max_size: int = 0,
                 hci_default_baudrate: int = 115200,
                 ss_addr: int = 0,
                 ss_len: int = 0,
                 ds_addr: int = 0,
                 flash_size: int = 0,
                 launch_firmware_addr: int = 0,
                 hci_flash_baudrate: int = 3000000):
        self.minidriver_load_addr = minidriver_load_addr
        self.mini_driver_max_size = mini_driver_max_size
        self.hci_default_baudrate = hci_default_baudrate
        self.ss_addr = ss_addr
        self.ss_len = ss_len
        self.ds_addr = ds_addr
        self.flash_size = flash_size
        self.launch_firmware_addr = launch_firmware_addr
        self.hci_flash_baudrate = hci_flash_baudrate
