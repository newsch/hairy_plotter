import os
import subprocess
import sys
from unittest.mock import patch

# noqa: I003
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import tts_worker  # noqa: E402,I001,I003


@patch('subprocess.run')
def test_process_speech_message(run):
    with patch('tts_worker.SPEECH_COMMAND', new='speech-command'):
        tts_worker.process_speech_message(dict(message='Hello world'))
    run.assert_called_with(['speech-command', 'Hello world'],
                           stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE)
