
import canvas_ble as ble
import time
import gc

try:
    ble.init()
except:
    pass

found = False
found_obj = None
connection = None
verbose = False


def wrapped_print(*args, **kwargs):
    if verbose:
        print(*args, **kwargs)


def scan_cb(evt):
    global found_obj, found
    if found_obj == None:
        found = True
        found_obj = evt


def cb_con(conn):
    global connection
    connection = conn


def cb_discon(conn):
    global connection
    connection = None


scanner = ble.Scanner(scan_cb)

#
# Callbacks cannot be used when running in Raw REPL mode.abs
# Therefore, the following function must be called after the script is loaded.
#


def scan_for_dut(name, phy, duration_seconds=10) -> bool:
    """ Required filter name and required phy are globals set by caller """
    global found, found_obj, required_filter_name, required_phy
    found = False
    found_obj = None
    active = False

    try:
        scanner.stop()
        scanner.filter_reset()
        required_filter_name = name
        required_phy = phy
        scanner.set_phys(required_phy)
        scanner.filter_add(ble.Scanner.FILTER_NAME,
                           required_filter_name.encode())
        if required_phy != ble.PHY_1M:
            active = True
        scanner.start(active)
        wrapped_print('central scan started')
    except:
        wrapped_print('central scan NOT started')
        return False

    while not found and duration_seconds > 0:
        time.sleep_ms(1000)
        duration_seconds -= 1
    scanner.stop()

    return found


def advertisement_found() -> bool:
    return found


def request_connection() -> bool:
    """ found_obj and required_phy come from the previously run script central_scan.py """
    global connection, found_obj, required_phy

    try:
        scanner.stop()
        connection = ble.connect(
            found_obj.addr, required_phy, cb_con, cb_discon)
        wrapped_print('connection started')
        return True
    except Exception as e:
        wrapped_print('connection NOT started: ', e)
        return False


def connected() -> bool:
    if connection is not None:
        return True
    else:
        return False


print('Script Completed Successfully')
