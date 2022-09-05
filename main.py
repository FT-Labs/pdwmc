#!/usr/bin/env python

from dwmparser import *

if __name__ == "__main__":
    dwm_parse = DwmParse()
    dwm_parse.write_tmp_files()
    dwm_parse.update()
    dwm_parse.print_keys()
#    dwm_parse.set_appearance_value("fonts", "21")
#    dwm_parse.update_appearance()
#    dwm_parse.update_keys()
    dwm_parse.save_config()
