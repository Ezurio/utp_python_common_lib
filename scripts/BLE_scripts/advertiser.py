import canvas_ble as ble

flags = [6]
my_bytes=bytes(flags)
try:
    ble.init()
    advert.stop()
except:
    pass

try:
    advert.stop()
except:
    pass

# Initialise the basic advert
try:
    advert = ble.Advertiser()
    advert.stop()
    advert.clear_buffer(False)
    advert.add_ltv(1, my_bytes, False)
    advert.set_phys(ble.PHY_1M, ble.PHY_1M)
    advert.set_properties(True, True, False)
    advert.set_interval(240, 250)
    print("advert object available")
except Exception as e:
    print(e)
    print("advert object NOT available")
