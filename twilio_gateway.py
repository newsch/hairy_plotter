import logging
import os
import sys

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

import sys
sys.path.append('./scripts')
from send_mqtt_messages import publish

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('messages')

HOST = '0.0.0.0' if 'PORT' in os.environ else '127.0.0.1'
PORT = int(os.environ.get('PORT', 5000))
DEBUG = 'PORT' not in os.environ
RESPONSE_TEXT = os.environ.get('RESPONSE_TEXT')

app = Flask(__name__)


@app.route('/sms_webhook', methods=['POST'])
def sms_webhook():
    topic = request.form['To'].replace('+', 'incoming-sms-')
    payload = dict(request.form)
    logger.info('publish {} to {}'.format(payload, topic))
    publish(topic, **request.form)

    resp = MessagingResponse()
    if RESPONSE_TEXT:
        msg = resp.message(RESPONSE_TEXT)
    return str(resp)

logger.setLevel(logging.INFO)
logger.info('Listening on {}'.format(PORT))
app.run(host=HOST, port=PORT, debug=DEBUG)
