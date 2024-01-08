# required_filter_name and required_phy must be set up

import canvas_ble as ble
import time
import gc

try:
    ble.init()
except:
    pass

try:
    scanner.stop()
    scanner.filter_reset()
except:
    pass

filter = bytes(required_filter_name,'utf-8')
found = False
found_obj = None

def scan_cb(evt):
    global found_obj, found
    if found_obj == None:
        found = True
        found_obj = evt

scanner = ble.Scanner(scan_cb)
scanner.set_phys(required_phy)
scanner.set_timing(250, 60)
scanner.filter_add(0, filter)
active = False
if required_phy != ble.PHY_1M:
    active = True
try:
    scanner.start(active)
    print('central scan started')
except:
    print('central scan NOT started')

