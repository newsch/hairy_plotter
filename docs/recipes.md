# Development Recipes

## Run the Bear Service

This runs your own Bear Service for local development, or testing the Bear
Service itself. You don't need this if you're connecting to a running Bear
Service.

1. Follow the install instructions above, as appropriate for your machine. You
   can skip the Twilio configuration variables in `.envrc`—Bear doesn't need
   these.
2. Install *espeak*:
    * macOS: `brew install espeak`
    * Linux: `sudo apt-get install espeak`
3. Run `python3 scripts/tts_worker.py`
4. Test it. You can run `python3 scripts/send_mqtt_message.py "Happy happy"` to
   test.

## Run a local Twilio Gateway

These instructions are for use with a local development Twilio gateway. You
don't need this if you're connecting to the public gateway.

1. Go to the Twilio phone number configuration page, e.g. https://www.twilio.com/console/phone-numbers/{sid}.
2. Under "Messaging: A Message Comes In", set the webhook to the server URL
   followed by the `/sms_webhook` path, e.g.
   `https://c115d7a2.ngrok.io/sms_webhook`.

## Use a local MQTT server

For local development, you may find it useful to run a local RabbitMQ server.

macOS: `brew install rabbitmq` (and then follow the instructions to launch the
daemon, now and on restart).

Add `rabbitmqadmin` to your path. (On macOS: `export
PATH=/usr/local/Cellar/rabbitmq/3.7.2/sbin/:PATH`.) Alternatively, you can
replace `rabbitmqadmin` by `/path/to/rabbitmqadmin` in the instructions below.

Create queues for the speaker and for your phone number:

```bash
rabbitmqadmin declare queue name=speak
rabbitmqadmin declare binding source=amq.topic destination_type=queue destination=speak routing_key=speak

rabbitmqadmin declare queue name=incoming-sms-16175551010
rabbitmqadmin declare binding source=amq.topic destination_type=queue destination=incoming-sms-16175551010 routing_key=incoming-sms-16175551010
```
