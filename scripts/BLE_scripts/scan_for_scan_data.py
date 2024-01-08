# must set filter_name up first with: filter_name = "C01e47f8f7d60c7" for example

import canvas_ble as ble
import time

state = 0
found = False
interim_obj = None
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

filter = bytes(filter_name,'utf-8')

def scan_cb(evt):
    global found
    global interim_obj
    global state
    global result_obj
    global filter
    if state == 0:
        interim_obj = evt
        state = 1
    elif state == 1:
        if found == False:
            if filter not in evt.data:
                result_obj = evt
                found = True

scanner = ble.Scanner(scan_cb)
scanner.set_phys(ble.PHY_1M)
scanner.set_timing(250, 60)
scanner.filter_add(0, filter)
scanner.start(1)

while state == 0:
    time.sleep_ms(10)

scanner.stop()
scanner.filter_reset()
scanner.filter_add(2, interim_obj.addr)
scanner.start(1)

print('scan object available')

