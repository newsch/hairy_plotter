#!/usr/bin/env python3
import logging
import os

import click
from receive_mqtt_messages import create_subscription_queue

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('speaker')
logger.setLevel(logging.INFO)


@click.command()
@click.option('--topic', default='speak')
def main(topic):
    for msg in create_subscription_queue(topic):
        message = msg['message']
        logger.info(msg)
        os.system("espeak '{}'".format(message))

if __name__ == '__main__':
    main()
