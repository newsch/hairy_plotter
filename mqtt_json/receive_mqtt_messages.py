import json
import logging
import socket
import sys
from queue import Queue

import click
import paho.mqtt.client as mqtt

from .mqtt_config import config

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('messages')


def create_subscription_queue(topic):
    messages = Queue()

    def on_connect(client, userdata, flags, rc):
        logger.info('connected result code=%s', str(rc))
        logger.info('subscribe topic=%s', topic)
        client.subscribe(topic, 0)

    def on_log(client, userdata, level, string):
        logger.info('log %s %s', level, string)

    def on_message(client, userdata, msg):
        logger.info('message topic=%s timestamp=%s payload=%s', msg.topic, msg.timestamp, msg.payload)
        messages.put(msg)

    def on_publish(client, userdata, rc):
        logger.info('published result code=%s', rc)

    def on_disconnect(client, userdata, other):
        logger.info('disconnected result code=%s', other)

    client = mqtt.Client(topic, clean_session=False)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish

    if config.hostname:
        if config.username:
            client.username_pw_set(config.username, config.password)
        try:
            client.connect(config.hostname, 1883, 60)
            client.loop_start()
            logger.info('subscribed to %s', config.hostname)
        except socket.error as err:
            print('MQTT:', err, file=sys.stderr)
            print('Continuing without subscriptions', file=sys.stderr)

    while True:
        payload = json.loads(messages.get().payload.decode('utf-8'))
        payload = {k: v[0] if isinstance(v, list) and len(v) == 1 else v
                   for k, v in payload.items()}
        yield payload


@click.command()
@click.option('--topic', default='speak')
def main(topic):
    logger.setLevel(logging.INFO)
    logger.info('Waiting for messages on {}'.format(topic))
    for payload in create_subscription_queue(topic):
        print(payload)


if __name__ == '__main__':
    main()
