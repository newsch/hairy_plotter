"""Library of gcode commands and related structures."""
import math
from typing import List, Tuple, Iterable


# Type definitions
Cmd = str
CmdList = Iterable[Cmd]
Coord = Tuple[float, float]

# class CmdList(list):

#     def add(self, item):
#         """Similar to append, but automagically extends iterables."""
#         if not isinstance(item, str) and hasattr(item, __iter__):
#             self.extend(item)
#         else:
#             self.append(item)

#     def __add__(self, other):
#         self.add(other)


def save(fpath: str, cmds: CmdList):
    with open(fpath, 'w') as f:
        f.writelines(cmds)


# "standard" commands

def pause(seconds: float) -> Cmd:
    return "G4 P{:.2f}".format(seconds)

def set_spindle(rate: int) -> Cmd:
    return "M3 S{}".format(rate)

def set_feed(feed: int) -> Cmd:
    return "F{}".format(feed)

def _build_xyz(x=None, y=None, z=None):
    cmd = ''
    for var, code in (
        (x, 'X'),
        (y, 'Y'),
        (z, 'Z')):
        if var is not None:
            cmd += ' {}{:.2f}'.format(code, var)
    return cmd

def move_rapid(x: float = None, y: float = None, z: float = None) -> Cmd:
    """G0 move command."""
    return 'G0' + _build_xyz(x, y, z)

def move(x: float = None, y: float = None, z: float = None, f: int = None) -> Cmd:
    """G1 move linearly command.

    >>> move(1, 0)
    'G1 X1.00 Y0.00'
    >>> move(y=1/3)
    'G1 Y0.33'
    """
    cmd = 'G1' + _build_xyz(x, y, z)
    if f is not None:
        cmd += ' {}{}'.format('F', f)
    return cmd

def rapid_home() -> Cmd:
    return move_rapid(0, 0, 0)


# plotter-specific commands

def set_pen(pos: int) -> Cmd:
    return set_spindle(pos)


class Pen(object):

    def __init__(self, up_pos: int, down_pos: int, up_pause: float = 1, down_pause: float = 1):
        self.up_pos = up_pos
        self.down_pos = down_pos
        self.up_pause = up_pause
        self.down_pause = down_pause

    def _move(self, pos: int, add_pause: bool, pause_time: float) -> Cmd:
        cmd = set_pen(pos)
        if add_pause:
            cmd += '\n'+pause(pause_time)
        return cmd

    def up(self, pause: bool = True) -> Cmd:
        return self._move(self.up_pos, pause, self.up_pause)

    def down(self, pause: bool = True) -> Cmd:
        return self._move(self.down_pos, pause, self.down_pause)

# shapes

def rect(width: float, height: float, start: Coord = (0,0)) -> str:
    """Draw a rectangle clockwise from bottom-left."""
    x, y = start
    return '\n'.join([
        move(x, y + height),
        move(x + width, y + height),
        move(x + width, y),
        move(x, y),
    ])

def square(length: float, start: Coord = (0,0)) -> str:
    """Draw a square clockwise from bottom-left."""
    return rect(length, length, start=start)

def line(length, angle=0) -> str:
    """Draw a line, with angle measured counter-clockwise from right in degrees."""
    return move(
        (length * math.cos(math.radians(angle))),
        (length * math.sin(math.radians(angle))))