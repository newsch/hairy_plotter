#!/usr/bin/env python3
# TODO: allow separate pen configs
# TODO: write test cases
# TODO: factor out into gcode generation/parsing and cli for patching
# TODO: factor and create configs for different program output (inkscape, illustrator plugin, gcodefont)
# TODO: fix Regexs for commands with zero-padded numbers (G01 vs G1)
import argparse
import logging
import re

import gcode as g

logger = logging.getLogger(__name__)


FEED_RATE = 20000
ADVANCE = False  # move to end of line and reset axes
MARGIN = 0  # distance to move before next print

# servo positions
PEN_UP = 700
PEN_DOWN = 860
# pauses
PEN_DOWN_PAUSE = 0.4
PEN_UP_PAUSE = 0.1

pens = {
    "magnum": {
        "up_pos": PEN_UP,
        "down_pos": 860,
        "up_pause": PEN_UP_PAUSE,
        "down_pause": PEN_DOWN_PAUSE,
    },
    "regular": {
        "up_pos": PEN_UP,
        "down_pos": 715,
        "up_pause": PEN_UP_PAUSE,
        "down_pause": PEN_DOWN_PAUSE,
    }
}

pen = g.Pen(PEN_UP, PEN_DOWN, PEN_UP_PAUSE, PEN_DOWN_PAUSE)


SPEED_PATTERN = "(-?\d+.?\d*)"  # general regex for getting commands

# match on G0/G1 commands with Z settings
# https://regexr.com/4222s
Z_PATTERN = "(G[01]) ?([\w\d.]*)Z(-?\d+.?\d*)([\w\d.]*)"
Z_COMPILED = re.compile(Z_PATTERN)
Z_LOWER = 0
Z_UPPER = 1

XY_PATTERN = "(G0?[01])[\w\d. ]*([XY]-?\d+.?\d*) ?([XY]-?\d+.?\d*)"
XY_COMPILED = re.compile(XY_PATTERN)

# commands to remove inline
# TODO: (optionally) strip inline comments
STRIP_LIST = [
    re.compile('F'+SPEED_PATTERN),  # feed commands
    # re.compile('G4 ?P\d'),  # pause commands
    re.compile('G[01] ?X0 ?Y0'),  # return home
]


# commands to skip line when reading
# TODO: switch to REGEX or skip/ignore spaces/case
SKIP_LIST = [
    "%",  # program start/end  TODO: start/stop parsing before/after these?
    "M6",  # tool change
    "G4 P",  # pause commands
]


def skip_commands(line):
    """Skip lines if they contain specified commands."""
    for cmd in SKIP_LIST:
        if cmd in line:
            logger.debug(
                "Skipped line {!r} from pattern {!r}".format(line,cmd))
            return []
    return [line]

def strip_commands(line):
    """Remove commands inline using regex."""
    for reg in STRIP_LIST:
        if reg.search(line) is not None:
            logger.debug('Stripped line {!r} w/ pattern {!r}'.format(
                line, reg.pattern))
            line = reg.sub('', line)  # "substitute" w/ empty string
    rem = line.strip().lower()
    if rem == '' or rem == 'g1' or rem == 'g0':
        logger.debug('Removed empty stripped line')
        return []  # return empty if string has no more commands
    else:
        return [line]

def patch_z(line):
    """Replace Z movements with custom tool movements."""
    def z_replace(matchobj):
        """Replace function for match object."""
        cmds = []
        add = lambda a: cmds.append(a)

        code = matchobj.group(1)
        pre = matchobj.group(2)
        zmove = float(matchobj.group(3))
        post = matchobj.group(4)
        if pre.strip() is not '':
            add(code+pre)
        if zmove <= Z_LOWER:
            add('(pen down)')
            add(pen.down())
        elif zmove >= Z_UPPER:
            add('(pen up)')
            add(pen.up())
        if post.strip() is not '':
            add(code+post)
        return '\n'.join(cmds)

    if Z_COMPILED.match(line):
        new_lines = []
        cmds = Z_COMPILED.sub(z_replace, line)
        logger.debug('Replaced z command from line {!r} with {!r}'.format(
            line, cmds))
        for cmd in cmds.splitlines():
            new_lines.append(cmd)
        return new_lines
    else:
        return [line]

PROCESS_ORDER = [  # functions to use and the order to use them in
    skip_commands,
    strip_commands,
    patch_z
]


def get_max_y(lines):
    """Get the max Y coordinate from a file."""
    def split_setting(text):
        """Split strings of the form 'Y-1.23'."""
        axis = text[0]
        val = text[1:]
        if val is '' or val is None:
            val = 0
        else:
            val = float(val)
        return axis, val
    max_y = 0
    for line in lines:
        match = XY_COMPILED.search(line)
        if match is not None:
            cmds = map(split_setting, filter(
                lambda a: a is not None,
                match.groups([2, 3])))
            # import pdb; pdb.set_trace()
            for axis, val in cmds:
                if axis.lower() == 'y' and val > max_y:
                    max_y = val
    return max_y


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('pen', choices=pens.keys(),
        help='pen to use'.format())
    parser.add_argument('infile', type=argparse.FileType('r'),
        help='input file (use `-` for stdin)')
    parser.add_argument('outfile', type=argparse.FileType('w'),
        help='output file (use `-` for stdout)')
    parser.add_argument('-a', '--advance', action='store_true',
        help='reset coordinates after printing, useful for continuous printing')
    parser.add_argument('-m', '--margin', type=float,
        help='y distance to move after print (default is {}, ignored if advance is False)'.format(MARGIN))
    args = parser.parse_args()

    if args.margin is not None:
        MARGIN = args.margin
    if args.advance is not None:
        ADVANCE = args.advance
    if args.pen is not None:
        pen = g.Pen(**pens.get(args.pen))
    # if args.pen_pause is not None and PEN_PAUSE != args.pen_pause:
    #     PEN_PAUSE = args.pen_pause

    # modify gcode
    content = args.infile.read().splitlines()  # gcode as a list where each element is a line
    new_lines = []  # where the new modified code will be put

    for line in content:
        # run through stateless single-line processors
        inputs = [line]
        for step in PROCESS_ORDER:
            for l in inputs:
                outputs = [result for result in step(l)]
            inputs = outputs
        [new_lines.append(output) for output in outputs]

    HEADER = [  # commands to add at the beginning of the file
        "G54",
        g.set_feed(FEED_RATE),
        "G10 L20 P1 X0 Y0 Z0",  # reset work coordinates
        # pendown(),  # DEBUG
        # pause(PEN_DOWN_PAUSE),
        pen.up(),
    ]

    FOOTER = [  # commands to add at the end of the file
        pen.up(),
    ]
    if ADVANCE:
        FOOTER += [
            g.move(0, get_max_y(new_lines)+MARGIN),
            "G10 L20 P1 X0 Y0 Z0",  # reset work coordinates
            # pendown(),  # DEBUG
            # pause(PEN_DOWN_PAUSE),
            # penup()  # DEBUG
            # pause(PEN_UP_PAUSE)
        ]

    new_lines = [
        *HEADER,
        *new_lines,
        *FOOTER
    ]
    logger.info('Writing {} lines of gcode'.format(len(new_lines)))
    args.outfile.write('\n'.join(new_lines)+'\n')
