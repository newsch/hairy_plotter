#!/usr/bin/env python3
import argparse
import logging
import os
import platform
import subprocess
import sys

# noqa: I003
# Allow this program to even if it's invoked from a current working directory
# different from the project root.
# FIXME Maybe this mode of operation isn't worth it.
sys.path.append(os.path.join(os.path.dirname(__file__), './..'))
import mqtt_json  # noqa: E402,I001

logger = logging.getLogger('print-worker')
logger.setLevel(logging.INFO)


mqtt_client = mqtt_json.Client()


def process_print_message(message):
    logger.info('New message: {}'.format(message))
    message_text = message['message']

    completed = subprocess.run(
        ['java','-classpath', 'gcodeFont', 'Romans', message_text,
        '0','0','4'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    print('returncode:', completed.returncode)
    print('Errors: {!s}'.format(completed.stderr))
    with open(message_text+'.gcode','wb') as f:
        f.write(completed.stdout)

    # TODO: convert message to svg
    # TODO: convert svg to gcode
    # TODO: add gcode to print queue



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--topic', default='print')
    args = parser.parse_args()

    TOPIC = args.topic
    logging.info('Listening on topic {}'.format(TOPIC))

    for msg in mqtt_client.create_subscription_queue(TOPIC):
        process_print_message(msg)
