#!/usr/bin/env python3
import textwrap

import svgwrite


SHEET_WIDTH = 300
# SHEET_HEIGHT  # roller has no fixed height
MARGIN = 50
MAX_WIDTH = SHEET_WIDTH - MARGIN*2  # max width of text in document units
MAX_HEIGHT = 800  # max height of text in document units
CHAR_WIDTH = 2  # in document units
CHAR_HEIGHT = 2  # in document units
LINE_SPACING = 1  # in characters

MAX_LINE_LENGTH = MAX_WIDTH // CHAR_WIDTH + 1
MAX_LINES = (MAX_HEIGHT - CHAR_HEIGHT) // (CHAR_HEIGHT * (1 + LINE_SPACING)) + 1  # will return negative in edge case where MAX_HEIGHT < CHAR_HEIGHT

wrapper = textwrap.TextWrapper(width=MAX_LINE_LENGTH)

style_dict = {
    "text-anchor": "middle",  # center text horizontally
    "font-family": "monospace"
}

def text_to_svg(text, fileobj):
    # create array of original lines, wrapped at max length and trimmed to max length
    lines = []
    for line in text.splitlines():
        lines.append(*wrapper.wrap(line))
    lines = lines[:MAX_LINES]

    # calculate sheet dimensions
    width = SHEET_WIDTH
    height = (1 + (len(lines) - 1)*(1 + LINE_SPACING))*CHAR_HEIGHT
    # dwg = svgwrite.Drawing(size=(width, height))
    dwg = svgwrite.Drawing(size=(width, 400))
    for i, line in enumerate(lines):
        x = SHEET_WIDTH / 2
        # y = i*LINE_SPACING + (i+1)*CHAR_HEIGHT
        y = 400/2 + i*LINE_SPACING + (i+1)*CHAR_HEIGHT
        text = dwg.add(dwg.text(line, insert=(x, y)))
    dwg.write(fileobj)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Convert text into svgs sized for the printer')
    parser.add_argument('infile', type=argparse.FileType('r'),
                        help='input file (use `-` for stdin)')
    parser.add_argument('outfile', type=argparse.FileType('w'),
                        help='output file (use `-` for stdout)')
    args = parser.parse_args()
    text_to_svg(args.infile.read(), args.outfile)