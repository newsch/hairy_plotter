import os
import subprocess
import sys
from unittest.mock import patch

# noqa: I003
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import tts_worker  # noqa: E402,I001,I003


@patch('subprocess.run')
def test_process_speech_message(run):
    # Test an old-style message.
    #
    # Eventually we'll remove this test since `test_upgrade_speech_message`
    # should handle this, but we'll use belt-and-suspenders to avoid breaking
    # clients at first.
    with patch('tts_worker.SPEECH_COMMAND', new='speech-command'):
        tts_worker.process_speech_message(dict(message='Hello world'))
    run.assert_called_with(['speech-command', 'Hello world'],
                           stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE)

    # Test a new-style message.
    with patch('tts_worker.SPEECH_COMMAND', new='speech-command'):
        tts_worker.process_speech_message(dict(message='Hello world'))
    run.assert_called_with(['speech-command', 'Hello world'],
                           stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE)


def test_upgrade_speech_message():
    v0_message = dict(message='Hello world')
    v1_message = dict(version='1', text='Hello world')
    assert tts_worker.upgrade_speech_message(v0_message) == v1_message, \
        "upgrades old-style messages"
    assert tts_worker.upgrade_speech_message(v1_message) == v1_message, \
        "preserves new-style messages"
