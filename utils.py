#!/usr/bin/env python

import os
import sys
sys.path.extend(['.', '..'])
from pycparser import c_generator

def set_dwm_data_dir():
    d = os.getenv("XDG_DATA_HOME")

    if d == None:
        d = os.getenv("HOME")
        if d == None:
            exit(1)
        d = d + "/.local/share/phyos/dwm"
        return d

    d = d + "/phyos/dwm"
    return d

def set_dwm_cache_dir():
    d = os.getenv("XDG_CACHE_HOME")

    if d == None:
        d = os.getenv("HOME")
        if d == None:
            return os.curdir
        d = d + "/.cache/phyos/ddwm"
        return d

    d = d + "/phyos/ddwm"
    return d


def read_file(header, path):
    with open(path, "r", encoding="utf-8") as f:
        return header + f.read()

def print_ast_to_c(ast):
    generator = c_generator.CGenerator()
    return generator._generate_stmt(ast)
