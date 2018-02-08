"""A wrapper for MQTT, with JSON payloads and an API that I find easier."""

from .send_mqtt_messages import publish
from .receive_mqtt_messages import create_subscription_queue


class Client(object):

    def publish(self, *args, **kwargs):
        return publish(*args, **kwargs)

    def create_subscription_queue(self, *args, **kwargs):
        return create_subscription_queue(*args, **kwargs)
