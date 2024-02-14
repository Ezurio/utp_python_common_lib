from enum import Enum
from SerialPort import SerialPort
import ezserial_host_api.ezslib as ez_serial


class SystemCommands:
    @property
    def CMD_PING(self): return "system_ping"
    @property
    def CMD_REBOOT(self): return "system_reboot"
    @property
    def CMD_DUMP(self): return "system_dump"
    @property
    def CMD_STORE_CONFIG(self): return "system_store_config"
    @property
    def CMD_FACTORY_RESET(self): return "system_factory_reset"
    @property
    def CMD_QUERY_FW(self): return "system_query_firmware_version"
    @property
    def CMD_QUERY_UID(self): return "system_query_unique_id"
    @property
    def CMD_QUERY_RANDOM_NUM(self): return "system_query_random_number"
    @property
    def CMD_AES_ENCRYPT(self): return "system_aes_encrypt"
    @property
    def CMD_AES_DECRYPT(self): return "system_aes_decrypt"
    @property
    def CMD_WRITE_USER_DATA(self): return "system_write_user_data"
    @property
    def CMD_READ_USER_DATA(self): return "system_read_user_data"
    @property
    def CMD_SET_BT_ADDR(self): return "system_set_bluetooth_address"
    @property
    def CMD_GET_BT_ADDR(self): return "system_get_bluetooth_address"
    @property
    def CMD_SET_ECO_PARAMS(self): return "system_set_eco_parameters"
    @property
    def CMD_GET_ECO_PARAMS(self): return "system_get_eco_parameters"
    @property
    def CMD_SET_WCO_PARAMS(self): return "system_set_wco_parameters"
    @property
    def CMD_GET_WCO_PARAMS(self): return "system_get_wco_parameters"
    @property
    def CMD_SET_SLEEP_PARAMS(self): return "system_set_sleep_parameters"
    @property
    def CMD_GET_SLEEP_PARAMS(self): return "system_get_sleep_parameters"
    @property
    def CMD_SET_TX_POWER(self): return "system_set_tx_power"
    @property
    def CMD_GET_TX_POWER(self): return "system_get_tx_power"
    @property
    def CMD_SET_TRANSPORT(self): return "system_set_transport"
    @property
    def CMD_GET_TRANSPORT(self): return "system_get_transport"
    @property
    def CMD_SET_UART_PARAMS(self): return "system_set_uart_parameters"
    @property
    def CMD_GET_UART_PARAMS(self): return "system_get_uart_parameters"

    @property
    def EVENT_SYSTEM_BOOT(self): return "system_boot"
    @property
    def EVENT_SYSTEM_ERROR(self): return "system_error"

    @property
    def EVENT_SYSTEM_FACTORY_RESET_COMPLETE(
        self): return "system_factory_reset_complete"

    @property
    def EVENT_SYSTEM_BOOT_FACTORY_TEST_ENTERED(
        self): return "system_factory_test_entered"

    @property
    def EVENT_SYSTEM_BOOT_DUMP_BLOB(self): return "system_dump_blob"


class BluetoothCommands:
    @property
    def CMD_START_INQUIRY(self): return "bt_start_inquiry"
    @property
    def CMD_CANCEL_INQUIRY(self): return "bt_cancel_inquiry"
    @property
    def CMD_QUERY_NAME(self): return "bt_query_name"
    @property
    def CMD_CONNECT(self): return "bt_connect"
    @property
    def CMD_CANCEL_CONNECTION(self): return "bt_cancel_connection"
    @property
    def CMD_DISCONNECT(self): return "bt_disconnect"
    @property
    def CMD_QUERY_CONNECTIONS(self): return "bt_query_connections"
    @property
    def CMD_QUERY_PEER_ADDR(self): return "bt_query_peer_address"
    @property
    def CMD_QUERY_RSSI(self): return "bt_query_rssi"
    @property
    def CMD_SET_DEVICE_CLASS(self): return "bt_set_device_class"
    @property
    def CMD_GET_DEVICE_CLASS(self): return "bt_get_device_class"
    @property
    def CMD_SET_PARAMS(self): return "bt_set_parameters"
    @property
    def CMD_GET_PARAMS(self): return "bt_get_parameters"
    @property
    def EVENT_INQUIRY_RESULT(self): return "bt_inquiry_result"
    @property
    def EVENT_NAME_RESULT(self): return "bt_name_result"
    @property
    def EVENT_INQUIRY_COMPLETE(self): return "bt_inquiry_complete"
    @property
    def EVENT_BT_CONNECTED(self): return "bt_connected"
    @property
    def EVENT_BT_CONN_STATUS(self): return "bt_connection_status"
    @property
    def EVENT_CONN_FAILED(self): return "bt_connection_failed"
    @property
    def EVENT_BT_DISCONNECTED(self): return "bt_disconnected"


class CYSPPCommands:
    @property
    def CMD_P_CYSPP_CHECK(self): return "p_cyspp_check"
    @property
    def CMD_P_CYSPP_START(self): return "p_cyspp_start"
    @property
    def CMD_P_CYSPP_SET_PARAMETERS(self): return "p_cyspp_set_parameters"
    @property
    def CMD_P_CYSPP_GET_PARAMETERS(self): return "p_cyspp_get_parameters"

    @property
    def CMD_P_CYSPP_SET_PACKETIZATION(
        self): return "p_cyspp_set_packetization"

    @property
    def CMD_P_CYSPP_GET_PACKETIZATION(
        self): return "p_cyspp_get_packetization"

    @property
    def EVENT_P_CYSPP_STATUS(self): return "p_cyspp_status"


class SmpCommands:
    @property
    def EVENT_SMP_BOND_ENTRY(self): return "smp_bond_entry"
    @property
    def EVENT_SMP_PAIRING_REQUESTED(self): return "smp_pairing_requested"
    @property
    def EVENT_SMP_PAIRING_RESULT(self): return "smp_pairing_result"
    @property
    def EVENT_SMP_ENCRYPTION_STATUS(self): return "smp_encryption_status"

    @property
    def EVENT_SMP_PASSKEY_DISPLAY_REQUESTED(
        self): return "smp_passkey_display_requested"


class GapCommands:
    @property
    def CMD_GAP_STOP_ADV(self): return "gap_stop_adv"
    @property
    def CMD_GAP_SET_ADV_PARAMETERS(self): return "gap_set_adv_parameters"
    @property
    def CMD_GAP_GET_ADV_PARAMETERS(self): return "gap_get_adv_parameters"
    @property
    def CMD_GAP_SET_ADV_DATA(self): return "gap_set_adv_data"
    @property
    def CMD_GAP_START_ADV(self): return "gap_start_adv"
    @property
    def CMD_GAP_START_SCAN(self): return "gap_start_scan"
    @property
    def EVENT_GAP_SCAN_RESULT(self): return "gap_scan_result"
    @property
    def CMD_GAP_STOP_SCAN(self): return "gap_stop_scan"
    @property
    def CMD_GAP_GET_CONN_PARAMS(self): return "gap_get_conn_parameters"
    @property
    def CMD_GAP_CONNECT(self): return "gap_connect"
    @property
    def EVENT_GAP_CONNECTED(self): return "gap_connected"
    @property
    def EVENT_GAP_CONNECTION_UPDATED(self): return "gap_connection_updated"
    @property
    def EVENT_GAP_ADV_STATE_CHANGED(self): return "gap_adv_state_changed"
    @property
    def EVENT_GAP_SCAN_STATE_CHANGED(self): return "gap_scan_state_changed"


class GattServerCommands:
    @property
    def CMD_GATTS_CREATE_ATTR(self): return "gatts_create_attr"
    @property
    def CMD_GATTS_WRITE_HANDLE(self): return "gatts_write_handle"
    @property
    def CMD_GATTS_NOTIFY_HANDLE(self): return "gatts_notify_handle"
    @property
    def EVENT_GATTS_DATA_WRITTEN(self): return "gatts_data_written"


class GattClientCommands:
    @property
    def CMD_GATTC_READ_HANDLE(self): return "gattc_read_handle"
    @property
    def CMD_GATTC_WRITE_HANDLE(self): return "gattc_write_handle"
    @property
    def EVENT_GATTC_DATA_RECEIVED(self): return "gattc_data_received"
    @property
    def EVENT_GATTC_DISCOVER_RESULT(self): return "gattc_discover_result"

    @property
    def EVENT_GATTC_REMOTE_PROCEDURE_COMPLETE(
        self): return "gattc_remote_procedure_complete"

    @property
    def EVENT_GATTC_WRITE_RESPONSE(self): return "gattc_write_response"


class GpioCommands:
    @property
    def CMD_GPIO_SET_DRIVE(self): return "gpio_set_drive"
    @property
    def CMD_GPIO_SET_LOGIC(self): return "gpio_set_logic"
    @property
    def CMD_GPIO_GET_LOGIC(self): return "gpio_get_logic"


class GapAdvertMode(Enum):
    NA = 0  # TODO: This does not match the user guide


class GapAdvertType(Enum):
    STOP = 0
    DIRECTED_HIGH_DUTY_CYCLE = 1
    DIRECTED_LOW_DUTY_CYCLE = 2
    UNDIRECTED_HIGH_DUTY_CYCLE = 3
    UNDIRECTED_LOW_DUTY_CYCLE = 4
    NON_CONNECTABLE_HIGH_DUTY_CYCLE = 5
    NON_CONNECTABLE_LOW_DUTY_CYCLE = 6
    DISCOVERABLE_HIGH_DUTY_CYCLE = 7
    DISCOVERABLE_LOW_DUTY_CYCLE = 8


class GapAdvertChannels(Enum):
    CHANNEL_37 = 0x01
    CHANNEL_38 = 0x02
    CHANNEL_39 = 0x04
    CHANNEL_ALL = 0x07


class GapAdvertFlags(Enum):
    AUTO_MODE = 0x01    # Enable automatic advertising mode upon boot/disconnection
    CUSTOM_DATA = 0x02  # Use custom advertisement and scan response data
    ALL = 0x03


class GapAddressType(Enum):
    PUBLIC = 0
    RANDOM = 1


class GapScanMode(Enum):
    NA = 1  # TODO: This does not match the user guide


class GapScanFilter(Enum):
    NA = 0


class GattAttrType(Enum):
    STRUCTURE = 0
    VALUE = 1


class GattAttrPermission(Enum):
    VAR_LEN = 0x01
    READ = 0x02
    WRITE_NO_ACK = 0x04
    WRITE_ACK = 0x08
    AUTH_READ = 0x10
    RELIABLE_WRITE = 0x20
    AUTH_WRITE = 0x40


class GattAttrCharProps(Enum):
    BROADCAST = 0x01
    READ = 0x02
    WRITE_NO_RESP = 0x04
    WRITE = 0x08
    NOTIFY = 0x10
    INDICATE = 0x20
    SIGNED_WRITE = 0x40
    EXTENDED_PROPS = 0x80


class EzSerialApiMode(Enum):
    TEXT = 0
    BINARY = 1


class EzSerialPort(SerialPort, SystemCommands, BluetoothCommands,
                   SmpCommands, GapCommands, GattServerCommands,
                   GattClientCommands, GpioCommands, CYSPPCommands):
    """Serial port implementation to communicate with EZ-Serial devices
    """
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    SUCCESS = 0
    ERROR_NO_RESPONSE = -1
    ERROR_RESPONSE = -2
    IF820_DEFAULT_BAUD = 115200

    def __init__(self):
        super().__init__()
        self.ez = None

    def __write_bytes(self, bytes: bytes):
        res = self.send(bytes)
        return (bytes, res)

    def __read_bytes(self, rxtimeout):
        res = self.ez.EZS_INPUT_RESULT_NO_DATA
        byte = None
        block = True
        if rxtimeout == None or rxtimeout == 0:
            block = False
        try:
            bytes_available = len(self._rx_queue)
            if block and bytes_available == 0:
                if not self.wait_for_bytes_received(rxtimeout):
                    return (byte, res)
            byte = self._rx_queue.pop(0)
            if len(self._rx_queue) == 0:
                self.signal_bytes_received()
            res = self.ez.EZS_INPUT_RESULT_BYTE_READ
        except IndexError:
            pass
        return (byte, res)

    def open(self, portName: str, baud: int, ctsrts: bool = False):
        """Open the serial port and init the EZ-Serial API

        Args:
            portName (str): COM port name or device
            baud (int): baud rate
            ctsrts (bool, optional): Use CTS/RTS flow control. Defaults to False.
        """

        self.ez = ez_serial.API(hardwareOutput=self.__write_bytes,
                                hardwareInput=self.__read_bytes)
        super().open(portName, baud, ctsrts)

    def send_and_wait(self, command: str, apiformat: int = None, rxtimeout: int = 1, clear_queue: bool = True, **kwargs) -> tuple:
        """Send command and wait for a response

        Args:
            command (str): Command to send
            apiformat (int, optional): API format to use 0=text, 1=binary. Defaults to None.
            rxtimeout (int, optional): Time to wait for response (in seconds). Defaults to False (Receive immediately).
            clear_queue (bool, optional): Clear the RX queue before sending. Defaults to True.

        Returns:
            tuple: (err code - 0 for success else error, Packet object)
        """
        self.pause_queue_monitor()
        if clear_queue:
            self.clear_rx_queue()
        res = self.ez.sendAndWait(
            command=command, apiformat=apiformat, rxtimeout=rxtimeout, **kwargs)
        if res[0] == None:
            self.resume_queue_monitor()
            return (EzSerialPort.ERROR_NO_RESPONSE, None)
        else:
            error = res[0].payload.get('error', None)
            result = res[0].payload.get('result', None)
            if error:
                self.resume_queue_monitor()
                return (EzSerialPort.ERROR_RESPONSE, None)
            elif result:
                self.resume_queue_monitor()
                return (result, res[0])
            else:
                self.resume_queue_monitor()
                return (EzSerialPort.SUCCESS, res[0])

    def send_cmd(self, command: str, apiformat: int = None, **kwargs):
        """Send command and don't wait for a response

        Args:
            command (str): Command to send
            apiformat (int, optional): API format to use 0=text, 1=binary. Defaults to None.

        Returns:
            none
            """
        self.ez.sendCommand(command=command, apiformat=apiformat, **kwargs)

    def wait_event(self, event: str, rxtimeout: int = 1) -> tuple:
        """Wait for an event to be received

        Args:
            event (str): The event to wait for
            rxtimeout (int, optional): Time to wait for the event. Defaults to False (Don't wait).

        Returns:
            tuple: (err code - 0 for success else error, Packet object)
        """
        self.pause_queue_monitor()
        res = self.ez.waitEvent(event, rxtimeout)
        if res[0] == None:
            self.resume_queue_monitor()
            return (-1, None)
        else:
            self.resume_queue_monitor()
            return (0, res[0])

    def set_api_format(self, api: int):
        """Set API format to use for sending commands

        Args:
            api (int): 0 = TEXT, 1 = BINARY
        """
        self.ez.defaults.apiformat = api
