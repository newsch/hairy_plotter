#!/usr/bin/env python3
import logging
import subprocess
import textwrap


logger = logging.getLogger(__name__)


FONT_SCALE = 4
FONT_BASE_WIDTH = 19  # in mm
FONT_BASE_HEIGHT = 21  # in mm

SHEET_WIDTH = 800  # in mm
# SHEET_HEIGHT  # roller has no fixed height
MARGIN = 25
MAX_WIDTH = SHEET_WIDTH - MARGIN*2  # max width of text in document units
MAX_HEIGHT = 800  # max height of text in document units
CHAR_WIDTH = FONT_BASE_WIDTH*FONT_SCALE  # in document units
CHAR_HEIGHT = FONT_BASE_HEIGHT*FONT_SCALE  # in document units
LINE_SPACING = 0.5  # in characters

MAX_LINE_LENGTH = MAX_WIDTH // CHAR_WIDTH
MAX_LINES = int((MAX_HEIGHT - CHAR_HEIGHT) // (CHAR_HEIGHT * (1 + LINE_SPACING)) + 1)  # will return negative in edge case where MAX_HEIGHT < CHAR_HEIGHT

wrapper = textwrap.TextWrapper(width=MAX_LINE_LENGTH)

def text_to_gcode(text, align='left'):
    """Convert an arbitrary string into gcode."""
    lines = []
    for line in text.splitlines():
        for l in wrapper.wrap(line):
            lines.append(l)  # wrap lines at max length
    if len(lines) > MAX_LINES:
        lines = lines[:MAX_LINES]  # trim to max length
        logger.info('Trimmed output to max line number')

    # calculate sheet dimensions
    # width = max([len(l) for l in lines])*CHAR_WIDTH + 2*MARGIN
    width = SHEET_WIDTH
    height = (1 + (len(lines) - 1)*(1 + LINE_SPACING))*CHAR_HEIGHT + 2*MARGIN

    lines.reverse()  # flip lines for printing
    gcodes = []
    for i, line in enumerate(lines):
        x = MARGIN
        y = MARGIN + (i*LINE_SPACING + i)*CHAR_HEIGHT
        # y = 400/2 + (i*LINE_SPACING + (i+1))*CHAR_HEIGHT  # for testing
        gcodes.append(line_to_gcode(line, x, y, FONT_SCALE))

    return '\n'.join(gcodes)

def line_to_gcode(text, xoffset=0, yoffset=0, scale=1):
    """Convert a single line of text into gcode using the gcodeFont program."""
    completed = subprocess.run(
        ['java','-classpath', '../gcodeFont', 'Romans',
        text, str(xoffset), str(yoffset), str(scale)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    # log output
    if completed.returncode != 0:
        logger.warning('gcodeFont process {} exited with code {}: {}'.format(
            completed.PID,
            completed.returncode,
            completed.stderr))
    elif completed.stderr:
        logger.debug('gcodeFont process {} stderr: {}'.format(
            completed.PID,
            completed.stderr))
        logger.debug('gcodeFonr process {} stdout: {}'.format(
            completed.PID,
            completed.stdout
        ))

    return completed.stdout.decode('UTF-8')



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    import argparse
    parser = argparse.ArgumentParser(description='Convert text into svgs sized for the printer')
    parser.add_argument('infile', type=argparse.FileType('r'),
                        help='input file (use `-` for stdin)')
    parser.add_argument('outfile', type=argparse.FileType('w'),
                        help='output file (use `-` for stdout)')
    args = parser.parse_args()

    args.outfile.write(text_to_gcode(args.infile.read()))