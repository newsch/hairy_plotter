#!/usr/bin/env python3
"""Fix gcode files to conform to plotter and GRBL needs.
TODO: write test cases
TODO: factor out into gcode generation/parsing and cli for patching
TODO: factor and create configs for different program output (inkscape, illustrator plugin, gcodefont)
TODO: fix Regexs for commands with zero-padded numbers (G01 vs G1)
TODO: figure out oddities of scale/patch_z interaction
TODO: spec out switching to a stateful char-by-char patcher ala GRBL
"""
import argparse
import logging
import re
import os

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

PEN_LEVEL = 500  # level position for pens (the pair on the servo is level)
PEN_SPEED = 900 / 0.7  # vertical speed for pen, PWM steps / seconds, used for calculating pauses

def get_pause(position, level_position=PEN_LEVEL, speed=PEN_SPEED):
    """Calculate the time for the pen to travel a distance."""
    return abs(position - level_position) / speed

pens = {
    "magnum": {
        # "up_pos": PEN_LEVEL,
        "down_pos": 750,
        # "up_pause": get_pause,
        # "down_pause": PEN_DOWN_PAUSE,
    },
    "regular": {
        # "up_pos": PEN_LEVEL,
        "down_pos": 710,
        # "up_pause": PEN_UP_PAUSE,
        # "down_pause": PEN_DOWN_PAUSE,
    },
    "sakura": {
        "down_pos": 200
    }
}

pen = g.Pen(PEN_UP, PEN_DOWN, PEN_UP_PAUSE, PEN_DOWN_PAUSE)


SPEED_PATTERN = "(-?\d+.?\d*)"  # general regex for getting commands

# match on G0/G1 commands with Z settings
# https://regexr.com/4222s
Z_PATTERN = "([Gg]0?[01]) ?([\w\d.]*)Z(-?\d+.?\d*)([\w\d.]*)"
Z_COMPILED = re.compile(Z_PATTERN)
Z_LOWER = 0
Z_UPPER = 1

# https://regexr.com/4222s
# Group 1: G command, e.g. "G1", "g 00"
# Group 2: G
# Group 3: 0 or 1
# Groups 4-12: 3 sets of axis-value pairs:
#  axis-value pair group 1: full command, e.g. "X 123.456"
#  axis-value pair group 2: axis, e.g. "X", "y"
#  axis-value pair group 3: value, e.g. "1", "123", "123.456"
XYZ_PATTERN = "(([Gg]) *0?([01])) *(([XxYyZz]) *(-?\d+.?\d*)) *(([XxYyZz]) *(-?\d+.?\d*))? *(([XxYyZz]) *(-?\d+.?\d*))?"
XYZ_COMPILED = re.compile(XYZ_PATTERN)

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
    # "G4 P",  # pause commands
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


def scale(line: str, x_scale: float, y_scale: float, z_scale: float) -> g.CmdList:
    """Scale the x and y axes of G0 and G1 commands.

    >>> scale("g01 X7.5 Y100", 2, 3)
    ['G1 X15.00 Y300.00']
    """
    match = XYZ_COMPILED.match(line.lstrip())
    if match is None:
        return [line]
    
    coordinates = {'x': None, 'y': None, 'z': None}

    for string, a, v in (match.group(*range(i, i+3)) for i in range(4, 12, 3)):
        if string is not None:
            axis = a.lower()
            value = float(v)
            if axis == 'x':
                coordinates['x'] = value * x_scale
            elif axis == 'y':
                coordinates['y'] = value * y_scale
            elif axis == 'z':
                coordinates['z'] = value * z_scale
    move_type = int(match.group(3))
    if move_type == 0:
        cmd = g.move_rapid(**coordinates)
    elif move_type == 1:
        cmd = g.move(**coordinates)
    else:
        raise ValueError("Couldn't match G command: {!r}".format(line))
    logger.debug("Scaled line {!r} by ({}, {}, {}) to {!r}".format(line, x_scale, y_scale, z_scale, cmd))
    return [cmd]


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
    logging.basicConfig(level=logging.DEBUG)

    import argparse
    parser = argparse.ArgumentParser()
    pen_group = parser.add_mutually_exclusive_group(required=True);
    pen_group.add_argument('-p', '--pen', type=str, choices=pens.keys(),
        help='pen preset to use'.format())
    pen_group.add_argument('-d', '--down-pos', type=int, help='Manually set a down position')
    parser.add_argument('infile', type=str,
        help='input file')
    parser.add_argument('out', type=str,
        help='output path')
    parser.add_argument('-a', '--advance', action='store_true',
        help='reset coordinates after printing, useful for continuous printing')
    parser.add_argument('-m', '--margin', type=float,
        help='y distance to move after print (default is {}, ignored if advance is False)'.format(MARGIN))
    parser.add_argument('-s', '--scale', type=float, help="Scale gcode coordinates")
    parser.add_argument('-f', '--feed', type=int, help="Set feed rate")
    args = parser.parse_args()

    # deal with in and out paths
    # Use infile name if out is a directory, ala `mv`, but replace extension
    infile = args.infile
    if not os.path.exists(infile):
        parser.error("file does not exist")
    infile_name, infile_ext = os.path.splitext(os.path.split(infile)[1])

    out = args.out
    if os.path.isdir(out):
        # if a directory is given, use the input filename and extension
        outpath = out
        outfile_ext = infile_ext
        outfile_name = infile_name
        outfile = os.path.join(outpath, outfile_name + outfile_ext)
    else:
        outfile = out
        outfile_name, outfile_ext = os.path.splitext(outfile)

    if args.margin is not None:
        MARGIN = args.margin
    if args.advance is not None:
        ADVANCE = args.advance
    if args.feed is not None:
        FEED_RATE = args.feed

    # set pen
    if args.pen is not None:
        p = pens.get(args.pen)
        pause = get_pause(p["down_pos"])
        pen = g.Pen(
            down_pos=p["down_pos"],
            up_pos=p.get("up_pos", PEN_LEVEL),
            down_pause=p.get("down_pause", pause),
            up_pause=p.get("up_pause", pause))
    elif args.down_pos is not None:
        pen = g.Pen(PEN_LEVEL, args.down_pos, get_pause(args.down_pos), get_pause(args.down_pos))
    
    if args.scale is not None:
        PROCESS_ORDER.insert(-1, lambda l: scale(l, args.scale, args.scale, args.scale))

    # modify gcode
    with open(infile, "r") as f:
        content = f.read().splitlines()  # gcode as a list where each element is a line
    new_lines = []  # where the new modified code will be put

    for i, line in enumerate(content):
        # run through stateless single-line processors
        logger.debug("On input line {}: {!r}".format(i, line))
        inputs = [line]
        for step in PROCESS_ORDER:
            for l in inputs:
                outputs = [result for result in step(l)]
            inputs = outputs
        [new_lines.append(output) for output in outputs]
        # import pdb; pdb.set_trace()

    HEADER = [  # commands to add at the beginning of the file
        "G54",
        g.set_feed(FEED_RATE),
        # "G10 L20 P1 X0 Y0 Z0",  # reset work coordinates
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
            # "G10 L20 P1 X0 Y0 Z0",  # reset work coordinates
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
    logger.info('Writing {} lines of gcode to {!r}'.format(len(new_lines), outfile))
    with open(outfile, "w") as f:
        f.write('\n'.join(new_lines)+'\n')
