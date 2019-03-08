#!/usr/bin/env python

import sys
import time
import subprocess
import signal
import os
import configparser as ConfigParser

import dothat.backlight as backlight
import dothat.lcd as lcd
import dothat.touch as touch
from dot3k.menu import Menu, MenuOption

from plugins.idle_display import IdleDisplay
from plugins.utils import Backlight, Contrast, Brightness
from plugins.clock import Clock, SimpleClock
from plugins.status import SystemStatus
from plugins.disk import DiskUsage
from plugins.pacman import PacmanStats
from plugins.network import NetworkStatus

# control redraw with this
DO_REDRAW = 1

# catch interrupt and turn everything off
def signal_handler(sig, frame):
    backlight.off()
    lcd.clear()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def interrupt_self():
    os.kill(os.getpid(), signal.SIGINT)

def system_power(mode='restart'):
    # subprocess isn't quick enough to beat lcd redraw, so disable
    global DO_REDRAW
    DO_REDRAW = 0
    backlight.off()
    lcd.clear()
    if mode == 'restart':
        subprocess.call(['shutdown', '-r', 'now'])
    elif mode == 'shutdown':
        subprocess.call(['shutdown', 'now'])

#idle_handler = IdleDisplay(backlight)

# nested dicts define menus/submenus to display
# instances of classes derived from MenuOption used as menu items
menu = Menu(
    structure={
        'Power': {
            'Display Off': IdleDisplay(backlight),
            'Restart': lambda:system_power('restart'),
            'Shutdown': lambda:system_power('shutdown')
        },
        'Network': NetworkStatus(),
        'Updates': PacmanStats(),
        'Clock': SimpleClock(),
        'Settings': {
            'Brightness': Brightness(backlight),
            'Backlight': Backlight(backlight),
            'Contrast': Contrast(lcd)
        },
        'Disk': DiskUsage(),
        'Status': SystemStatus(),
    },
    lcd=lcd,
    idle_handler=IdleDisplay(backlight),
    idle_time=60
    )

# use touch module to control menu
touch.bind_defaults(menu)

# set initial backlight brightness
# TODO work out how this is actually set on start-up
menu.menu_options['Settings']['Brightness'].set_brightness()

while DO_REDRAW:
    menu.redraw()
    time.sleep(0.05)
