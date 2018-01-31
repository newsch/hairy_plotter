import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from mqtt_json import Client
from unittest.mock import MagicMock, patch


@patch('paho.mqtt.publish.single')
def test_config(publish):
    client = Client()
    client.publish('topic', k1=1, k2=2)
    assert publish.calleds


@patch('paho.mqtt.client.Client')
def test_create_subscription_queue(mqtt_factory):
    # Configure the mock object to send a message to the subscriber.
    def mock_on_loop_start():
        mqtt_client.on_connect(mqtt_client, None, None, None)
        msg = MagicMock()
        msg.payload = '{"key":1}'.encode()
        mqtt_client.on_message(mqtt_client, None, msg)
    mqtt_client = mqtt_factory()
    mqtt_client.loop_start = MagicMock(side_effect=mock_on_loop_start)

    client = Client()
    queue = client.create_subscription_queue('topic')
    msg = next(queue, None)
    assert mqtt_client.connect.called
    assert mqtt_client.subscribe.called
    assert mqtt_client.loop_start.called
    assert msg == {'key': 1}
