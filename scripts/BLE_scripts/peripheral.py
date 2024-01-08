# required_name and required_phy must be setup

import canvas_ble as ble
import gc

try:
    ble.init()
except:
    pass

try:
    advert.stop()
except:
    pass

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

# Initialise the basic advert
try:
    ble.set_periph_callbacks(cb_con, cb_discon)
    advert = ble.Advertiser()
    advert.stop()
    advert.clear_buffer(False)
    advert.add_ltv(1, bytes([6]), False)
    advert.add_tag_string(9, required_name, False)
    required_phy1 = required_phy
    if required_phy == ble.PHY_2M:
        required_phy1 = ble.PHY_1M
    advert.set_phys(required_phy1, required_phy)
    active = False
    if required_phy != ble.PHY_1M:
        active = True
    advert.set_properties(True, False, active)
    advert.set_interval(240, 250)
    advert.start()
    print("advert started")
except Exception as e:
    print("advert NOT started: ", e)
