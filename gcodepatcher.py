#!/usr/bin/env python3
import argparse
import re

##### VARIABLES #####
Z_Retract_Height    = "G0 Z2"       # this is the upper height/ where Z goes before rapid traversing (pen shouldn't be touching)
Z_Cut_Height        = "G1 Z-1"      # this is the lower height/ where Z goes during cutting (pen down)

# servo positions
PEN_UP = 525
PEN_1_DOWN = 950
PEN_2_DOWN = 1

# template for pen movement
PEN_MOVE_TEMP = "M03 S{}"
PAUSE_TEMP = "G4 P{}"

SEND_HOME = "G0X0Y0"

Z_LOWER = 0
Z_UPPER = 1
Z_PATTERN = "(G[01]) ?([\w\d.]*)Z(-?\d+.?\d*)([\w\d.]*)"
Z_COMPILED = re.compile(Z_PATTERN)

skip_list = [
    "M6"
]


def z_replace(matchobj):
    # TODO: remove F commands
    cmds = []
    code = matchobj.group(1)
    pre = matchobj.group(2)
    zmove = float(matchobj.group(3))
    post = matchobj.group(4)
    if pre:
        cmds.append(code+pre)
    if zmove <= Z_LOWER:
        cmds.append(PEN_MOVE_TEMP.format(PEN_1_DOWN))
        cmds.append(PAUSE_TEMP.format(0.5))
    elif zmove >= Z_UPPER:
        cmds.append(PEN_MOVE_TEMP.format(PEN_UP))
        cmds.append(PAUSE_TEMP.format(0.5))

    if post:
        cmds.append(code+post)
    return '\n'.join(cmds)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', type=argparse.FileType('r'),
                        help='input file (use `-` for stdin)')
    parser.add_argument('outfile', type=argparse.FileType('w'),
                        help='output file (use `-` for stdout)')
    args = parser.parse_args()

    # modify gcode
    new_lines = []  # where the new modified code will be put
    new_lines.append('G0 F1500')  # set feed rate

    content = args.infile.read().splitlines()  # gcode as a list where each element is a line

    for line in content:
        # replace Z codes w/ pen change
        # import pdb; pdb.set_trace()
        skip = False
        for cmd in skip_list:
            if cmd in line:
                skip = True
        if skip:
            continue  # skip to next line

        if Z_COMPILED.match(line):
            cmds = Z_COMPILED.sub(z_replace, line)
            for cmd in cmds.splitlines():
                new_lines.append(cmd)
        else:
            new_lines.append(line)

        # ##### INSERT PEN COMMANDS - REPLACE Z TRANSLATION WITH SERVO ROTATION #####
        # #if line contains z retract text, replace with pen up
        # if Z_Retract_Height in line:
        #     new_code += line.replace(Z_Retract_Height, PEN_UP)
        # #if line contains z cut text, replace with pen down
        # elif Z_Cut_Height in line:
        #     new_code += line.replace(Z_Cut_Height, PEN_DOWN)
        # else:
        #     new_code += line

    new_lines.append(PEN_MOVE_TEMP.format(PEN_1_DOWN))
    new_lines.append(PEN_MOVE_TEMP.format(PEN_UP))
    new_lines.append(SEND_HOME)
    # output new_code
    args.outfile.write('\n'.join(new_lines)+'\n')
