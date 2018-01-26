# Bear-as-a-Service

[![IMAGE ALT TEXT HERE](docs/images/bear-vimeo.jpg)](https://vimeo.com/248514938)

- A Holiday Happening
- [A Life Size Brown Cardboard Bear](https://www.amazon.com/Brown-Bear-Advanced-Graphics-Cardboard/dp/B00B03DT0O)
- Keenan Zucker
- Patrick Huston

## Running the Example

This requires a running bear server.

1. Follow the setup instructions below.
2. Run `python3 examples/sms_bear_gateway.py`
3. Send text

## Install Instructions

Make sure you have a running python 3.6. Earlier versions of Python 3.x might
work too, but haven't been tested. Python 2.x is Right Out.

### macOS and Linux

Copy `envrc.template`: `cp envrc.template .envrc`.

Replace the strings in `.envrc` by your credentials and phone number.

`source .envrc`

Optionally install [direnv](https://direnv.net/)

Now continue with the "All Platforms" instructions.

### Windows

On Windows, set an environment variable from the command line using:

`setx MQTT_URL mqtt://…`

Repeat for each variable in `envrc.template`.

This adds entries to the Windows registry. You only need to do this once.

### All Platforms

`pip3 install -r requirements.txt`

Send a test message (replace the number below by your own phone number):

`python3 scripts/send_sms_message.py +16175551010`

Send a test message to the bear:

`python3 mqtt_json/send_mqtt_message.py "forget about your worries"'

## Acknowledgements

Bear-as-a-Service was adapted from Patrick Huston's Holiday Bear, introduced at
the Olin College December 2017 Holiday Party.

## LICENSE

MIT
