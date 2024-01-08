import canvas_ble as ble

found = False
result_obj = None

try:
    ble.init()
except:
    pass

try:
    scanner.stop()
    scanner.filter_reset()
except:
    pass

def scan_cb(evt):
    global found
    global result_obj
    if found == False:
        result_obj = evt
    found = True

def set_scan_filter_address(address:str):
    global scanner
    filter = bytes.fromhex(address)
    scanner.filter_add(2, filter)

def set_scan_filter_name(name:str):
    global scanner
    filter = bytes(name,'utf-8')
    scanner.filter_add(0, filter)

scanner = ble.Scanner(scan_cb)
scanner.set_phys(ble.PHY_1M)
scanner.set_timing(250, 60)

print('scan object available')
