# Hairy Plotter

A collection of scripts and services for working with a cnc poster printer, including:
- printing from sms messages
- converting text into svg and gcode files
- fixing gcode output from various programs to meet the printer's somewhat unusual expectations

The sms portion of this leans heavily on work from the Hacking the Library course's
[`bear-as-a-service project`](https://github.com/olinlibrary/bear-as-a-service).

## What's Included in the Box

```
.
├── gcodepatcher.py - patch printer-specific quirks in gcode
├── mqtt_json - wrapper library from @osteele for interfacing with the mqtt broker
│   ├── __init__.py
│   ├── mqtt_config.py
│   ├── receive_mqtt_messages.py
│   └── send_mqtt_messages.py
├── print_worker.py - read from print-text queue and convert to gcode
├── print_queue.py - print files (text or gcode) from a folder
├── send_sms_message.py - tool to send an sms message through twilio
├── simple_stream.py - GRBL example script to stream gcode
├── sms_print_gateway.py - process sms queue and send to print-text queue
├── str2gcode.py - tool to convert text into gcode
├── str2svg.py - tool to convert text into svgs
└── stream.py - modified GRBL script to stream gcode
```

## Install

Make sure you have a running Python 3.5. Earlier versions of Python 3.x might
work too, but haven't been tested. Python 2.x is Right Out.

### Dependencies

Install python dependencies with [`pipenv`](https://pipenv.readthedocs.io/en/latest/).
```shell
pipenv install
```

[`str2gcode.py`](str2gcode.py) requires a copy of [`gcodeFont`](https://github.com/misan/gcodeFont).

[`sms_print_gateway.py`](sms_print_gateway.py) depends on the
[`twilio-mqtt-gateway`](https://github.com/olin-build/twilio-mqtt-gateway).

### Environment Variables

Copy `env.template` to `.env`. On Linux/macOS: `cp env.template .env`.

Replace the strings in `.env` with your Twilio and MQTT credentials and phone number.

Execute: `source .env` (`pipenv` will also do this automatically whenever you
use `pipenv run` or `pipenv shell`).

### Running the scripts

> Note: most of these scripts support more command-line options. You can learn
> more about them with `python3 <scriptname> -h` (and, of course, by reading the
> source code)

> Note: by marking the scripts as executable with `chmod +x <scriptname>`, you
> can call them with `./<scriptname>` instead of `python3 <scriptname>`

Generate an svg from text:

`echo -e "Hello\nWorld" | python3 str2svg.py - out.svg`

Generate gcode from text:

`echo -e "Hello\nWorld" | python3 str2gcode.py - out.gcode`

Patch the gcode (printer-specific):

`python3 gcodepatcher.py out.gcode out-patched.gcode`

Send a test sms message (replace the number below by your own phone number):

`python3 send_sms_message.py +16175551010`

Send a test message directly to the `print_worker.py` queue:

`python3 mqtt_json/send_mqtt_messages.py "forget about your worries"`

### Running the services

Provision a RabbitMQ server. Or, use the same server as the `twilio-mqtt-gateway`.

To process incoming sms messages:
```
python3 sms_print_gateway.py
```

To convert processed sms messages into gcode:
```
python3 print_worker.py
```

## CAM solutions

- [Diego Monzon's G-Code Illustrator plugin](https://diegomonzon.com/illustrator-to-gcode/)
- [PyCAM](https://github.com/SebKuzminsky/pycam) (I have yet to get this working)
- `cam.py` - script from an MIT prof, Neil Gershenfeld [this is the latest version I found on the Wayback Machine](https://web.archive.org/web/20110829105018/http://web.media.mit.edu/~neilg/fab/dist/cam.py)
- [`Fab Modules`](https://github.com/FabModules/fabmodules-html5), a similar project from the same person.

- [cncjs](https://cnc.js.org/)
- [Universal G-Code Sender](https://github.com/winder/Universal-G-Code-Sender)
- more options on [the GRBL wiki](https://github.com/gnea/grbl/wiki/Using-Grbl#how-to-stream-g-code-programs-to-grbl)

## LICENSE

MIT
