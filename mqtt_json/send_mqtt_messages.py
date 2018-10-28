import json
import logging
import sys

import paho.mqtt.publish as mqtt_publish

from .mqtt_config import config

logger = logging.getLogger('mqtt_json')
logger.setLevel(logging.WARNING)


def publish(topic, **payload):
    logger.info('publish topic=%s payload=%s', topic, payload)
    mqtt_publish.single(topic,
                        payload=json.dumps(payload),
                        qos=1,
                        retain=True,  # keep most recent message and send to new connections
                        hostname=config.hostname,
                        auth=config.auth,
                        port=config.port,
                        client_id='')


def repl(topic):
    while True:
        try:
            message = input('> ')
        except EOFError:
            break
        publish(topic, message=message)


def main(topic='print'):
    # logger.setLevel(logging.INFO)
    if not config.hostname:
        print('At least one of these must be set:',
              ', '.join(config.MQTT_ENV_VARS), file=sys.stderr)
        sys.exit(1)
    if len(sys.argv) > 1:
        message = sys.argv[1]
        publish(topic, message=message)
    else:
        repl(topic)


if __name__ == '__main__':
    main()
