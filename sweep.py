#!/usr/bin/env python3
"""Sweep plotting parameters for testing."""
import math

import gcode as g


def sweep_feeds(r: range, length: float = 10) -> g.CmdList:
    cmds = []
    add = lambda a: cmds.append(a)
    for i, feed in enumerate(r):
        add(g.move_rapid(i*length, 0))
        add(g.move(0, length, f=feed))
    return cmds

cmdlist2str = lambda c: '\n'.join(c)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser('sweep')
    parser.add_argument('lower', type=int)
    parser.add_argument('upper', type=int)
    sequencing = parser.add_mutually_exclusive_group()
    sequencing.add_argument('-s', '--step', type=int)
    sequencing.add_argument('-n', '--num', type=int)
    args = parser.parse_args()


    if args.step:
        step = args.step
    else:
        calc_step = lambda n: (args.upper - args.lower) // n
        if args.num:
            step = calc_step(args.num)
        else:
            step = calc_step(5)


    print(cmdlist2str(sweep_feeds(range(args.lower, args.upper, step))))
