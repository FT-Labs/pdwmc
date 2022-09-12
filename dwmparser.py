#!/usr/bin/env python

from __future__ import print_function
import sys
import utils as u
import os
import subprocess
from dwmparams import *
import tabulate
from phyOS_simple_term_menu import TerminalMenu

sys.path.extend(['.', '..'])
from pycparser import c_parser, c_ast

class c(int):
    APPEARANCE = 0
    BUTTONS    = 1
    KEYS       = 2
    RULES      = 3

class DwmParse:

    def __init__(self):
        self.cparser = c_parser.CParser()
        self.data_dir = u.set_dwm_data_dir()
        self.cache_dir = u.set_dwm_cache_dir()
        self.ast = ["", "", "", ""]
        self.tabular_appearance = []
        self.tabular_buttons    = []
        self.tabular_keys       = []
        self.tabular_rules      = []

    def build_dwm(self):
        self.get_files("/appearance", "/keys", "/buttons", "/rules")
        self.update()
        self.save_config()
        os.chdir(self.data_dir)
        os.system("gcc -c dwm-conf.c -fPIC")
        os.system("gcc -shared dwm-conf.o -o libdwm-conf.so")

    def delete_attr(self, attr):
        if attr == self.tabular_appearance:
            t1 = tabulate.tabulate([[i] for i in attr[-1]], tablefmt="fancy_grid").split("\n")
            term_menu = TerminalMenu(t1, skip_empty_entries=True, cursor_index=1)
            idx = term_menu.show()
            idx //= 2
            attr[-1].pop(idx)
            self.write_tmp_files()
        else:
            t1 = tabulate.tabulate(attr, tablefmt="fancy_grid").split("\n")
            term_menu = TerminalMenu(t1, skip_empty_entries=True, cursor_index=1)
            idx = term_menu.show()
            idx //= 2
            attr.pop(idx)
            self.write_tmp_files()

    def get_files(self, *args):
        for f in args:
            if f == "/appearance":
                data = u.read_file("", self.data_dir + "/appearance")
                self.ast[c.APPEARANCE] = self.cparser.parse(data)
            elif f == "/buttons":
                data = u.read_file("", self.data_dir + "/buttons")
                self.ast[c.BUTTONS] = self.cparser.parse(data)
            elif f == "/keys":
                data = u.read_file("", self.data_dir + "/keys")
                self.ast[c.KEYS] = self.cparser.parse(data)
            elif f == "/rules":
                data = u.read_file("", self.data_dir + "/rules")
                self.ast[c.RULES] = self.cparser.parse(data)

    def table_appearance(self):
        if self.tabular_appearance:
            return
        for var in self.ast[c.APPEARANCE]:
            if not isinstance(var.init, c_ast.InitList):
                self.tabular_appearance.append([var.name, var.init.value])
            else:
                t = u.print_ast_to_c(var.init)
                self.tabular_appearance.append(t.strip("\n").split(", "))

    def table_keys(self):
        if self.tabular_keys:
            return
        for var in self.ast[c.KEYS]:
            if isinstance(var, c_ast.Typedef):
                continue
            for i in var.init.exprs:
                t = u.print_ast_to_c(i)
                params = t.strip("\n").split(", ", maxsplit=2)
                if params[-1] in keys_dict:
                    params[-1] = keys_dict[params[-1]]
                self.tabular_keys.append(params)

    def table_buttons(self):
        if self.tabular_buttons:
            return
        for var in self.ast[c.BUTTONS]:
            if isinstance(var, c_ast.Typedef):
                continue
            for i in var.init.exprs:
                t = u.print_ast_to_c(i)
                params = t.strip("\n").split(", ", maxsplit=3)
                if params[-1] in buttons_dict:
                    params[-1] = buttons_dict[params[-1]]
                self.tabular_buttons.append(params)

    def table_rules(self):
        if self.tabular_rules:
            return
        for var in self.ast[c.RULES]:
            if isinstance(var, c_ast.Typedef):
                continue
            for i in var.init.exprs:
                t = u.print_ast_to_c(i)
                params = t.strip("\n").split(", ")
                self.tabular_rules.append(params)

    def make_action(self, command, is_terminal):
        cmd = 'spawn, SHCMD('
        if is_terminal:
            cmd += f'MAKETERM(TERMINAL, " -e {command}"))'
        else:
            cmd += f'"{command}")'
        return cmd

    def make_tables(self):
        self.table_appearance()
        self.table_buttons()
        self.table_keys()
        self.table_rules()

    def which_table(self, arg, argval):
        os.system("tput setaf 51")
        if "app" in argval or argval == "font":
            self.update_appearance()
            self.table_appearance()
            if arg == "show":
                self.print_appearance()
            elif arg == "change" and argval == "appr":
                self.change_appearance_nonfont()
            elif arg == "change" and argval == "font":
                self.change_font(False)
            elif arg == "add" and argval == "font":
                self.change_font(True)
            elif arg == "delete" and argval == "font":
                self.delete_attr(self.tabular_appearance)
        elif "key" in argval:
            self.update_keys()
            self.table_keys()
            if arg == "show":
                self.print_keys()
            elif arg == "change":
                self.change_key(False)
            elif arg == "add":
                self.change_key(True)
            elif arg == "delete":
                self.delete_attr(self.tabular_keys)
        elif "button" in argval:
            self.update_buttons()
            self.table_buttons()
            if arg == "show":
                self.print_buttons()
            elif arg == "change":
                self.change_button(False)
            elif arg == "add":
                self.change_button(True)
            elif arg == "delete":
                self.delete_attr(self.tabular_buttons)
        else:
            self.update_rules()
            self.table_rules()
            if arg == "show":
                self.print_rules()
            elif arg == "change":
                self.change_rule(False)
            elif arg == "add":
                self.change_rule(True)
            elif arg == "delete":
                self.delete_attr(self.tabular_rules)

    def write_tmp_files(self):

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        if self.tabular_appearance:
            with open (self.cache_dir + "/appearance", "w", encoding = "utf-8") as a:
                for data in self.tabular_appearance:
                    arr = ", ".join(data) + "\n"
                    if '"' in arr:
                        a.write("fonts, " + ", ".join(data) + "\n")
                    else:
                        a.write(", ".join(data) + "\n")

        if self.tabular_keys:
            with open (self.cache_dir + "/keys", "w", encoding = "utf-8") as a:
                for data in self.tabular_keys:
                    a.write(", ".join(data) + "\n")

        if self.tabular_buttons:
            with open (self.cache_dir + "/buttons", "w", encoding = "utf-8") as a:
                for data in self.tabular_buttons:
                    a.write(", ".join(data) + "\n")

        if self.tabular_rules:
            with open (self.cache_dir + "/rules", "w", encoding = "utf-8") as a:
                for data in self.tabular_rules:
                    a.write(", ".join(data) + "\n")

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
                    arr = l.strip("\n").split(", ", maxsplit=2)
                    if arr[-1] in keys_dict.values():
                        arr[-1] = u.get_key_from_value(keys_dict, arr[-1])
                    arr = ", ".join(arr)
                    line_val = "struct Key key = {" + arr + "};"
                    ast = self.cparser.parse(line_val)
                    cur_attr.init.exprs.append(ast.ext[0].init)

    def update_buttons(self):
        for cur_attr in self.ast[c.BUTTONS]:
            cur_attr.init.exprs.clear()
            if isinstance(cur_attr, c_ast.Typedef):
                continue
            with open(self.cache_dir + "/buttons", "r", encoding = "utf-8") as a:
                for l in a:
                    arr = l.strip("\n").split(", ", maxsplit=3)
                    if arr[-1] in buttons_dict.values():
                        arr[-1] = u.get_key_from_value(buttons_dict, arr[-1])
                    arr = ", ".join(arr)
                    line_val = "struct Button button = {" + arr + "};"
                    ast = self.cparser.parse(line_val)
                    cur_attr.init.exprs.append(ast.ext[0].init)

    def update_rules(self):
        for cur_attr in self.ast[c.RULES]:
            cur_attr.init.exprs.clear()
            if isinstance(cur_attr, c_ast.Typedef):
                continue
            with open(self.cache_dir + "/rules", "r", encoding = "utf-8") as a:
                for l in a:
                    arr = l.strip("\n")
                    line_val = "struct Rule rule = {" + arr + "};"
                    ast = self.cparser.parse(line_val)
                    cur_attr.init.exprs.append(ast.ext[0].init)

    def update(self):
        self.update_appearance()
        self.update_buttons()
        self.update_keys()
        self.update_rules()

    def change_appearance_nonfont(self):
        t1 = tabulate.tabulate(self.tabular_appearance[:-1], tablefmt="fancy_grid").split("\n")
        term_menu = TerminalMenu(t1, skip_empty_entries=True, cursor_index=1)
        idx = term_menu.show()
        idx //= 2
        os.system("tput setaf 51")
        try:
            inp = int(input(f"Set value for {self.tabular_appearance[idx][0]}: "))
            if inp < 0:
                raise ValueError
            os.system("tput sgr0")
            self.tabular_appearance[idx][1] = str(inp)
            self.write_tmp_files()
        except ValueError:
            print("Please enter an integer number")

    def change_button(self, isappend):
        if isappend:
            add_button = []
            events = ["ClkStatusText", "ClkRootWin", "ClkClientWin", "ClkLtSymbol", "ClkTagBar"]
            term_menu = TerminalMenu(events, title="Select event window:")
            eventidx = term_menu.show()
            add_button.append(events[eventidx])
            new_button = input("Please enter the new modifier (Win, Alt, Shift, Control), you can add combinations with '|'.\nGive empty input for no modifier.\n")
            new_button = "0" if new_button == "" else new_button
            add_button.append(new_button)
            new_button = input("Please enter the new mouse button.\n")
            add_button.append(new_button)
            events = ["ADD NEW ACTION (spawn a terminal command)"]
            events.extend(list(buttons_dict.values()))
            term_menu = TerminalMenu(events, title="Select action:")
            eventidx = term_menu.show()
            if eventidx != 0:
                add_button.append(events[eventidx])
            else:
                is_term = input("Will this command run on a terminal? [y|yes or n|no, empty input is no]\n")
                if is_term != "y" and is_term != "" and is_term != "yes" and is_term != "n" and is_term != "no":
                    sys.stderr("Please input a valid argument.")
                    exit(1)
                is_term = True if is_term == "y" or is_term == "yes" else False
                command = input("Please enter your command.\n")
                add_button.append(self.make_action(command, is_term))
            self.tabular_buttons.append(add_button)
            self.write_tmp_files()
        else:
            t1 = tabulate.tabulate(self.tabular_buttons, tablefmt="fancy_grid").split("\n")
            term_menu = TerminalMenu(t1, skip_empty_entries=True, cursor_index=1)
            idx = term_menu.show()
            idx //= 2
            events = ["ClkStatusText", "ClkRootWin", "ClkClientWin", "ClkLtSymbol", "ClkTagBar"]
            term_menu = TerminalMenu(events, title="Select event window:")
            eventidx = term_menu.show()
            self.tabular_buttons[idx][0] = events[eventidx]
            new_button = input("Please enter the new modifier (Win, Alt, ShiftMask), you can add combinations with '|'.\nGive empty input for no modifier.\n")
            new_button = "0" if new_button == "" else new_button
            self.tabular_buttons[idx][1] = new_button
            new_button = input("Please enter the new mouse button.\n")
            self.tabular_buttons[idx][2] = new_button
            self.write_tmp_files()


    def change_font(self, isappend):
        if isappend:
            cur_fonts = [[f'{i} = {self.tabular_appearance[-1][i]}'] for i in range(len(self.tabular_appearance[-1]))]
            os.system("tput setaf 51")
            fonts = subprocess.check_output("fc-list : family style | sed '/\\,/d'", shell=True, text=True).strip("\n").split("\n")
            term_menu = TerminalMenu(fonts, title="Please select a font:")
            termidx = term_menu.show()
            try:
                size = int(input("Please set font size (int): "))
                if size < 0:
                    raise ValueError
                font = '"' + fonts[termidx] + f":size={size}" + '"'
                self.tabular_appearance[-1].append(font)
                print("Current fonts:")
                print(tabulate.tabulate(cur_fonts, tablefmt="fancy_grid"))
                idx = input("Please choose an index and press 'Enter' to add the new font. Empty input appends the font.\n")
                if idx == "":
                    self.write_tmp_files()
                    return
                idx = int(idx)
                if idx < 0:
                    raise ValueError
                else:
                    idx = idx if idx < len(self.tabular_appearance[-1]) else len(self.tabular_appearance[-1]) - 1
                    self.tabular_appearance[-1][-1], self.tabular_appearance[-1][idx] = \
                            self.tabular_appearance[-1][idx], self.tabular_appearance[-1][-1]
                    self.write_tmp_files()
            except ValueError:
                print("Please enter an integer greater than 0.")
        else:
            fonts = [[i] for i in self.tabular_appearance[-1]]
            t2 = tabulate.tabulate(fonts, tablefmt="fancy_grid").split("\n")
            term_menu = TerminalMenu(t2, skip_empty_entries=True, cursor_index=1)
            idx = term_menu.show()
            idx //= 2
            os.system("tput setaf 51")
            fonts = subprocess.check_output("fc-list : family style | sed '/\\,/d'", shell=True, text=True).strip("\n").split("\n")
            term_menu = TerminalMenu(fonts, title="Please select a font:")
            termidx = term_menu.show()
            try:
                size = int(input("Please set font size (int): "))
                if size < 0:
                    raise ValueError
                font = '"' + fonts[termidx] + f":size={size}" + '"'
                self.tabular_appearance[len(self.tabular_appearance) - 1][idx] = font
                self.write_tmp_files()
            except ValueError:
                print("Please enter an integer greater than 0.")

    def change_key(self, isappend):
        if isappend:
            pass
        else:
            t1 = tabulate.tabulate(self.tabular_keys, tablefmt="fancy_grid").split("\n")
            term_menu = TerminalMenu(t1, skip_empty_entries=True, cursor_index=1)
            idx = term_menu.show()
            idx //= 2
            new_key = input("Please enter the new modifier (Win, Alt, ShiftMask), you can add combinations with '|'.\nGive empty input for no modifier.\n")
            self.tabular_keys[idx][0] = new_key
            new_key = input("Please enter the new key, you can add multiple keys with '|'.\n")
            self.tabular_keys[idx][1] = new_key
            self.write_tmp_files()

    def change_rule(self, isappend):
        if isappend:
            pass
        else:
            t1 = tabulate.tabulate(self.tabular_rules, tablefmt="fancy_grid").split("\n")
            term_menu = TerminalMenu(t1, skip_empty_entries=True, cursor_index=1)
            idx = term_menu.show()
            idx //= 2


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
        h = ["CLICK WIN", "KEY", "BUTTON", "ACTION"]
        print(tabulate.tabulate(self.tabular_buttons, headers=h, tablefmt="fancy_grid"))

    def print_keys(self):
        h = ["MODIFIERS", "KEY", "ACTION"]
        print(tabulate.tabulate(self.tabular_keys, headers=h, tablefmt="fancy_grid"))

    def print_rules(self):
        h = ["CLASS", "INSTANCE", "TITLE", "TAGS", "ISFLOATING", "ISTERMINAL", "ISCENTERED", "NOSWALLOW", "MANAGEDSIZE", "MON"]
        print(tabulate.tabulate(self.tabular_rules, headers=h, tablefmt="fancy_grid"))

    def save_config(self):
        a = self.data_dir + "/appearance"
        k = self.data_dir + "/keys"
        b = self.data_dir + "/buttons"
        r = self.data_dir + "/rules"

        with open(a, "w", encoding="utf-8") as f:
            f.write(u.print_ast_to_c(self.ast[c.APPEARANCE]))
        with open(k, "w", encoding="utf-8") as f:
            f.write(u.print_ast_to_c(self.ast[c.KEYS]))
        with open(b, "w", encoding="utf-8") as f:
            f.write(u.print_ast_to_c(self.ast[c.BUTTONS]))
        with open(r, "w", encoding="utf-8") as f:
            f.write(u.print_ast_to_c(self.ast[c.RULES]))
