import canvas_ble as ble
import gc

connection = None
current_state = 0

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
    "Service 1":{
        "Name": "TestService",
        "UUID":"b8d00000-6329-ef96-8a4d-55b376d8b25a",
        "Characteristic 1":{
            "Name": "WriteChar",
            "UUID" :"b8d00001-6329-ef96-8a4d-55b376d8b25a",
            "Length" : 20,
            "Read Encryption" : "None",
            "Write Encryption" : "None",
            "Capability" : "Write",
            "Callback" : write_cb
        },
        "Characteristic 2":{
            "Name": "ReadChar",
            "UUID" :"b8d00002-6329-ef96-8a4d-55b376d8b25a",
            "Length" : 20,
            "Read Encryption" : "None",
            "Write Encryption" : "None",
            "Capability" : "Read"
        },
        "Characteristic 3":{
            "Name": "IndicateChar",
            "UUID" :"b8d00003-6329-ef96-8a4d-55b376d8b25a",
            "Length" : 20,
            "Read Encryption" : "None",
            "Write Encryption" : "None",
            "Capability" : "Indicate",
            "Callback" : cb_indicate
        },
        "Characteristic 4":{
            "Name": "NotifyChar",
            "UUID" :"b8d00004-6329-ef96-8a4d-55b376d8b25a",
            "Length" : 20,
            "Read Encryption" : "None",
            "Write Encryption" : "None",
            "Capability" : "Notify",
            "Callback" : cb_notify
        }
    }
}


try:
    ble.init()
except:
    pass

# Initialise the basic advert
# 'required_' values must be set by the robot test before calling this script.
try:
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
    print("advert NOT started: ", e)

try:
    global gatt_server
    gatt_server = ble.GattServer()
    gatt_server.build_from_dict(db)
    gatt_server.start()
    print("server ready")
except Exception as e:
    print("Gatt Server failed: ", e)

