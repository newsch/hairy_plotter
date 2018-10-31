#!/usr/bin/env python3
import argparse
import io
import logging
import os
import platform
import subprocess
import sys


import str2gcode

# noqa: I003
# Allow this program to even if it's invoked from a current working directory
# different from the project root.
# FIXME Maybe this mode of operation isn't worth it.
sys.path.append(os.path.join(os.path.dirname(__file__), './..'))
import mqtt_json  # noqa: E402,I001

logger = logging.getLogger('print-worker')
logger.setLevel(logging.INFO)


mqtt_client = mqtt_json.Client()

def make_gcode(message, align='center', scale: float = None):
    if scale and scale != str2gcode.FONT_SCALE:
        str2gcode.FONT_SCALE = scale
        str2gcode.calculate_parameters()
    lines = str2gcode.wrap_text(message)
    gcode = str2gcode.lines_to_gcode(lines, align='center')
    return gcode


def make_txt(message):
    completed = subprocess.run(
        ['centerer', '-'],
        input=message.encode('UTF-8'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    logger.debug('Process exited with code {}: {}'.format(
        completed.returncode,
        completed.stderr))
    return completed.stdout


def process_print_message(message, filename='out.gcode'):
    message_text = message['text']

    bytetxt = make_txt(message_text)
    # initial_gcode = make_gcode(message_text)
    # TODO: don't run python from within python
    # completed = subprocess.run(
    #     ['python3','gcodepatcher.py', '-', '-'],
    #     input=initial_gcode.encode('UTF-8'),
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE)
    # logger.debug('Process exited with code {}: {}'.format(
    #     completed.returncode,
    #     completed.stderr))
    with open(filename,'wb') as f:
        # f.write(completed.stdout)
        f.write(bytetxt)

    # TODO: add gcode to print queue


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--topic', default='print')
    args = parser.parse_args()

    TOPIC = args.topic
    logger.info('Listening on topic {!r}'.format(TOPIC))
    counter = 0
    for msg in mqtt_client.create_subscription_queue(TOPIC):
        counter += 1
        filename = 'out{:0=3}.gcode'.format(counter)
        logger.info('Creating file {!r} from message: {}'.format(filename, msg))
        process_print_message(msg, 'print-queue/'+filename)
