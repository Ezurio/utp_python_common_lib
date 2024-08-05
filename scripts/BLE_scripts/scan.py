import canvas_ble as ble
import time

found = False
result_obj = None
name_filter_bytes = None
look_for_response = False

try:
    ble.init()
except:
    pass


def normal_cb(evt):
    """ Process adv or response data. """
    global found
    global result_obj
    if found == False:
        result_obj = evt
        found = True
        scanner.stop()


def reponse_cb(evt):
    """ Process scan response data. """
    global found
    global result_obj
    global name_filter_bytes
    if evt.type & ble.Scanner.TYPE_SCAN_RESPONSE:
        if found == False:
            if name_filter_bytes not in evt.data:
                result_obj = evt
                found = True
                scanner.stop()


def scan_cb(evt):
    if look_for_response:
        reponse_cb(evt)
    else:
        normal_cb(evt)


scanner = ble.Scanner(scan_cb)


def set_scan_filter_address(address: str):
    filter_bytes = bytes.fromhex(address)
    scanner.filter_add(ble.Scanner.FILTER_ADDR, filter_bytes)


def set_scan_filter_name(name: str):
    global name_filter_bytes
    name_filter_bytes = bytes(name, 'utf-8')
    scanner.filter_add(ble.Scanner.FILTER_NAME, name_filter_bytes)


def do_scan(duration_seconds, active=False) -> bool:
    global found
    global result_obj
    found = False
    result_obj = None
    scanner.stop()
    scanner.start(active)
    while not found and duration_seconds > 0:
        time.sleep_ms(1000)
        duration_seconds -= 1
    scanner.stop()
    return found


def do_scan_reponse_test(duration_seconds, name) -> bool:
    """ Filter the advertisement data by name, and then filter the scan response 
    data by address.
    """
    global look_for_response

    set_scan_filter_name(name)
    do_scan(duration_seconds)
    if found:
        scanner.stop()
        look_for_response = True
        scanner.filter_reset()
        scanner.filter_add(ble.Scanner.FILTER_ADDR, result_obj.addr)
        do_scan(duration_seconds, True)
        look_for_response = False
    return found


print('scan object available')
