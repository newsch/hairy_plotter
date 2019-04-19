#!/usr/bin/env python3
"""Sweep plotting parameters for testing."""
import math

import gcode as g


def sweep_feeds(r: range, pen: g.Pen, length: float = 700, sep: float = 20) -> g.CmdList:
    cmds = []
    add = lambda a: cmds.append(a)
    for i, feed in enumerate(r):
        ypos = i * sep
        add('(Sweep {}: {})'.format(i+1, feed))
        add(g.move_rapid(0, ypos))
        add(pen.down())
        add(g.move(length, ypos, f=feed))
        add(pen.up())
    return cmds

def sweep_heights(r: range, length: float = 20, safe_height: int = 500) -> g.CmdList:
    cmds = []
    add = lambda a: cmds.append(a)

    add(g.set_feed(20000))
    for i, height in enumerate(r):
        pen = g.Pen(safe_height, height, up_pause=1)
        base = (i*length*2, 0)
        add(pen.up())
        add('(Sweep {}: {})'.format(i+1, height))
        add(g.move_rapid(*base))
        add(pen.down())
        add(g.square(length, base))
    add(pen.up())
    return cmds

cmdlist2str = lambda c: '\n'.join(c)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser('sweep')
    parser.add_argument('param', choices=['feed', 'height', 'feed'])
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

    r = range(args.lower, args.upper, step)
    if args.param == 'feed':
        cmds = sweep_feeds(r, g.Pen(500, 750))
    elif args.param == 'height':
        cmds = sweep_heights(r)

    print(cmdlist2str(cmds))
