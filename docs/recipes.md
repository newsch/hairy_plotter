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
4. Test it. You can run `python3 scripts/send_mqtt_message.py "forget about your worries"` to
   test.

## Use a local RabbitMQ server

For local development, you may find it useful to run a local RabbitMQ server.

macOS: `brew install rabbitmq` (and then follow the instructions to launch the
daemon, now and on restart).

Add `rabbitmqadmin` to your path. (On macOS: `export
PATH=/usr/local/Cellar/rabbitmq/3.7.2/sbin/:PATH`.) Alternatively, you can
replace `rabbitmqadmin` by `/path/to/rabbitmqadmin` in the instructions below.

Create a queue for speaker messages:

```bash
rabbitmqadmin declare queue name=speak
rabbitmqadmin declare binding source=amq.topic destination_type=queue destination=speak routing_key=speak
```

Note that at the example script assumes a single Twilio server for the Twilio
SMS gateway, and the Bear service. In order to use a local RabbitMQ server, you
will therefore also want to set up your own Twilio → Gateway and run it locally
as described [here](https://github.com/olin-build/twilio-mqtt-gateway).
