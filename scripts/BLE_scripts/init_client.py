import canvas_ble as ble
import time

connection = None
current_state = 0
notify_message = None
indicate_message = None
gatt_client = None
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


def cb_notify(event):
    global notify_message
    notify_message = event.data.decode('utf-8')


def cb_indicate(event):
    global indicate_message
    indicate_message = event.data.decode('utf-8')

def init_client() -> bool:
    global gatt_client

    try:
        ble.init()
    except:
        pass
    
    connection = ble.connect(required_address, required_phy, cb_con, cb_discon)
    count = 10
    while current_state != 1 and count > 0:
        time.sleep_ms(1000)
        count -= 1

    if current_state == 1:
        gatt_client = ble.GattClient(connection)
        gatt_client.discover()
        time.sleep_ms(1000)
        gatt_client.set_name("b8d00001-6329-ef96-8a4d-55b376d8b25a", "WriteChar")
        gatt_client.set_name("b8d00002-6329-ef96-8a4d-55b376d8b25a", "ReadChar")
        gatt_client.set_name(
            "b8d00003-6329-ef96-8a4d-55b376d8b25a", "IndicateChar")
        gatt_client.set_name("b8d00004-6329-ef96-8a4d-55b376d8b25a", "NotifyChar")
        wrapped_print("client ready")
        return True
    else:
        wrapped_print("not connected")
        return False

print('Script Completed Successfully')
