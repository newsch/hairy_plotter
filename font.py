#!/usr/bin/env python3
from typing import List, Dict, Tuple, NamedTuple, Generator, Mapping, Iterable

import matplotlib.pyplot as plt

import gcode as g


Coordinate = Tuple[int, int]
Path = List[Coordinate]
Charpath = List[Path]

class Glyph(NamedTuple):
    left: int
    right: int
    paths: Charpath
    # box: Tuple[Coordinate, Coordinate]
    # width: int
    # height: int

Charmap = Mapping[str, Glyph]


def parse_hershey_file(f) -> Generator[Tuple[int, Glyph], None, None]:

    ctoi = lambda a: ord(a) - ord('R')

    def parse_hershey_char_info(code):
        char_num = int(code[0:4].strip())
        num_vertices = int(code[4:7].strip())
        left = ctoi(code[7])
        right = ctoi(code[8])
        return char_num, num_vertices-1, left, right  # return the number of vertices - left/right pair

    def parse_hershey_char_paths(num_vertices, f):
        paths = []
        cur_path = []
        counted_vertices = 0
        while(counted_vertices < num_vertices):
            x = f.read(1)
            if x == '\n':
                continue
            y = f.read(1)
            if x == ' ' and y == 'R':
                paths.append(cur_path)
                cur_path = []
            else:
                cur_path.append((ctoi(x), -ctoi(y)))  # flip y values
            counted_vertices += 1
        paths.append(cur_path)
        return paths

    while(True):
        while (f.read(1) == '\n'):  # skip newlines and absorb leading space of new character
            pass
        info_line = f.read(9)
        if info_line == '':  # exit on EOF
            break
        char_num, num_vertices, l, r = parse_hershey_char_info(info_line)
        paths = parse_hershey_char_paths(num_vertices, f)
        yield char_num, Glyph(l, r, paths)


def make_ascii_charcode_map(hmap: str) -> Mapping[str, int]:
    paths = hmap.split()
    charcode_to_ord = {}
    i = 32
    def add(a):
        charcode_to_ord[chr(i)] = a

    for p in paths:
        if '-' in p:
            r = p.split('-')
            for n in range(int(r[0]), int(r[1])+1):
                add(n)
                i += 1
        else:
            add(int(p))
            i += 1
    return charcode_to_ord


def plot_charpath(charpath: Charpath, x_offset: int = 0, y_offset: int = 0):
    plot_paths(offset_paths(charpath, x_offset, y_offset))


def plot_glyph(g: Glyph, start: Coordinate = (0, 0)):
    x, y = start
    plot_charpath(g.paths, x - g.left, y)


def plot_str(cmap: Charmap, txt: str, start: Coordinate = (0, 0)):
    char_start = list(start)
    for c in txt:
        g = cmap[c]
        plot_glyph(g, start=char_start)
        char_start[0] += g.right - g.left


# generic path functions


def plot_paths(paths: Iterable[Path]):
    for p in paths:
        if p:
            x, y = zip(*p)
            plt.plot(x, y)
    plt.axis('equal')


def glyph_to_paths(g: Glyph, start: Coordinate = (0, 0)):
    x, y = start
    paths = []
    for p in g.paths:
        paths.append(offset_path(p, x - g.left, y))
    return paths


def offset_path(p: Path, x_offset: int = 0, y_offset: int = 0):
    return [(c[0] + x_offset, c[1] + y_offset) for c in p]


def scale_path(p: Path, scale: float):
    """Scales from (0, 0)."""
    return [(c[0] * scale, c[1] * scale) for c in p]


def offset_paths(paths: Iterable[Path], x_offset: int = 0, y_offset: int = 0):
    return map(lambda p: offset_path(p, x_offset, y_offset), paths)


def scale_paths(paths: Iterable[Path], scale: float):
    """Scales from (0, 0)."""
    return map(lambda p: scale_path(p, scale), paths)


def str_to_paths(cmap: Charmap,
                 txt: str,
                 start: Coordinate = (0, 0),
                 scale: float = 1,
                 wrap: float = -1,
                 line_height = 20) -> List[Path]:
    """Create paths from text.

    Wraps naively on character width (doesn't take words or whitespace into account).
    """
    x_start, y_start = start
    local_w = wrap / scale  # account for scale when wrapping
    paths = []
    # relative coordinates
    x = 0
    y = 0
    for c in txt:
        g = cmap[c]
        if wrap > 0:
            w = g.right - g.left
            if x + w > local_w:
                # new_line
                x = 0
                y -= line_height
        paths.extend(glyph_to_paths(g, (x, y)))
        x += g.right - g.left
    return list(scale_paths(paths, scale))


def format_txt(cmap: Charmap,
               txt: str,
               line_height: float,
               width: float,
               align: str = 'left',
               justify: bool = False):
    # TODO: wrap long words
    # TODO: align text
    # TODO: figure out scale/start
    # TODO: figure out char height
    widths = {c: (g.right - g.left) for c, g in cmap.items()}
    def str_length(txt: str) -> int:
        return sum((widths[c] for c in txt))

    def output_lines(lines: List[str]):
        # adjust paths horizontally
        line_paths = []
        justify_func = lambda words: justify_paths([str_to_paths(cmap, w) for w in words], width)
        align_func = lambda words: align_path(str_to_paths(cmap, ' '.join(words)), width, align)

        line_paths.extend(map(
            justify_func if justify else align_func, lines))
        # adjust paths vertically
        output = []
        for i, l in enumerate(line_paths):
            output.extend(offset_paths(l, 0, line_height * i))

        return output

    words = txt.split()
    lines = []
    line = []
    llength = 0
    for w in words:
        wlength = str_length(w)
        if llength + wlength > width:
            # add line, reset
            lines.append(line)
            llength = wlength
            line = [w]
        else:
            line.append(w)
            llength += wlength
    # add final line
    if line:
        lines.append(line)
    lines.reverse()
    return output_lines(lines)


def align_path(p: Path, width: float, align: str):
    dx = 0
    w, _ = calc_dimensions(p)
    gap = width - w
    if align == 'left':
        dx = 0
    elif align == 'right':
        dx = gap
    elif align == 'center':
        dx = gap / 2
    return offset_paths(p, dx)


def justify_paths(paths: List[Path], width: float):
    widths = [w for w, _ in map(calc_dimensions, paths)]
    num_paths = len(paths)
    total_width = sum(widths)
    gap = width - total_width
    step = gap / (num_paths - 1)

    output = []
    dx = 0
    for p, w in zip(paths, widths):
        output.extend(offset_paths(p, dx))
        dx += w + step
    return output


def calc_dimensions(paths: Iterable[Path]) -> Tuple[int, int]:
    xs, ys = zip(*sum(paths, []))
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)
    return width, height


if __name__ == "__main__":
    parse_hershey_char("    8  9MWOMOV RUMUV ROQUQ\n")
    with open('../romans.hmp', 'r') as f:
        hmap = f.read()
    c = hershey_to_ascii(hmap)
    print('len:', len(c.keys()))
    print(c)
    # parse_hershey("  507 23H]ZKYIWGUFQFOGMILKKNKSLVMXOZQ[U[WZYXZVZS RUSZS\n")