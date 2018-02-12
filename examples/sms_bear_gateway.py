import logging
import os
import random
import string
import sys

import click
import twilio.rest
from profanityfilter import ProfanityFilter

sys.path.append(os.path.join(os.path.dirname(__file__), './..'))  # noqa: I003
import mqtt_json  # noqa: E402,I001

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('sms-bear-gateway')

SEND_TOPIC = 'speak'

ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

assert ACCOUNT_SID, 'Error: the TWILIO_ACCOUNT_SID is not set'
assert AUTH_TOKEN, 'Error: the TWILIO_AUTH_TOKEN is not set'
assert PHONE_NUMBER, 'Error: the TWILIO_PHONE_NUMBER is not set'

# FIXME REPLY_TEXT isn't used. Find a place for it, or remove it.
REPLY_TEXT = os.getenv('BEAR_REPLY_TEXT', "The bear has received your message.")
UNCLEAN_MESSAGE_REPLY_TEXT = "Hey! That's not very nice. Keep it clean, kids!"

CANNED_SPEECHES = [
    "Come to the Holiday Happening!",
    "Come take a photo with me at the Holiday Happening!",
    "Did you know that the Holiday Happening is this next Monday at 3PM in the library?",
    "I am very sad inside",
    "Nothing is real.",
    "Plus one good timing",
    "Love equals quantum entanglement",
    "Come to the Holiday Happening for cookies, crafts, friendship, and more",
    "Class of 2020 was a mistake",
    "Keenan Zucker is hot",
    "Every one of us is a lab rat but we are also the observer",
    "Numbers matter dates matter numbers are not all the same they are very unique",
    "Thanks everyone for coming I'll be here all week I also do birthday parties and bar mitzvahs",
    "Come give me a hug",
    "What is your name",
    "Long live poop monkey",
]

pf = ProfanityFilter()

mqtt_client = mqtt_json.Client()


def process_text_message(message, reply_text=None):
    from_number = message['From']
    message_body = message['Body']

    if pf.is_clean(message_body):
        speech = parse_command(message_body)
        if speech:
            mqtt_client.publish(SEND_TOPIC, message=speech)
        response_text = reply_text
    else:
        response_text = UNCLEAN_MESSAGE_REPLY_TEXT
    if response_text:
        twilio_client = twilio.rest.Client(ACCOUNT_SID, AUTH_TOKEN)
        # `to` and `from` are reversed: this message goes *to* the number that
        # the incoming message came *from*.
        twilio_client.api.account.messages.create(
            to=from_number,  # sic — see previous comment
            from_=PHONE_NUMBER,
            body=response_text)


def parse_command(command):
    """Parse a possible text command, and returns the text to speak.

    * 'say' -> speak a canned speech
    * 'say something' -> speak the words after 'say'
    * 'speak' or 'speak something' -> 'speak' is the same as 'say'
    * anything else -> speak the anything else
    """
    # remove 8-bit characters
    # FIXME if the intent is to remove non-ASCII, it should remove < 32 too
    # TODO probably the worker should do this instead, since it's connected
    # to the synthesizer and knows whether the synthesizer can handle accents
    # and other non-ASCII
    command = ''.join(c for c in command
                      if ord(c) < 128 and c not in string.punctuation)

    words = command.lower().split(maxsplit=2)
    if words[0] in ('speak', 'say'):
        if words[1:]:
            return ' '.join(words[1:])
        else:
            return random.choice(CANNED_SPEECHES)
    else:
        # TODO probably the worker should do this instead. Some synthesizers
        # might be able to do meaningful things with case.
        return command.lower()


@click.command()
@click.option('--reply-text', default='Bear has spoken')
def main(reply_text=None):
    logger.setLevel(logging.INFO)
    topic = 'incoming-sms-' + PHONE_NUMBER.strip('+')
    logger.info('Waiting for messages on {}'.format(topic))
    for payload in mqtt_client.create_subscription_queue(topic):
        process_text_message(payload, reply_text=reply_text)


if __name__ == '__main__':
    main()
