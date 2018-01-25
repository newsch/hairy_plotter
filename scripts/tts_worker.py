#!/usr/bin/env python3
import logging
import platform
import subprocess

import click
from receive_mqtt_messages import create_subscription_queue

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('speaker')
logger.setLevel(logging.INFO)


SPEECH_COMMAND = 'say' if platform.system() == 'Darwin' else 'espeak'


@click.command()
@click.option('--topic', default='speak')
def main(topic):
    for msg in create_subscription_queue(topic):
        message = msg['message']
        logger.info(msg)
        res = subprocess.run([SPEECH_COMMAND, message],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            logger.error(res.stderr.decode().strip())

if __name__ == '__main__':
    main()
