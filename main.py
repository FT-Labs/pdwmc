#!/usr/bin/env python

import utils as u
from dwmparser import *

if __name__ == "__main__":
    u.init()

    dwm_parse = DwmParse()
    dwm_parse.get_files()

    dwm_parse.set_appearance_value("fonts", "21")
    dwm_parse.write_tmp_files()
