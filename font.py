#!/usr/bin/env python3
import gcode as g

import matplotlib.pyplot as plt


def parse_hershey_file(f):

    ctoi = lambda a: ord(a) - ord('R')

    def parse_hershey_char_info(code):
        char_num = int(code[0:4].strip())
        num_vertices = int(code[4:7].strip())
        left = ctoi(code[7])
        right = ctoi(code[8])
        return char_num, num_vertices-1  # return the number of vertices - left/right pair

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
        char_num, num_vertices = parse_hershey_char_info(info_line)
        paths = parse_hershey_char_paths(num_vertices, f)
        yield char_num, paths


def make_ascii_charcode_map(hmap: str):
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


def plot_charpath(charpath):
    for p in charpath:
        x, y = zip(*p)
        plt.plot(x, y)
    plt.axis('equal')


def calc_dimensions(charpath):
    xs, ys = zip(*sum(charpath, []))
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