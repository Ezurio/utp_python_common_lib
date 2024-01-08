import canvas_ble as ble

try:
    ble.init()
except:
     pass

try:
    raw_addr = ble.my_addr()
    string_addr = raw_addr.hex()
    print(string_addr)
except:
    print("Error")
