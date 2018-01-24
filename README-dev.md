## Running the Bear Speaker

1. Follow the install instructions below, as appropriate for your machine. You can skip the Twilio configuration variables in `.envrc`—Bear doesn't need these.
2. Run `python3 scripts/tts_worker.py`

## Install Instructions

### macOS

Make sure you have a running python3.6.
Earlier versions might work too, but haven't been tested.

Easiest to install [Homebrew](https://brew.sh).

`brew install espeak`

### macOS and Linux

Copy `envrc.template`: `cp envrc.template .envrc`

Edit your credentials and phone number into `.envrc`.

`source .envrc`

Optionally install [direnv](https://direnv.net/)

### All

`pip install -r requirements.txt`

Send a test message (replace the number below by your own phone number):

`python3 scripts/send_sms_message.py +16175551010'

Send a test message to the bear:

`python3 scripts/send_mqtt_message.py "Happy happy"'

## Optional

To use a local RabbitMQ server: `brew install rabbitmq`.
