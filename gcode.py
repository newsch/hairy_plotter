"""Library of gcode commands and related structures."""
import math
from typing import List

CmdList = List[str]

# class CmdList(list):

#     def add(self, item):
#         """Similar to append, but automagically extends iterables."""
#         if not isinstance(item, str) and hasattr(item, __iter__):
#             self.extend(item)
#         else:
#             self.append(item)

#     def __add__(self, other):
#         self.add(other)


# "standard" commands

def pause(seconds):
    return "G4 P{}".format(seconds)

def set_spindle(rate):
    return "M3 S{}".format(rate)

def set_feed(feed):
    return "F{}".format(feed)

def _build_xyz(x=None, y=None, z=None):
    cmd = ''
    for var, code in (
        (x, 'X'),
        (y, 'Y'),
        (z, 'Z')):
        if var is not None:
            cmd += ' {}{:.6f}'.format(code, var)
    return cmd

def move_rapid(x=None, y=None, z=None):
    return 'G0' + _build_xyz(x, y, z)

def move(x=None, y=None, z=None, f=None):
    cmd = 'G1' + _build_xyz(x, y, z)
    if f is not None:
        cmd += ' {}{}'.format('F', f)
    return cmd

def rapid_home():
    return move_rapid(0, 0, 0)


# plotter-specific commands

def set_pen(pos):
    return set_spindle(pos)


class Pen(object):

    def __init__(self, up: int, down: int, up_pause: float = 1, down_pause: float = 1):
        self.up_pos = up
        self.down_pos = down
        self.up_pause = up_pause
        self.down_pause = down_pause

    def _move(self, pos, add_pause, pause_time):
        cmd = set_pen(self.down_pos)
        if add_pause:
            cmd += '\n'+pause(pause_time)
        return cmd

    def up(self, pause=True):
        return self._move(self.up_pos, pause, self.up_pause)

    def down(self, pause=True):
        return self._move(self.down_pos, pause, self.down_pause)


# shapes

def rect(width, height):
    """Draw a rectangle clockwise from bottom-left."""
    return '\n'.join([
        move(height),
        move(width),
        move(-height),
        move(-width),
    ])

def square(length):
    """Draw a square clockwise from bottom-left."""
    return rect(length, length)

def line(length, angle=0):
    """Draw a line, with angle measured counter-clockwise from right in degrees."""
    return move(
        (length * math.cos(math.radians(angle))),
        (length * math.sin(math.radians(angle))))