import os
import socket
import sys
from unittest.mock import MagicMock, patch

import pytest

# noqa: I003
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import mqtt_json  # noqa: E402,I001,I003


def make_mqtt_client(connect_error=False):
    # Configure the mock object to send a message to the subscriber.
    def mock_on_loop_start():
        if connect_error:
            raise socket.error('simulated socket error')
        msg = MagicMock()
        msg.payload = '{"key":1}'.encode()
        mqtt_client.on_connect(mqtt_client, None, None, None)
        mqtt_client.on_message(mqtt_client, None, msg)
    mqtt_client = MagicMock()
    mqtt_client.connect = MagicMock()
    mqtt_client.loop_start = MagicMock(side_effect=mock_on_loop_start)
    return mqtt_client


@patch('paho.mqtt.publish.single')
def test_config(publish):
    client = mqtt_json.Client()
    client.publish('topic', k1=1, k2=2)
    assert publish.calleds


def test_create_subscription_queue():
    mqtt_client = make_mqtt_client()
    with patch('paho.mqtt.client.Client', return_value=mqtt_client):
        client = mqtt_json.Client()
        queue = client.create_subscription_queue('topic')
        # Since create_subscription_queue is a generator, its initial code isn't run
        # until the generator's first ("next") value is requested.
        msg = next(queue)
        mqtt_client.connect.assert_called()
        mqtt_client.subscribe.assert_called_with('topic', 0)
        mqtt_client.loop_start.assert_called_with()
        assert msg == {'key': 1}


def test_create_subscription_queue_connection_error():
    mqtt_client = make_mqtt_client(connect_error=True)
    with patch('paho.mqtt.client.Client', return_value=mqtt_client):
        client = mqtt_json.Client()
        with pytest.raises(socket.error):
            queue = client.create_subscription_queue('topic')
            # See the comment in `test_create_subscription_queue`.
            next(queue)
