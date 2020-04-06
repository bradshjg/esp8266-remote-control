import logging
from machine import Pin, PWM
import json
from umqtt.simple import MQTTClient

from config import config


logger = logging.getLogger(__name__)


class Servo:
    freq = 50
    slope = 0.55
    intercept = 75

    def __init__(self, pin):
        self.pin = pin
        self.pwm = PWM(pin, duty=self.get_duty_for_angle(0), freq=self.freq)

    def get_duty_for_angle(self, angle):
        if angle < -45:
            angle = -45
        if angle > 45:
            angle = 45
        return round(angle * self.slope + self.intercept)

    def set_angle(self, angle):
        self.pwm.duty(self.get_duty_for_angle(angle))


class Device:
    PITCH = 'pitch'
    YAW = 'yaw'
    OUT = 'out'

    def __init__(self, pitch_pin, yaw_pin, out_pin):
        self.pitch = Servo(Pin(pitch_pin))
        self.yaw = Servo(Pin(yaw_pin))
        self.out = Pin(out_pin, Pin.OUT, Pin.PULL_UP, value=0)

    def connect_and_subscribe(self, client_id, host, topic):
        logger.info('connecting to mqtt broker...')
        client = MQTTClient(client_id, host)
        client.set_callback(self.on_message)
        client.connect()
        client.subscribe(topic)
        while True:
            client.wait_msg()

    def on_message(self, _, msg):
        logger.info('got message: %s', msg)

        try:
            payload = json.loads(msg)
        except json.JSONDecodeError as e:
            logger.warning(e)
        else:
            for axis in [self.PITCH, self.YAW]:
                if axis in payload:
                    logger.info('setting %s to %s', axis, payload[axis])
                    getattr(self, axis).set_angle(payload[axis])

            if self.OUT in payload:
                logger.info('setting output to %s', payload['out'])
                self.out.value(payload['out'])


if __name__ == '__main__':
    device = Device(config['pin-pitch'], config['pin-yaw'], config['pin-out'])
    device.connect_and_subscribe(config['mqtt-client-id'], config['mqtt-host'], config['mqtt-topic'])
