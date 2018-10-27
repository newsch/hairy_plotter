import logging
import os
import random
import string
import sys

import twilio.rest
from profanityfilter import ProfanityFilter

sys.path.append(os.path.join(os.path.dirname(__file__), './..'))  # noqa: I003
import mqtt_json  # noqa: E402,I001

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('sms-print-gateway')

SEND_TOPIC = 'print'

ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

FILTER_MESSAGES = os.getenv('FILTER_MESSAGES', True)
if isinstance(FILTER_MESSAGES, str):
    FILTER_MESSAGES = FILTER_MESSAGES.lower() != 'false'


assert ACCOUNT_SID, 'Error: the TWILIO_ACCOUNT_SID is not set'
assert AUTH_TOKEN, 'Error: the TWILIO_AUTH_TOKEN is not set'
assert PHONE_NUMBER, 'Error: the TWILIO_PHONE_NUMBER is not set'

# FIXME REPLY_TEXT isn't used. Find a place for it, or remove it.
REPLY_TEXT = os.getenv('REPLY_TEXT', "Thanks! Your message has been queued to print.")
UNCLEAN_MESSAGE_REPLY_TEXT = "Hey! That's not very nice. Keep it clean, kids!"

pf = ProfanityFilter()

mqtt_client = mqtt_json.Client()


def process_text_message(message, reply_text=None):
    from_number = message['From']
    message_body = message['Body']

    logger.info('Message from {}: {}'.format(from_number, message_body))

    if not FILTER_MESSAGES or pf.is_clean(message_body):
        speech = parse_command(message_body)
        if speech:
            mqtt_client.publish(SEND_TOPIC, message=speech)
        response_text = reply_text
    else:
        logger.info('Blocked unclean message.')
        response_text = UNCLEAN_MESSAGE_REPLY_TEXT
    if response_text:
        twilio_client = twilio.rest.Client(ACCOUNT_SID, AUTH_TOKEN)
        # `to` and `from` are reversed: this message goes *to* the number that
        # the incoming message came *from*.
        twilio_client.api.account.messages.create(
            to=from_number,  # sic — see previous comment
            from_=PHONE_NUMBER,
            body=response_text)
        # logger.info


def parse_command(command):
    """Parse a text command, and returns the text to print."""
    # restrict to ascii
    command = ''.join(c for c in command if c in string.printable)
    return command.upper()


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    topic = 'incoming-sms-' + PHONE_NUMBER.strip('+')
    logger.info('Waiting for messages on {}'.format(topic))
    for payload in mqtt_client.create_subscription_queue(topic):
        process_text_message(payload, reply_text=REPLY_TEXT)
