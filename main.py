from machine import Pin, PWM
import json
from umqtt.simple import MQTTClient

from config import config


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


pitch = Servo(Pin(config['pin-pitch']))
yaw = Servo(Pin(config['pin-yaw']))
out = Pin(config['pin-out'], Pin.OUT, Pin.PULL_UP, value=0)


def connect_and_subscribe():
    print('connecting to mqtt broker...')
    client = MQTTClient(config['mqtt-client-id'], config['mqtt-host'])
    client.set_callback(on_message)
    client.connect()
    client.subscribe(config['mqtt-topic'])
    while True:
        client.wait_msg()


def on_message(_, msg):
    print('got message...')
    payload = json.loads(msg)

    if 'pitch' in payload:
        pitch.set_angle(payload['pitch'])

    if 'yaw' in payload:
        yaw.set_angle(payload['yaw'])

    if 'out' in payload:
        out.value(payload['out'])


if __name__ == '__main__':
    connect_and_subscribe()
