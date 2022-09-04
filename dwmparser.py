#!/usr/bin/env python

from __future__ import print_function
import sys
import utils as u
import os

sys.path.extend(['.', '..'])
from pycparser import c_parser, c_ast

class c(int):
    APPEARANCE = 0
    BUTTONS    = 1
    KEYS       = 2

class DwmParse:

    def __init__(self):
        self.parser = c_parser.CParser()
        self.ast = []

    def get_files(self):
        dir = u.DWM_DATA_DIR

        data = u.read_file("", dir + "/appearance")
        self.ast.append(self.parser.parse(data))
        data = u.read_file("typedef struct Button Button;\n", dir + "/buttons")
        self.ast.append(self.parser.parse(data))
        data = u.read_file("typedef struct Key Key;\n", dir + "/keys")
        self.ast.append(self.parser.parse(data))

    def write_tmp_files(self):
        cache_dir = os.getenv("HOME") + "/.cache/phyos/ddwm"
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        with open (cache_dir + "/appearance", "w", encoding = "utf-8") as a:
            for var in self.ast[c.APPEARANCE]:
                if not isinstance(var.init, c_ast.InitList):
                    a.write(f"{var.name}, {var.init.value}\n")
                else:
                    a.write(var.name + ", ")
                    a.write(u.print_ast_to_c(var.init))

        with open (cache_dir + "/keys", "w", encoding = "utf-8") as a:
            for var in self.ast[c.KEYS]:
                if isinstance(var, c_ast.Typedef):
                    continue
                if not isinstance(var.init, c_ast.InitList):
                    a.write(f"{var.name} {var.init.value}\n")
                else:
                    for i in var.init.exprs:
                        a.write(u.print_ast_to_c(i) + "\n")

        with open (cache_dir + "/buttons", "w", encoding = "utf-8") as a:
            for var in self.ast[c.BUTTONS]:
                if isinstance(var, c_ast.Typedef):
                    continue
                if not isinstance(var.init, c_ast.InitList):
                    a.write(f"{var.name} {var.init.value}\n")
                else:
                    for i in var.init.exprs:
                        a.write(u.print_ast_to_c(i) + "\n")

    def set_appearance_value(self, attr, value):
        for var in self.ast[c.APPEARANCE]:
            if var.name == attr:
                if not isinstance(var.init, c_ast.InitList):
                    var.init.value = value
                else:
                    var.init.exprs.append(var.init.exprs[0])
                return
