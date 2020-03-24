import network
import time

from config import config


def wifi_connect():
    station = network.WLAN(network.STA_IF)

    station.active(True)
    station.connect(config['wifi-ssid'], config['wifi-password'])

    while not station.isconnected():
        print('connecting...')
        time.sleep(0.1)


wifi_connect()
