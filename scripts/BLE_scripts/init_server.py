import canvas_ble as ble
from canvas_ble import UUID
import gc

connection = None
current_state = 0
do_notify = None
do_indicate = None
indicate_ack = None
gatt_server = None
verbose = False


def wrapped_print(*args, **kwargs):
    if verbose:
        print(*args, **kwargs)


def cb_con(conn):
    global current_state, connection
    current_state = 1
    connection = conn


def cb_discon(conn):
    global current_state, connection
    current_state = 2
    connection = None


def write_cb(event):
    if event.type == ble.GattServer.EVENT_ATTR_VALUE:
        global write_value
        write_value = event.data.decode()


def cb_notify(event_object):
    global do_notify
    if event_object.type == ble.GattServer.EVENT_CCCD_NONE:
        do_notify = False
    if event_object.type == ble.GattServer.EVENT_CCCD_NOTIFY:
        do_notify = True


def cb_indicate(event_object):
    global do_indicate
    global indicate_ack
    if event_object.type == ble.GattServer.EVENT_CCCD_NONE:
        do_indicate = False
    if event_object.type == ble.GattServer.EVENT_CCCD_INDICATE:
        do_indicate = True
    if event_object.type == ble.GattServer.EVENT_INDICATION_OK:
        indicate_ack = True
    if event_object.type == ble.GattServer.EVENT_INDICATION_TIMEOUT:
        event_object.connection.disconnect()


# Start the gatt server
db = {
    UUID('b8d00000-6329-ef96-8a4d-55b376d8b25a'): {
        UUID('b8d00001-6329-ef96-8a4d-55b376d8b25a'): {
            'name': 'WriteChar',
            'flags': ble.GattServer.FLAG_WRITE_NO_ACK,
            'length': 20,
            'callback': write_cb
        },
        UUID('b8d00002-6329-ef96-8a4d-55b376d8b25a'): {
            'name': 'ReadChar',
            'flags': ble.GattServer.FLAG_READ,
            'length': 20,
        },
        UUID('b8d00003-6329-ef96-8a4d-55b376d8b25a'): {
            'name': 'IndicateChar',
            'flags': ble.GattServer.FLAG_INDICATE,
            'length': 20,
            'callback': cb_indicate
        },
        UUID('b8d00004-6329-ef96-8a4d-55b376d8b25a'): {
            'name': 'NotifyChar',
            'flags': ble.GattServer.FLAG_NOTIFY,
            'length': 20,
            'callback': cb_notify
        }
    }
}


def init_server() -> bool:
    """ Initialise the basic advert and the Gatt Server.
    'required_' values must be set by the robot test before calling this script.
    """
    global gatt_server

    try:
        ble.init()
        ble.set_periph_callbacks(cb_con, cb_discon)
        advert = ble.Advertiser()
        advert.stop()
        advert.clear_buffer(False)
        advert.add_ltv(1, bytes([6]), False)
        advert.add_tag_string(9, required_name, False)
        advert.set_phys(required_phy1, required_phy2)
        advert.set_properties(True, False, required_extended)
        advert.set_interval(240, 250)
        advert.start()
    except Exception as e:
        wrapped_print("advert NOT started: ", e)
        return False

    try:
        gatt_server = ble.GattServer()
        gatt_server.build_from_dict(db)
        gatt_server.start()
        wrapped_print("server ready")
    except Exception as e:
        wrapped_print("Gatt Server failed: ", e)
        return False

    return True


print('Script Completed Successfully')
