import logging
from machine import ADC, Pin
import json
import time
from umqtt.simple import MQTTClient

from config import config


logger = logging.getLogger(__name__)


class JoyStick:
    def __init__(self, x_axis_pin, y_axis_pin, button_pin):
        self.x_axis_read = Pin(x_axis_pin, Pin.OUT)
        self.y_axis_read = Pin(y_axis_pin, Pin.OUT)
        self.button_pin = Pin(button_pin, Pin.IN, Pin.PULL_UP)
        self.adc = ADC(0)
        self.axes = (self.x_axis_read, self.y_axis_read)

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
        logger.info(joystick.read_axes())
        logger.info(joystick.read_button())


if __name__ == '__main__':
    joystick = JoyStick(config['pin-read-x-axis'], config['pin-read-y-axis'], config['pin-button'])
