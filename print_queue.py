#!/usr/bin/env python3
import logging
import os
from os.path import isfile, join
import subprocess
import time


logger = logging.getLogger(__name__)


DIR = 'print-queue'
FINISHED_DIR = join(DIR, 'completed')


def print_file(filepath):
    with open(filepath) as f:
        text = f.read()
        centerer = subprocess.run(
            ['centerer', '-'],
            input=text.encode('UTF-8'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        logger.debug("'centerer' process exited with code {}: {}".format(
            centerer.returncode,
            centerer.stderr))
        print_command = subprocess.run(
            ['lp', '-o', 'raw'],
            input=centerer.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        logger.debug("'lp' process exited with code {}: {}".format(
            print_command.returncode,
            print_command.stderr))


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    no_files = False  # flag to stop multiple checks
    while True:
        for folder in [DIR, FINISHED_DIR]:
            if not os.path.exists(folder):
                os.makedirs(folder)

        files_to_print = [f for f in os.listdir(DIR) if isfile(join(DIR, f))]

        if len(files_to_print) == 0 and not no_files:
            logger.info('Found no more files to print')
            no_files = True
        else:
            for filename in files_to_print:
                cur_file = join(DIR, filename)
                logger.info('Printing {!r}'.format(cur_file))
                print_file(cur_file)
                logger.info('Finished printing {!r}'.format(cur_file))
                os.rename(cur_file, join(FINISHED_DIR, os.path.basename(cur_file)))  # move to finished directory
        time.sleep(2)
