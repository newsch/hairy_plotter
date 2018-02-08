# /usr/bin/env python3
# Modified from https://www.twilio.com/docs/quickstart/python/sms
import re
import os

import click
from twilio.rest import Client

ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
assert ACCOUNT_SID, 'Error: the TWILIO_ACCOUNT_SID is not set'
assert AUTH_TOKEN, 'Error: the TWILIO_AUTH_TOKEN is not set'
assert PHONE_NUMBER, 'Error: the TWILIO_PHONE_NUMBER is not set'

PHONE_NUMBER_RE = re.compile(r'^\+1\d{10}$')
PHONE_NUMBER_EXAMPLE = '+161723351010'


@click.command()
@click.argument('to_number')
@click.argument('message_body', default='hello')
def send_sms_message(to_number, message_body):
    assert PHONE_NUMBER_RE.match(to_number), 'Phone number must match ' + PHONE_NUMBER_EXAMPLE
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    client.api.account.messages.create(
        to=to_number,
        from_=PHONE_NUMBER,
        body=message_body)


if __name__ == '__main__':
    send_sms_message()
