from flask import Flask, request
from twilio.twiml.messaging_response import Message, MessagingResponse
import os
import string
import boto3
import uuid

# Create SQS client
sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-2.amazonaws.com/842599995920/holidaybear.fifo'

app = Flask(__name__)
 
@app.route('/', methods=['POST'])
def sms():
    number = request.form['From']
    message_body = request.form['Body']

    parse_command(number, message_body)

    return send_response()

def send_response():
    response_str = "Come to the Holiday Happening! Monday, December 11!"
    resp = MessagingResponse()
    resp.message(response_str)
    return str(resp)


def parse_command(number, command):
    command_list = command.lower().split()
    if command_list[0] == 'say' and is_clean(number, command):
        queue_message(" ".join(command_list[1:])) 
    elif command_list[0] == 'speak':
        queue_message("Come to the Holiday Happening!")


def is_clean(number, message):
    return True

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
