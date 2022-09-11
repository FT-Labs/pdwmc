#!/usr/bin/env python

import os
import sys
from shutil import rmtree
sys.path.extend(['.', '..'])
from pycparser import c_generator

def get_key_from_value(d, val):
    return [k for k, v in d.items() if v == val][0]

def write_default_settings():
    if not os.path.exists("/etc/xdg/pdwm"):
        sys.stderr("Error: /etc/xdg/pdwm doesn't exist.")
        exit(1)
    p = set_dwm_data_dir()
    if not os.path.exists(p):
        os.makedirs(p)
    os.system(f"cp -fr /etc/xdg/pdwm/* {p}")
    os.system("tput setaf 51")
    print(f"Default settings have been written to {p}")
    p = set_dwm_cache_dir()
    if os.path.exists(p):
        rmtree(p)

def set_dwm_data_dir():
    d = os.getenv("XDG_CONFIG_HOME")

    if d == None:
        d = os.getenv("HOME")
        if d == None:
            exit(1)
        d = d + "/.config/phyos/pdwm"
        return d

    d = d + "/phyos/pdwm"
    return d

def set_dwm_cache_dir():
    d = os.getenv("XDG_CACHE_HOME")

    if d == None:
        d = os.getenv("HOME")
        if d == None:
            return os.curdir
        d = d + "/.cache/phyos/pdwm"
        return d

    d = d + "/phyos/pdwm"
    return d


def read_file(header, path):
    with open(path, "r", encoding="utf-8") as f:
        return header + f.read()

def print_ast_to_c(ast):
    generator = c_generator.CGenerator()
    return generator._generate_stmt(ast)
