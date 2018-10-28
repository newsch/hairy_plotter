#!/usr/bin/env python3
"""Convert strings into gcode."""
import logging
import subprocess
import string
import textwrap


logger = logging.getLogger(__name__)

# DRIVING VALUES
# note: some of these are modified by command-line params at the end of the file
FONT_SCALE = 1.5
FONT_BASE_WIDTH = 19  # in mm
FONT_BASE_HEIGHT = 21  # in mm

SHEET_WIDTH = 800  # in mm
# SHEET_HEIGHT  # roller has no fixed height
LINE_SPACING = 0.5  # in characters
MARGIN = 25

MAX_HEIGHT = 800  # max height of text in document units

# DRIVEN PARAMETERS
global MAX_WIDTH
global CHAR_WIDTH
global CHAR_HEIGHT
global MAX_LINE_LENGTH
global MAX_LINES
global wrapper

def calculate_parameters():
    global MAX_WIDTH
    global CHAR_WIDTH
    global CHAR_HEIGHT
    global MAX_LINE_LENGTH
    global MAX_LINES
    global wrapper

    MAX_WIDTH = SHEET_WIDTH - MARGIN*2  # max width of text in document units
    CHAR_WIDTH = FONT_BASE_WIDTH*FONT_SCALE  # in document units
    CHAR_HEIGHT = FONT_BASE_HEIGHT*FONT_SCALE  # in document units

    MAX_LINE_LENGTH = int(MAX_WIDTH // CHAR_WIDTH)
    MAX_LINES = int((MAX_HEIGHT - CHAR_HEIGHT) // (CHAR_HEIGHT * (1 + LINE_SPACING)) + 1)  # will return negative in edge case where MAX_HEIGHT < CHAR_HEIGHT

    wrapper = textwrap.TextWrapper(width=MAX_LINE_LENGTH)

calculate_parameters()


def wrap_text(text):
    """Wrap an arbitrary string into the document size."""
    lines = []
    for line in text.splitlines():
        for l in wrapper.wrap(line):
            lines.append(l)  # wrap lines at max length
    if len(lines) > MAX_LINES:
        lines = lines[:MAX_LINES]  # trim to max length
        logger.info('Trimmed output to max line number')
    logger.info('Final length: {} lines'.format(len(lines)))
    return lines


def lines_to_gcode(lines: list, align='left'):
    """Convert lines of text into gcode."""
    assert align in ['left', 'right', 'center']

    # calculate sheet dimensions
    # width = max([len(l) for l in lines])*CHAR_WIDTH + 2*MARGIN
    width = SHEET_WIDTH
    height = (1 + (len(lines) - 1)*(1 + LINE_SPACING))*CHAR_HEIGHT + 2*MARGIN

    lines.reverse()  # flip lines for printing (gcode origin is bottom left)
    gcodes = []
    for i, line in enumerate(lines):
        # horizontal alignment
        if align is 'left':
            x = MARGIN
        elif align is 'right':
            x = SHEET_WIDTH - MARGIN - len(line)*CHAR_WIDTH
        elif align is 'center':
            x = MARGIN + (SHEET_WIDTH - 2*MARGIN - len(line)*CHAR_WIDTH)/2

        y = MARGIN + (i*LINE_SPACING + i)*CHAR_HEIGHT
        # y = 400/2 + (i*LINE_SPACING + (i+1))*CHAR_HEIGHT  # for testing
        gcodes.append(gcodefont_wrapper(line, x, y, FONT_SCALE))

    return '\n'.join(gcodes)


def gcodefont_wrapper(text, xoffset=0, yoffset=0, scale=1):
    """Convert a single line of text into gcode using the gcodeFont program."""
    completed = subprocess.run(
        ['java','-classpath', '../gcodeFont', 'Romans',
        text, str(xoffset), str(yoffset), str(scale)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    # log output
    if completed.returncode != 0:
        logger.warning('gcodeFont exited with code {}: {}'.format(
            completed.returncode,
            completed.stderr))
    elif completed.stderr:
        logger.debug('gcodeFont stderr: {}'.format(
            completed.stderr))
        logger.debug('gcodeFont stdout: {}'.format(
            completed.stdout
        ))
    else:
        logger.debug('gcodeFont exited with code {}'.format(
            completed.returncode))

    return completed.stdout.decode('UTF-8')


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='{levelname}:{message}', style='{')

    import argparse
    parser = argparse.ArgumentParser(description='Convert text into svgs sized for the printer')
    parser.add_argument('infile', type=argparse.FileType('r'),
                        help='input file (use `-` for stdin)')
    parser.add_argument('outfile', type=argparse.FileType('w'),
                        help='output file (use `-` for stdout)')
    parser.add_argument('-p', '--plaintext', action='store_true',
                        help='output an ascii representation of the final text instead of gcode')
    parser.add_argument('-a', '--align', type=str,
                        choices=['left','center','right'], default='left',
                        help='horizontal text alignment (default: left)')
    parser.add_argument('-s','--scale', type=float,
                        help='scale factor for the font (default: {})'.format(FONT_SCALE))
    parser.add_argument('-l', '--line-spacing', type=float,
                        help='line spacing in character units (default: {})'.format(LINE_SPACING))
    args = parser.parse_args()

    if args.scale:
        FONT_SCALE = args.scale
    if args.line_spacing:
        LINE_SPACING = args.line_spacing

    calculate_parameters()  # update params with command-line values

    [logging.debug('{}: {}'.format(name, val)) if name == name.upper() else None for name, val in globals().items()]  # print set "constants"

    lines = wrap_text(args.infile.read())
    if not args.plaintext:
        args.outfile.write(lines_to_gcode(lines, align=args.align))
    else:
        fmt_str = '{{:{}{}}}'.format(
            {'left':'<','center':'^','right':'>'}[args.align],
            MAX_LINE_LENGTH)
        [print(fmt_str.format(l)) for l in lines]