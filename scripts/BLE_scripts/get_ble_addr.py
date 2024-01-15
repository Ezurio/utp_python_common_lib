import canvas_ble as ble

try:
    ble.init()
except:
     pass

try:
    raw_addr = ble.my_addr()
    string_addr = ble.addr_to_str(raw_addr)
    print(string_addr)
except:
    print("Error")
