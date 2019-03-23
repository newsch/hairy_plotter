#!/usr/bin/env python3
import gcode as g

import matplotlib.pyplot as plt

# _HERSHEY = {
#     'a':
# }



def parse_hershey_char(code):
    print(code)
    ctoi = lambda a: ord(a) - ord('R')
    get_coord = lambda a: (tuple(map(ctoi, a[i:i+2])) for i in range(0, len(a), 2))
    # assert(code[0]==' ')
    # assert(code[-1] == '\n')
    char_num = int(code[0:4].strip())
    num_vertices = int(code[4:7].strip())
    left = ctoi(code[7])
    right = ctoi(code[8])

    path_strs = code[9:].replace('\n', '').split(' R')
    paths = tuple(tuple(get_coord(p)) for p in path_strs)

    counted_vertices = (len(paths)-1) + sum((len(p) for p in paths)) + 1


    # print(char_num, num_vertices, left, right)
    # print(paths)
    # print(counted_vertices)
    assert(counted_vertices == num_vertices)

    return char_num, paths



def parse_hershey_file(f):

    ctoi = lambda a: ord(a) - ord('R')
    get_coord = lambda a: (tuple(map(ctoi, a[i:i+2])) for i in range(0, len(a), 2))

    def parse_hershey_char_info(code):
        char_num = int(code[1:5].strip())
        num_vertices = int(code[5:8].strip())
        left = ctoi(code[8])
        right = ctoi(code[9])
        return char_num, num_vertices-1

    def parse_hershey_char_paths(num_vertices, code):
        path_strs = code.replace('\n', '').split(' R')
        paths = tuple(tuple(get_coord(p)) for p in path_strs)
        return paths

    while(True):
        info_line = f.read(10)
        if info_line == '':
            break
        print(info_line)
        char_num, num_vertices = parse_hershey_char_info(info_line)
        num_chars = num_vertices*2 + ((num_vertices*2+10) // 72) + 1
        paths_str = f.read(num_chars)
        paths = parse_hershey_char_paths(paths_str)
        counted_vertices = (len(paths)-1) + sum((len(p) for p in paths))
        assert counted_vertices == num_vertices, "{}: {!r}".format(char_num, paths_str)
        yield char_num, paths



    # f.read()
    # text = f.read()
    # return {c: p for c, p in map(parse_hershey_char, text[1:].split('\n '))}

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


# def make_gcode(characters)

if __name__ == "__main__":
    parse_hershey_char("    8  9MWOMOV RUMUV ROQUQ\n")
    with open('../romans.hmp', 'r') as f:
        hmap = f.read()
    c = hershey_to_ascii(hmap)
    print('len:', len(c.keys()))
    print(c)
    # parse_hershey("  507 23H]ZKYIWGUFQFOGMILKKNKSLVMXOZQ[U[WZYXZVZS RUSZS\n")