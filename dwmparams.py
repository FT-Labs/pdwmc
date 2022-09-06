#!/usr/bin/env python

keys_dict = {
    'SHCMD("pavucontrol; kill -44 $(pidof dwmblocks)")' : "Sound options gui",
    'SHCMD("pOS-displayselect")' : "Set display rate & resolution",
    'SHCMD("pOS-mount")' : "Mount device",
    'SHCMD("pOS-umount")' : "Unmount device",
    'SHCMD("mpv --no-cache --no-osc --no-input-default-bindings --profile=low-latency --input-conf=/dev/null --title=webcam $(ls /dev/video[0,2,4,6,8] | tail -n 1)")' : "Open camera",
    'SHCMD("pOS-unicode")' : "Choose emoji & copy",
    '{.v = &layouts[0]}' : "Tiled layout",
    '{.v = &layouts[1]}' : "Backstack layout",
    '{.v = &layouts[2]}' : "Monocle layout",
    '{.v = &layouts[3]}' : "Deck layout",
    '{.v = &layouts[4]}' : "Spiral layout",
    '{.v = &layouts[5]}' : "Dwindle layout",
    '{.v = &layouts[6]}' : "Centered master layout",
    '{.v = &layouts[7]}' : "Centered floatin master layout",
    '{.v = &layouts[8]}' : "Floating (like Windows)",
    'SHCMD("pOS-powermenu")' : "Open power menu",
    'SHCMD("pOS-windowswitchcurtag")' : "Switch between clients in curtag",
    'SHCMD("pOS-windowswitch")' : "Switch between clients in all tags",
    'SHCMD("$BROWSER")' : "Open browser ($BROWSER)",
    'SHCMD("pidof -s $COMPOSITOR && killall -9 $COMPOSITOR || pOS-compositor &")' : "Toggle picom",
    'SHCMD(MAKETERM(TERMINAL, " -e lf"))' : "Open lf (file manager)",
    'SHCMD("pass_menu")' : "Open password manager",
    'SHCMD(MAKETERM(TERMINAL, " -e htop"))' : "Open htop",
    'SHCMD(MAKETERM(TERMINAL, " -e s-tui"))' : "Open stress test (check pc health)",
    'SHCMD("rofi -show drun")' : "Open applications menu",
    'SHCMD("pOS-maimpick ~/Pictures/")' : "Take screenshot",
    'SHCMD("pOS-choose-dir")' : "Open terminal in selected bookmark",
    '{.v = termcmd}' : "Open $TERMINAL",
    'SHCMD("pOS-record")' : "Start recording",
    'SHCMD("pOS-record kill")' : "Stop recording",
    'SHCMD("pamixer -t; kill -44 $(pidof dwmblocks)")' : "Mute",
    'SHCMD("pamixer -i 3; kill -44 $(pidof dwmblocks)")' : "Increase volume",
    'SHCMD("pamixer -d 3; kill -44 $(pidof dwmblocks)")' : "Decrease volume",
    'SHCMD("pactl set-source-mute @DEFAULT_SOURCE@ toggle")' : "Mute microphone",
    'SHCMD("pOS-touchpadtoggle")' : "Toggle touchpad",
    'SHCMD("light -A 2 && pOS-brightness")' : "Increase brightness",
    'SHCMD("light -U 2 && pOS-brightness")' : "Decrease brightness",
    'SHCMD("var=$( ls /sys/class/leds/ | grep kbd_backlight ); light -s sysfs/leds/$var -r -U 1")' : "Increase keyboard backlight",
    'SHCMD("var=$( ls /sys/class/leds/ | grep kbd_backlight ); light -s sysfs/leds/$var -r -A 1")' : "Decrease keyboard backlight"
}
