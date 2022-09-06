#!/usr/bin/env python

from dwmparser import *
import argparse

if __name__ == "__main__":
    dwm_parse = DwmParse()
    dwm_parse.write_tmp_files()

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--show", type=str, required=False,
            choices=["appearance", "appr", "buttons", "keys"])

    args = parser.parse_args()

    if args.show != None:
        dwm_parse.which_table(args.show)
#    dwm_parse.update()
#    dwm_parse.print_keys()
#    dwm_parse.print_buttons()
#    dwm_parse.set_appearance_value("fonts", "21")
    dwm_parse.update_appearance()
#    dwm_parse.update_keys()
#    dwm_parse.save_config()
