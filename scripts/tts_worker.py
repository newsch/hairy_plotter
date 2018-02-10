#!/usr/bin/env python3
import logging
import os
import platform
import subprocess
import sys

import click

# noqa: I003
# Allow this program to even if it's invoked from a current working directory
# different from the project root.
# FIXME Maybe this mode of operation isn't worth it.
sys.path.append(os.path.join(os.path.dirname(__file__), './..'))
import mqtt_json  # noqa: E402,I001

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('speaker')
logger.setLevel(logging.INFO)

# The current speech message version. Messages in this format are dictionaries
# `dict(version='1', text='Hello world')`
SPEECH_MESSAGE_VERSION = '1'

# The command-line program to use for speech synthesis.
DEFAULT_SPEECH_COMMAND = 'say' if platform.system() == 'Darwin' else 'espeak'
SPEECH_COMMAND = os.getenv('BEAR_SPEECH_COMMAND', DEFAULT_SPEECH_COMMAND)

mqtt_client = mqtt_json.Client()


def process_speech_message(message):
    message = upgrade_speech_message(message)
    logger.info(message)
    message_text = message['text']
    res = subprocess.run([SPEECH_COMMAND, message_text],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    if res.returncode != 0:
        logger.error(res.stderr.decode().strip())


def upgrade_speech_message(message):
    """Return a current-version speech message."""
    version = message.get('version')
    if not version:
        text = message['message']
        return dict(version=SPEECH_MESSAGE_VERSION, text=text)
    assert version == SPEECH_MESSAGE_VERSION
    return message


@click.command()
@click.option('--topic', default='speak')
def main(topic):
    for msg in mqtt_client.create_subscription_queue(topic):
        process_speech_message(msg)


if __name__ == '__main__':
    main()
