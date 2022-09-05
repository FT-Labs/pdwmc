#!/usr/bin/env python

from __future__ import print_function
import sys
import utils as u
import os
from copy import deepcopy
import tabulate

sys.path.extend(['.', '..'])
from pycparser import c_parser, c_ast

class c(int):
    APPEARANCE = 0
    BUTTONS    = 1
    KEYS       = 2

class DwmParse:

    def __init__(self):
        self.parser = c_parser.CParser()
        self.data_dir = u.set_dwm_data_dir()
        self.cache_dir = u.set_dwm_cache_dir()
        self.ast = []
        self.tabular_appearance = []
        self.tabular_keys       = []
        self.tabular_buttons    = []
        self.get_files()

    def get_files(self):
        data = u.read_file("", self.data_dir + "/appearance")
        self.ast.append(self.parser.parse(data))
        data = u.read_file("", self.data_dir + "/buttons")
        self.ast.append(self.parser.parse(data))
        data = u.read_file("", self.data_dir + "/keys")
        self.ast.append(self.parser.parse(data))

    def write_tmp_files(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        with open (self.cache_dir + "/appearance", "w", encoding = "utf-8") as a:
            for var in self.ast[c.APPEARANCE]:
                if not isinstance(var.init, c_ast.InitList):
                    a.write(f"{var.name}, {var.init.value}\n")
                else:
                    a.write(var.name + ", ")
                    a.write(u.print_ast_to_c(var.init))

        with open (self.cache_dir + "/keys", "w", encoding = "utf-8") as a:
            for var in self.ast[c.KEYS]:
                if isinstance(var, c_ast.Typedef):
                    continue
                if not isinstance(var.init, c_ast.InitList):
                    a.write(f"{var.name} {var.init.value}\n")
                else:
                    for i in var.init.exprs:
                        a.write(u.print_ast_to_c(i))

        with open (self.cache_dir + "/buttons", "w", encoding = "utf-8") as a:
            for var in self.ast[c.BUTTONS]:
                if isinstance(var, c_ast.Typedef):
                    continue
                if not isinstance(var.init, c_ast.InitList):
                    a.write(f"{var.name} {var.init.value}\n")
                else:
                    for i in var.init.exprs:
                        a.write(u.print_ast_to_c(i))

    def set_appearance_value(self, attr, value):
        for var in self.ast[c.APPEARANCE]:
            if var.name == attr:
                if not isinstance(var.init, c_ast.InitList):
                    var.init.value = value
                else:
                    var.init.exprs.append(deepcopy(var.init.exprs[0]))
                    var.init.exprs[-1].value = value

    def update_appearance(self):
        a = open(self.cache_dir + "/appearance", "r", encoding = "utf-8")
        for cur_attr in self.ast[c.APPEARANCE]:
            line_val = a.readline().strip("\n").split(", ")
            self.tabular_appearance.append(line_val)
            if len(line_val) <= 2:
                cur_attr.init.value = line_val[1]
            else:
                while len(line_val) - 1 > len(cur_attr.init.exprs):
                    cur_attr.init.exprs.append(deepcopy(cur_attr.init.exprs[0]))
                for j in range(len(cur_attr.init.exprs)):
                    cur_attr.init.exprs[j].value = line_val[j + 1]
        a.close()

    def update_keys(self):
        for cur_attr in self.ast[c.KEYS]:
            cur_attr.init.exprs.clear()
            if isinstance(cur_attr, c_ast.Typedef):
                continue
            with open(self.cache_dir + "/keys", "r", encoding = "utf-8") as a:
                for l in a:
                    self.tabular_keys.append(l.split(", "))
                    line_val = "struct Key key = {" + l.strip("\n") + "};"
                    ast = self.parser.parse(line_val)
                    cur_attr.init.exprs.append(ast.ext[0].init)

    def update_buttons(self):
        for cur_attr in self.ast[c.BUTTONS]:
            cur_attr.init.exprs.clear()
            if isinstance(cur_attr, c_ast.Typedef):
                continue
            with open(self.cache_dir + "/buttons", "r", encoding = "utf-8") as a:
                for l in a:
                    self.tabular_buttons.append(l.split(", "))
                    line_val = "struct Button button = {" + l.strip("\n") + "};"
                    ast = self.parser.parse(line_val)
                    cur_attr.init.exprs.append(ast.ext[0].init)

    def update(self):
        self.update_appearance()
        self.update_buttons()
        self.update_keys()

    def print_buttons(self):
        h = ["CLICK WIN", "KEY", "BUTTON", "FUNC", "ARG"]
        print(tabulate.tabulate(self.tabular_buttons, headers=h, tablefmt="fancy_grid"))

    def print_keys(self):
        h = ["CLICK WIN", "KEY", "BUTTON", "FUNC", "ARG"]
        print(tabulate.tabulate(self.tabular_keys, tablefmt="fancy_grid"))

    def save_config(self):
        a = self.data_dir + "/appearance"
        k = self.data_dir + "/keys"
        b = self.data_dir + "/buttons"

        with open(a, "w", encoding="utf-8") as f:
            f.write(u.print_ast_to_c(self.ast[c.APPEARANCE]))
        with open(k, "w", encoding="utf-8") as f:
            t = u.print_ast_to_c(self.ast[c.KEYS])
            f.write(t)
        with open(b, "w", encoding="utf-8") as f:
            t = u.print_ast_to_c(self.ast[c.BUTTONS])
            f.write(t)
