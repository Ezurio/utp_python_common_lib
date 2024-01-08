# required_filter_name and required_phy must be set up
# Only run after central_scan.py passes
connection = None
current_state = 0

def cb_con(conn):
    global current_state, connection, rssi
    current_state = 1
    connection = conn

def cb_discon(conn):
    global current_state, connection, rssi
    current_state = 2
    connection = None

scanner.stop()
try:
    connection = ble.connect(found_obj.addr, required_phy, cb_con, cb_discon)
    print('connection started')
except Exception as e:
    print('connection NOT started: ', e)

