#!/usr/bin/env python

import os
import sys
sys.path.extend(['.', '..'])
from pycparser import c_generator

DWM_DATA_DIR = None

def set_dwm_data_dir():
    global DWM_DATA_DIR
    d = os.getenv("XDG_DATA_HOME")

    if d == None:
        d = os.getenv("HOME")
        if d == None:
            return
        d = d + "/.local/share/phyos/dwm"
        DWM_DATA_DIR = d
        return

    d = d + "/phyos/dwm"
    DWM_DATA_DIR = d

def read_file(header, path):
    with open(path, "r", encoding="utf-8") as f:
        return header + f.read()

def print_ast_to_c(ast):
    generator = c_generator.CGenerator()
    return generator.visit(ast)

def init():
    set_dwm_data_dir()

    if DWM_DATA_DIR == None:
        exit(1)
