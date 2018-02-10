import os
import sys
from unittest.mock import patch
# noqa: I003

os.environ['TWILIO_ACCOUNT_SID'] = '--test-account-id--'
os.environ['TWILIO_AUTH_TOKEN'] = '--test-auth-token--'
os.environ['TWILIO_PHONE_NUMBER'] = '--test-phone-number--'
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'examples'))
import sms_bear_gateway  # noqa: E402,I001,I003


@patch('random.choice', return_value='random response')
def test_parse_command(random_choice):
    # canned responses
    assert sms_bear_gateway.parse_command('say') == 'random response'
    assert sms_bear_gateway.parse_command('speak') == 'random response'
    # verbatim
    assert sms_bear_gateway.parse_command('say hello') == 'hello'
    assert sms_bear_gateway.parse_command('speak hello') == 'hello'
    # downcases test
    assert sms_bear_gateway.parse_command('speak Hello') == 'hello'
    # removes punctuation
    assert sms_bear_gateway.parse_command('speak Hello, world!') == 'hello world'
    # removes non-ASCII characters
    assert sms_bear_gateway.parse_command('say Héllo') == 'hllo'


@patch('twilio.rest.Client')
@patch('sms_bear_gateway.pf.is_clean', wraps=lambda s: 'profanity' not in s)
@patch('sms_bear_gateway.mqtt_client')
def test_process_text_message(mqtt_client, profanity_filter, twilio_client):
    def mock_message(text):
        """Create a mock Twilio message from a text string."""
        return dict(From='+16175552323', Body=text)

    def process_text_message_with(text, reply_text=None):
        """Call process_text_message.

        The `text` value is wrapped in a Twilio message.
        This function resets the mocks before making the call.
        """
        mqtt_client.reset_mock()
        twilio_client.reset_mock()
        sms_bear_gateway.process_text_message(mock_message(text),
                                              reply_text=reply_text)

    # publishes the message
    process_text_message_with('say hello')
    mqtt_client.publish.assert_called_with('speak', message='hello')

    # sends a response message when reply_text is specified
    process_text_message_with('say hello', reply_text='Got your message')
    twilio_client.api.account.messages.create.assert_not_called()

    # doesn't respond when reply_text isn't specified
    process_text_message_with('say hello')
    twilio_client.api.account.messages.create.assert_not_called()

    # handles profanity
    process_text_message_with('say profanity')
    mqtt_client.publish.assert_not_called()
    twilio_client.api.account.messages.create.assert_not_called()
