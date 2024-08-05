import canvas_ble as ble
import gc

advert = None
verbose = False
def wrapped_print(*args, **kwargs):
    if verbose:
        print(*args, **kwargs)

try:
    ble.init()
except:
    pass

try:
    advert.stop()
except:
    pass

connection = None

def cb_con(conn):
    global connection
    connection = conn

def cb_discon(conn):
    global connection
    connection = None

def init_and_start_advert(name, phy) -> bool:
    global advert

    try:
        ble.set_periph_callbacks(cb_con, cb_discon)
        advert = ble.Advertiser()
        advert.stop()
        advert.clear_buffer(False)
        advert.add_ltv(1, bytes([6]), False)
        advert.add_tag_string(ble.AD_TYPE_NAME_COMPLETE, name, False)
        # Advertisemens on the primary ad channels only use the 1M PHY or Coded PHY.
        # Advertisements using 2M PHY require the 1M PHY and extended advertisements.
        phy2 = phy1 = phy
        if phy == ble.PHY_2M:
            phy1 = ble.PHY_1M
        advert.set_phys(phy1, phy2)
        extended = False
        if phy != ble.PHY_1M:
            extended = True
        advert.set_properties(True, False, extended)
        advert.set_interval(240, 250)
        advert.start()
        wrapped_print("advert started")
        return True
    except Exception as e:
        wrapped_print("advert NOT started: ", e)
        return False

def connected() -> bool:
    if connection is not None:
        return True
    else:
        return False

print('Script Completed Successfully')
