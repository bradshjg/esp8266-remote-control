import uuid

from paho.mqtt.client import Client as MQTTClient

from django.conf import settings


class Controller:
    _client = None
    _client_id = str(uuid.uuid4())
    _topic = settings.MQTT_TOPIC
    _host = settings.MQTT_HOST

    @classmethod
    def _get_client(cls):
        if cls._client is None:
            client = MQTTClient(cls._client_id)
            client.connect(cls._host)
            cls._client = client
        return cls._client

    @classmethod
    def send(cls, message):
        cls._get_client().publish(cls._topic, message)
