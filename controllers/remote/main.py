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
    thresholds_list = sorted(list(thresholds.keys()))

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

        x_threshold = self.bin_search_range(x_value, self.thresholds_list)
        y_threshold = self.bin_search_range(y_value, self.thresholds_list)

        x_delta = self.thresholds[x_threshold]
        y_delta = self.thresholds[y_threshold]

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
            return thresholds_list[midpoint]

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


class Remote:
    freq = 5
    bounds = (-45, 45)

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

    def initialize(self):
        self.publish({'pitch': 0, 'yaw': 0, 'out': 1})

    def control_loop(self):
        self.initialize()

        while True:
            yaw_delta, pitch_delta = self.joystick.get_deltas()

            new_yaw = self._yaw + yaw_delta
            if self.bounds[0] <= new_yaw <= self.bounds[1]:
                self._yaw = new_yaw

            new_pitch = self._pitch + pitch_delta
            if self.bounds[0] <= new_pitch <= self.bounds[1]:
                self._pitch = new_pitch
            self._out = self.joystick.read_button()
            msg = {'pitch': self._pitch, 'yaw': self._yaw, 'out': self._out}
            logger.info(msg)
            self.publish(msg)
            time.sleep(1 / self.freq)


if __name__ == '__main__':
    joystick = JoyStick(config['pin-read-x-axis'], config['pin-read-y-axis'], config['pin-button'])
    remote = Remote(joystick, config['mqtt-client-id'], config['mqtt-host'], config['mqtt-topic'])
    remote.control_loop()
