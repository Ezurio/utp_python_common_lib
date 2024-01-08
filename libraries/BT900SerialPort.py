import logging
from common_lib.CmdSerialPort import CmdSerialPort


class BT900SerialPort(CmdSerialPort):

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    RX_DELIMITER = b'\n00\r'
    CMD_MODE_RX_DELIMITER = b'\r\n>'
    BT900_CMD_QUERY_FW = "ati 3"
    BT900_CMD_QUERY_MAC_ADDR = "ati 4"
    BT900_CMD_MODE = "cmd"
    BT900_CMD_BTC_BOND_DEL = "btc bond delall"
    BT900_CMD_BTC_IOCAP = "btc iocap 0"
    BT900_CMD_BTC_JUST_WORKS = "btc justworks 0"
    BT900_CMD_SET_BTC_PAIRABLE = "btc setpairable 1"
    BT900_CMD_SET_BTC_CONNECTABLE = "btc setconnectable 1"
    BT900_CMD_SET_BTC_DISCOVERABLE = "btc setdiscoverable 1 30"
    BT900_CMD_INQUIRY_CONFIG = "inquiry config 1 2"
    BT900_CMD_INQUIRY_START = "inquiry start 5"
    BT900_CMD_SPP_CONNECT = "spp connect"
    BT900_CMD_SPP_OPEN = "spp open"
    BT900_CMD_BTC_PAIR_RESPONSE = "btc pairresp 1"
    BT900_SPP_WRITE_PREFIX = "spp write 1 "
    BT900_SPP_DISCONNECT = "spp disconnect 1"
    BT900_DISCONNECT = "disconnect 1"
    BT900_EXIT = "exit"
    BT900_PAIR_REQ = "Pair Req:"
    BT900_PAIR_RESULT = "Pair Result:"
    BT900_SPP_CONNECT = "SPP Connect:"
    BT900_SPP_CONNECT_REQ = "spp connect "
    BT900_CYSPP_CONNECT = "connect "
    BT900_GATTC_OPEN = "gattc open 512 0"
    BT900_GATTC_CLOSE = "gattc close"
    BT900_ENABLE_CYSPP_NOT = "gattc write 1 18 0100"
    BT900_CYSPP_WRITE_DATA_STRING = "gattc writecmd$ 1 17 "

    BT900_DEFAULT_BAUD = 115200
    DEFAULT_WAIT_TIME_SEC = 1
    ERROR_DEVICE_TYPE = "Error!  Unknown Device Type."
    OK = "OK"

    def __init__(self):
        super().__init__()
        self.set_rx_delimiter(BT900SerialPort.RX_DELIMITER)
        self.consume_echo(False)

    def open(self, portName: str, baud: int = BT900_DEFAULT_BAUD, rtsCts: bool = False):
        super().open(portName, baud, rtsCts)

    @staticmethod
    def check_bt900_response(response: str, expected_response: str = OK):
        if (expected_response in response):
            logging.info(f"BT900 response = {response}")
        else:
            raise Exception(f"BT900 response error! {response}")

    def __parse_response(self, response: str):
        parse_rsp = {}
        rsp_parts = []
        rsp_parts = response.split("\t")
        if (len(rsp_parts) > 2):
            value_part = rsp_parts[2].split("\r")
            parse_rsp = {"direction": rsp_parts[0].removeprefix("\n"),
                         "msgId": rsp_parts[1].removeprefix("\n"),
                         "val": value_part[0]}
        return parse_rsp

    def get_bt900_fw_ver(self) -> str:
        """Get the firmware version

        Returns:
            str: firmware version
        """
        response = self.send(self.BT900_CMD_QUERY_FW)
        response_parts = self.__parse_response(response)
        fw_ver = response_parts["val"]
        return fw_ver

    def get_bt900_bluetooth_mac(self) -> tuple[str, list[int]]:
        """Get the bluetooth mac address

        Returns:
            tuple[str, list[int]]: mac address in string and list of bytes
        """
        response = self.send(self.BT900_CMD_QUERY_MAC_ADDR)
        response_parts = self.__parse_response(response)
        mac = response_parts["val"]
        mac_parts = mac.split(' ')
        str_mac = mac_parts[1]
        # covert to list-of-bytes
        mac_bytes = bytes.fromhex(str_mac)
        list_bytes_mac = list(mac_bytes)
        return str_mac, list_bytes_mac

    def enter_command_mode(self):
        """Enter command mode
        """
        self.set_rx_delimiter(BT900SerialPort.CMD_MODE_RX_DELIMITER)
        return self.send(self.BT900_CMD_MODE)

    def exit_command_mode(self):
        """Exit command mode
        """
        self.set_rx_delimiter(BT900SerialPort.RX_DELIMITER)
        return self.send(self.BT900_EXIT)
