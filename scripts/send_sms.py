# /usr/bin/env python3
# Modified from https://www.twilio.com/docs/quickstart/python/sms
import re
import os

import click
from twilio.rest import Client

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
phone_number = os.getenv('TWILIO_PHONE_NUMBER')
assert account_sid, 'Error: the TWILIO_ACCOUNT_SID is not set'
assert auth_token, 'Error: the TWILIO_AUTH_TOKEN is not set'
assert phone_number, 'Error: the TWILIO_PHONE_NUMBER is not set'

PHONE_NUMBER_RE = re.compile(r'^\+1\d{10}$')
PHONE_NUMBER_EXAMPLE = '+161723351010'


@click.command()
@click.argument('to_number')  # , help='The SMS destination.')
@click.argument('message_body', default='hello')  # , help='The message body.')
def send_sms(to_number, message_body):
    assert PHONE_NUMBER_RE.match(to_number), 'Phone number must match ' + PHONE_NUMBER_EXAMPLE

    client = Client(account_sid, auth_token)

    client.api.account.messages.create(
        to=to_number,
        from_=phone_number,
        body=message_body)

if __name__ == '__main__':
    send_sms()
