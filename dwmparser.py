#!/usr/bin/env python

from __future__ import print_function
import sys
import utils as u
import os
from dwmparams import *
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
        self.cparser = c_parser.CParser()
        self.data_dir = u.set_dwm_data_dir()
        self.cache_dir = u.set_dwm_cache_dir()
        self.ast = []
        self.tabular_appearance = []
        self.tabular_keys       = []
        self.tabular_buttons    = []
        self.data               = ["", "", ""]
        self.get_files()

    def get_files(self):
        data = u.read_file("", self.data_dir + "/appearance")
        self.ast.append(self.cparser.parse(data))
        data = u.read_file("", self.data_dir + "/buttons")
        self.ast.append(self.cparser.parse(data))
        data = u.read_file("", self.data_dir + "/keys")
        self.ast.append(self.cparser.parse(data))

    def table_appearance(self):
        if self.tabular_appearance:
            return
        for var in self.ast[c.APPEARANCE]:
            if not isinstance(var.init, c_ast.InitList):
                self.tabular_appearance.append([var.name, var.init.value])
                self.data[c.APPEARANCE] += f"{var.name}, {var.init.value}\n"
            else:
                self.data[c.APPEARANCE] += var.name + ", "
                t = u.print_ast_to_c(var.init)
                self.data[c.APPEARANCE] += t
                self.tabular_appearance.append(t.strip("\n").split(", "))

    def table_keys(self):
        if self.tabular_keys:
            return
        for var in self.ast[c.KEYS]:
            if isinstance(var, c_ast.Typedef):
                continue
            if not isinstance(var.init, c_ast.InitList):
                self.data[c.KEYS] += f"{var.name} {var.init.value}\n"
            else:
                for i in var.init.exprs:
                    t = u.print_ast_to_c(i)
                    params = t.strip("\n").split(", ", maxsplit=3)
                    if params[-1] in keys_dict:
                        params[-1] = keys_dict[params[-1]]
                    self.tabular_keys.append(params)
                    self.data[c.KEYS] += t

    def table_buttons(self):
        if self.tabular_buttons:
            return
        for var in self.ast[c.BUTTONS]:
            if isinstance(var, c_ast.Typedef):
                continue
            if not isinstance(var.init, c_ast.InitList):
                self.data[c.BUTTONS] += f"{var.name} {var.init.value}\n"
            else:
                for i in var.init.exprs:
                    t = u.print_ast_to_c(i)
                    self.tabular_buttons.append(t.strip("\n").split(", "))
                    self.data[c.BUTTONS] += t

    def make_tables(self):
        self.table_appearance()
        self.table_buttons()
        self.table_keys()

    def which_table(self, arg):
        os.system("tput setaf 51")
        if arg == "appr" or arg == "appearance":
            self.table_appearance()
            self.print_appearance()
        elif arg == "keys":
            self.table_keys()
            self.print_keys()
        else:
            self.table_buttons()
            self.print_buttons()

    def write_tmp_files(self):
        if self.data[0] == "":
            self.make_tables()

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        with open (self.cache_dir + "/appearance", "w", encoding = "utf-8") as a:
            a.write(self.data[c.APPEARANCE])

        with open (self.cache_dir + "/keys", "w", encoding = "utf-8") as a:
            a.write(self.data[c.KEYS])

        with open (self.cache_dir + "/buttons", "w", encoding = "utf-8") as a:
            a.write(self.data[c.BUTTONS])

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
            if len(line_val) <= 2:
                cur_attr.init.value = line_val[1]
            else:
                cur_attr.init.exprs.clear()
                for j in range(1, len(line_val)):
                    t = self.cparser.parse("const char *x = " + line_val[j] + ";")
                    cur_attr.init.exprs.append(t.ext[0].init)
        a.close()

    def update_keys(self):
        for cur_attr in self.ast[c.KEYS]:
            cur_attr.init.exprs.clear()
            if isinstance(cur_attr, c_ast.Typedef):
                continue
            with open(self.cache_dir + "/keys", "r", encoding = "utf-8") as a:
                for l in a:
                    line_val = "struct Key key = {" + l.strip("\n") + "};"
                    ast = self.cparser.parse(line_val)
                    cur_attr.init.exprs.append(ast.ext[0].init)

    def update_buttons(self):
        for cur_attr in self.ast[c.BUTTONS]:
            cur_attr.init.exprs.clear()
            if isinstance(cur_attr, c_ast.Typedef):
                continue
            with open(self.cache_dir + "/buttons", "r", encoding = "utf-8") as a:
                for l in a:
                    line_val = "struct Button button = {" + l.strip("\n") + "};"
                    ast = self.cparser.parse(line_val)
                    cur_attr.init.exprs.append(ast.ext[0].init)

    def update(self):
        self.update_appearance()
        self.update_buttons()
        self.update_keys()

    def print_appearance(self):
        t1 = tabulate.tabulate(self.tabular_appearance[:-1], tablefmt="fancy_grid").split("\n")
        fonts = [[i] for i in self.tabular_appearance[-1]]
        t2 = tabulate.tabulate(fonts, stralign="center", headers=["FONTS"], tablefmt="fancy_grid").split("\n")
        min_start = min(len(t1), len(t2))
        if len(t1) < len(t2):
            t1, t2 = t2, t1

        for c1, c2 in zip(t1, t2):
            print(c1 + "\t" + c2)

        for c in t1[min_start:]:
            print(c)

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
            f.write(u.print_ast_to_c(self.ast[c.KEYS]))
        with open(b, "w", encoding="utf-8") as f:
            f.write(u.print_ast_to_c(self.ast[c.BUTTONS]))
