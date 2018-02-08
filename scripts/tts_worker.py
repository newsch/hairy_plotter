#!/usr/bin/env python3
import logging
import os
import platform
import subprocess
import sys

import click

sys.path.append(os.path.join(os.path.dirname(__file__), './..'))
import mqtt_json  # noqa: E402

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('speaker')
logger.setLevel(logging.INFO)


SPEECH_COMMAND = 'say' if platform.system() == 'Darwin' else 'espeak'

mqtt_client = mqtt_json.Client()


@click.command()
@click.option('--topic', default='speak')
def main(topic):
    for msg in mqtt_client.create_subscription_queue(topic):
        message = msg['message']
        logger.info(msg)
        res = subprocess.run([SPEECH_COMMAND, message],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            logger.error(res.stderr.decode().strip())


if __name__ == '__main__':
    main()
