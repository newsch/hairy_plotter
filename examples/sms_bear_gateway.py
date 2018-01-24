import logging
import os
import random
import string
import sys

from twilio.rest import Client
from profanityfilter import ProfanityFilter

sys.path.append(os.path.join(os.path.dirname(__file__), './../scripts'))
from send_mqtt_messages import publish
from receive_mqtt_messages import create_subscription_queue

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('messages')

SEND_TOPIC = 'speak'

ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

assert ACCOUNT_SID, 'Error: the TWILIO_ACCOUNT_SID is not set'
assert AUTH_TOKEN, 'Error: the TWILIO_AUTH_TOKEN is not set'
assert PHONE_NUMBER, 'Error: the TWILIO_PHONE_NUMBER is not set'

PRESET_SPEECHES = [
    "Come to the Holiday Happening!", "Come take a photo with me at the Holiday Happening!",
    "Did you know that the Holiday Happening is this next Monday at 3PM in the library?",
    "I am very sad inside", "Nothing is real.", "Plus one good timing", "Love equals quantum entanglement",
    "Come to the Holiday Happening for cookies, crafts, friendship, and more",
    "Class of 2020 was a mistake", "Keenan Zucker is hot", "Every one of us is a lab rat but we are also the observer",
    "Numbers matter dates matter numbers are not all the same they are very unique",
    "Thanks everyone for coming I'll be here all week I also do birthday parties and bar mitzvahs",
    "Come give me a hug", "What is your name", "Long live poop monkey"]

pf = ProfanityFilter()


def process_message(message):
    from_number = message['From']
    message_body = message['Body']
    print(message, from_number, message_body)

    if pf.is_clean(message_body):
        speech = parse_command(message_body)
        if speech:
            publish(SEND_TOPIC, message=speech)
        response_text = "Come to the Holiday Happening this coming Monday (Dec. 11) at 3PM!"
    else:
        response_text = "Hey! That's not very nice. Keep it clean, kids!"
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    client.api.account.messages.create(
        to=from_number,  # sic
        from_=PHONE_NUMBER,
        body=response_text)


def parse_command(command):
    command = ''.join(c for c in command
                      if ord(c) < 128 and c not in string.punctuation)

    command_list = command.lower().split(maxsplit=2)
    if command_list[0] == 'say':
        return ' '.join(command_list[1:])
    elif command_list[0] == 'speak':
        return random.choice(PRESET_SPEECHES)


def main():
    logger.setLevel(logging.INFO)
    topic = 'incoming-sms-' + PHONE_NUMBER.strip('+')
    logger.info('Waiting for messages on {}'.format(topic))
    for payload in create_subscription_queue(topic):
        process_message(payload)


if __name__ == '__main__':
    main()
