# unnamed printer project

A collection of scripts for working with a cnc poster printer.

The sms portion of this leans heavily on work from the Hacking the Library course's
[`bear-as-a-service project`](https://github.com/olinlibrary/bear-as-a-service)

## What's Included in the Box

```
.
├── gcodepatcher.py - patch printer-specific quirks in gcode
├── mqtt_json - library from @osteele for the twilio_mqtt_gateway
│   ├── __init__.py
│   ├── mqtt_config.py
│   ├── receive_mqtt_messages.py
│   └── send_mqtt_messages.py
├── print_worker.py - read from print-text queue and convert to gcode
├── send_sms_message.py - tool to send an sms message through twilio
├── sms_print_gateway.py - process sms queue and send to print-text queue
├── str2gcode.py - tool to convert text into gcode
└── str2svg.py - tool to convert text into svgs
```

## Install

Make sure you have a running Python 3.5. Earlier versions of Python 3.x might
work too, but haven't been tested. Python 2.x is Right Out.

### Dependencies

Install python dependencies with [`pipenv`](https://pipenv.readthedocs.io/en/latest/).
```shell
pipenv install
```

[`str2gcode.py`](str2gcode.py) requires a copy of [`gcodeFont.py`](https://github.com/misan/gcodeFont)

[`sms_print_gateway.py`](sms_print_gateway.py) depends on the
[Twilio ⟶ MQTT Gateway](https://github.com/olin-build/twilio-mqtt-gateway).

### Environment Variables

Copy `env.template` to `.env`. On Linux/macOS: `cp env.template .env`.

Replace the strings in `.env` with your Twilio and MQTT credentials and phone number.

Execute: `source .env` (`pipenv` will also do this automatically whenever you
use `pipenv run` or `pipenv shell`).

### Running

Send a test message. (Replace the number below by your own phone number.)

`python3 send_sms_message.py +16175551010`

Send a test message to the print_worker:

`python3 mqtt_json/send_mqtt_message.py "forget about your worries"`

## Run the services

Provision a RabbitMQ server. Or, use the same server as the Twilio ⟶ MQTT
Gateway.

To process incoming sms messages:
```
python3 sms_print_gateway.py
```

To convert processed sms messages into gcode:
```
python3 print_worker.py`.
```

## LICENSE

MIT
