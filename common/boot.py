import network
import time
import upip

from config import config

PACKAGES = ['micropython-logging']


def setup_logging():
    import logging
    logging.basicConfig(level=logging.INFO)


def wifi_connect():
    station = network.WLAN(network.STA_IF)

    station.active(True)
    station.connect(config['wifi-ssid'], config['wifi-password'])

    while not station.isconnected():
        time.sleep(0.1)


wifi_connect()

for package in PACKAGES:
    upip.install(package)

setup_logging()
