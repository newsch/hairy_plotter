import os
import sys

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

import sys
sys.path.append('./scripts')
from send_mqtt_messages import publish


app = Flask(__name__)


@app.route('/sms_webhook', methods=['POST'])
def sms_webhook():
    topic = request.form['To'].replace('+', 'incoming-sms-')
    payload = dict(request.form)
    print('publish', payload, 'to', topic)
    publish(topic, **request.form)

    resp = MessagingResponse()
    msg = resp.message("Your message has been relayed.")
    return str(resp)

HOST = '0.0.0.0' if 'PORT' in os.environ else '127.0.0.1'
DEBUG = 'PORT' not in os.environ
PORT = int(os.environ.get('PORT', 5000))
print('Listening on', PORT)
app.run(host=HOST, port=PORT, debug=DEBUG)
