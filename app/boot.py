# This file is executed on every boot (including wake-boot from deepsleep)
# Pull counter: 2
#import esp
#import webrepl
#esp.osdebug(None)
#import webrepl
#webrepl.start()
import webrepl
import ujson
import time
import network


def read_config():
    with open('config.json', 'r') as f:
        config = ujson.load(f)
    return config

def do_connect(ssid, password):
    print("debug in do connect")
    # setup interface
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    wlan.active(True)
    wlan.config(reconnects=3)

    # attempt to connect
    wlan.connect(ssid, password)

    # wait for timeout or connect successfull
    timeout = 10
    start_time = time.time()
    while not wlan.isconnected() and (time.time() - start_time) < timeout:
        time.sleep(1)
    
    if wlan.isconnected():
        print("Connected to Wlan")
        print(wlan.ifconfig())
    else:
        print(wlan.ifconfig())
        raise Exception("Failed to Connect after specified recconect attempts")

def do_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(ssid='lampe')
    ap.config(max_clients=3)
    print("ap would now!!")

def main():
    # Read the config
    config = read_config()
    wifi_config = config.get('wifi', {})

    # get wifi creds for normal connecting
    ssid = wifi_config.get('ssid')
    password = wifi_config.get('password')

    try:
        print("debug pre do connect")
        print("Data:", ssid, password)
        do_connect(ssid, password)
    except Exception as e:
        print("Failed to Connect to wifi:",ssid)
        print("\nError:", e)
        do_ap()
        
    webrepl.start()

if __name__ == "__main__":
    main()
