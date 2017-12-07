from flask import Flask, request
from twilio.twiml.messaging_response import Message, MessagingResponse
from profanityfilter import ProfanityFilter
import os
import string
import boto3
import uuid
import random

preset_speak = ["Come to the Holiday Happening!", "Come take a photo with me at the Holiday Happening!",
                "Did you know that the Holiday Happening is this next Monday at 3PM in the library?",
                "I am very sad inside"]

pf = ProfanityFilter()

# Create SQS client
sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-2.amazonaws.com/842599995920/holidaybear.fifo'

app = Flask(__name__)
 
@app.route('/', methods=['POST'])
def sms():
    number = request.form['From']
    message_body = request.form['Body']

    if is_clean(number, message_body):
        parse_command(number, message_body)
        return send_response("Come to the Holiday Happening this coming Monday (Dec. 11) at 3PM!")
    else:
        print "DIRTY DIRTY DIRTY "
        return send_response("Hey! That's not very nice. Keep it clean, kids!")

def send_response(resp_str):
    resp = MessagingResponse()
    resp.message(resp_str)
    return str(resp)


def parse_command(number, command):
    command_list = command.lower().split()
    if command_list[0] == 'say': 
        queue_message(" ".join(command_list[1:])) 
    elif command_list[0] == 'speak':
        queue_message(random.choice(preset_speak))


def is_clean(number, message):
    return pf.is_clean(message)

def queue_message(message):
    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageDeduplicationId=str(uuid.uuid4()),
        MessageGroupId='bearspeak',
        MessageBody=(
            message
        )
    )
    print(response['MessageId'])

 
if __name__ == '__main__':
    app.run(debug=True)
