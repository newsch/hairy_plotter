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

SEND_HOME = "G0X0Y0"

Z_PATTERN = "G\dZ(-?\d+.?\d*)(?:F\d+.\d*)?"
Z_COMPILED = re.compile(Z_PATTERN)


def z_replace(matchobj):
    move = float(matchobj.group(1))
    if move < 0:
        return PEN_MOVE_TEMP.format(PEN_1_DOWN)
    else:
        return PEN_MOVE_TEMP.format(PEN_UP)

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
    content = args.infile.read().splitlines()  # gcode as a list where each element is a line

    for line in content:
        # replace Z codes w/ pen change
        # import pdb; pdb.set_trace()
        line = Z_COMPILED.sub(z_replace, line)

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

    new_lines.append(PEN_MOVE_TEMP.format(PEN_UP))
    new_lines.append(SEND_HOME)
    # output new_code
    args.outfile.write('\n'.join(new_lines)+'\n')
