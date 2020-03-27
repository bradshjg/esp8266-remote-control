import logging
from machine import ADC, Pin
import json
import time
from umqtt.simple import MQTTClient

from config import config


logger = logging.getLogger(__name__)


class JoyStick:
    sensitivity = 1
    thresholds = {
        0: -3 * sensitivity,
        100: -2 * sensitivity,
        250: -1 * sensitivity,
        400: 0 * sensitivity,
        600: 1 * sensitivity,
        750: 2 * sensitivity,
        900: 3 * sensitivity
    }
    threshold_list = list(thresholds.keys())

    def __init__(self, x_axis_pin, y_axis_pin, button_pin):
        self.x_axis_read = Pin(x_axis_pin, Pin.OUT)
        self.y_axis_read = Pin(y_axis_pin, Pin.OUT)
        self.button_pin = Pin(button_pin, Pin.IN, Pin.PULL_UP)
        self.adc = ADC(0)
        self.axes = (self.x_axis_read, self.y_axis_read)

    def get_deltas(self, values=None):
        if values is None:
            x_value, y_value = self.read_axes()
        else:
            x_value, y_value = values

        x_delta = self.thresholds[self.bin_search_range(x_value, self.threshold_list)]
        y_delta = self.thresholds[self.bin_search_range(y_value, self.threshold_list)]

        return x_delta, y_delta

    def bin_search_range(self, value, thresholds_list):
        if len(thresholds_list) == 1:
            return thresholds_list[0]

        midpoint = len(thresholds_list) // 2
        midpont_value = thresholds_list[midpoint]
        if value > midpont_value:
            return self.bin_search_range(value, thresholds_list[midpoint:])
        elif value < midpont_value:
            return self.bin_search_range(value, thresholds_list[:midpoint])
        else:
            return self.thresholds[midpoint]

    def read_axes(self):
        self.x_axis_read.value(1)
        x_value = self.adc.read()
        self.x_axis_read.value(0)

        self.y_axis_read.value(1)
        y_value = self.adc.read()
        self.y_axis_read.value(0)

        return x_value, y_value

    def read_button(self):
        return self.button_pin.value()

    def log(self):
        axis_values = self.read_axes()
        button_value = self.read_button()
        deltas = self.get_deltas(axis_values)

        logger.info(axis_values)
        logger.info(button_value)
        logger.info(deltas)


class Remote:
    freq = 10

    def __init__(self, joystick, client_id, mqtt_host, mqtt_topic):
        self.joystick = joystick
        self.client_id = client_id
        self.host = mqtt_host
        self.topic = mqtt_topic
        self.client = self.connect()

        self._pitch = 0
        self._yaw = 0
        self._out = 1

    def connect(self):
        client = MQTTClient(self.client_id, self.host)
        client.connect()
        return client

    def publish(self, message_dict):
        message = json.dumps(message_dict)
        self.client.publish(self.topic, message)

    def run(self):
        while True:
            self.publish({'pitch': self._pitch, 'yaw': self._yaw, 'out': self._out})
            time.sleep(1 / self.freq)
            yaw_delta, pitch_delta = self.joystick.get_deltas()
            self._yaw += yaw_delta
            self._pitch += pitch_delta
            self._out = self.joystick.read_button()


if __name__ == '__main__':
    joystick = JoyStick(config['pin-read-x-axis'], config['pin-read-y-axis'], config['pin-button'])
