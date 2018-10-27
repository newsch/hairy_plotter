#!/usr/bin/env python3
import textwrap

import svgwrite


FONT_SIZE = 20  # in pt

SHEET_WIDTH = 600
# SHEET_HEIGHT  # roller has no fixed height
MARGIN = 50
MAX_WIDTH = SHEET_WIDTH - MARGIN*2  # max width of text in document units
MAX_HEIGHT = 800  # max height of text in document units
CHAR_WIDTH = 10  # in document units
CHAR_HEIGHT = 20  # in document units
LINE_SPACING = 0.25  # in characters

MAX_LINE_LENGTH = MAX_WIDTH // CHAR_WIDTH + 1
MAX_LINES = int((MAX_HEIGHT - CHAR_HEIGHT) // (CHAR_HEIGHT * (1 + LINE_SPACING)) + 1)  # will return negative in edge case where MAX_HEIGHT < CHAR_HEIGHT

wrapper = textwrap.TextWrapper(width=MAX_LINE_LENGTH)

style_str = (
    "text-anchor: middle;"  # center horizontally https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/text-anchor
    "font-family: ubuntu mono;"
    # "font-family: monospace;"  # monospace font for easy calculations
    "font-size: {}pt".format(FONT_SIZE)
)  # https://stackoverflow.com/questions/17127083/python-svgwrite-and-font-styles-sizes

def text_to_svg(text, fileobj):
    lines = []
    for line in text.splitlines():
        for l in wrapper.wrap(line):
            lines.append(l)  # wrap lines at max length
    lines = lines[:MAX_LINES]  # trim to max length

    # calculate sheet dimensions
    # width = max([len(l) for l in lines])*CHAR_WIDTH + 2*MARGIN
    width = SHEET_WIDTH
    height = (1 + (len(lines) - 1)*(1 + LINE_SPACING))*CHAR_HEIGHT + 2*MARGIN
    # dwg = svgwrite.Drawing(size=(width, height))
    dwg = svgwrite.Drawing(size=(width, 400))  # for testing
    g = dwg.g(style=style_str)
    for i, line in enumerate(lines):
        x = SHEET_WIDTH / 2
        # y = MARGIN + (i*LINE_SPACING + (i+1))*CHAR_HEIGHT
        y = 400/2 + (i*LINE_SPACING + (i+1))*CHAR_HEIGHT  # for testing
        g.add(dwg.text(line, insert=(x, y)))
    dwg.add(g)
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