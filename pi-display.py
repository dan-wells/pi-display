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

from plugins.utils import Backlight, Contrast
from plugins.clock import Clock

# catch interrupt and turn everything off
def signal_handler(sig, frame):
    backlight.off()
    lcd.clear()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def interrupt_self():
    os.kill(os.getpid(), signal.SIGINT)

# when called as a menu option inside Menu structure, this inherits
# Menu config into self.config. when called as idle_handler, that
# doesn't get passed, so have to read config independently
class IdleDisplay(MenuOption):
    def __init__(self, backlight):
        self.backlight = backlight
        MenuOption.__init__(self)
        if self.config is None:
            self.config = ConfigParser.ConfigParser()
            self.config.read('dot3k.cfg')
            self.r = int(self.get_option('Backlight', 'r', 255))
            self.g = int(self.get_option('Backlight', 'g', 255))
            self.b = int(self.get_option('Backlight', 'b', 255))

    def setup(self, config):
        self.config = config
        self.mode = 0
        self.r = int(self.get_option('Backlight', 'r', 255))
        self.g = int(self.get_option('Backlight', 'g', 255))
        self.b = int(self.get_option('Backlight', 'b', 255))
        self.backlight.rgb(self.r, self.g, self.b)

    def redraw(self, menu):
        menu.lcd.clear()
        backlight.off()

    def cleanup(self):
        self.backlight.rgb(self.r, self.g, self.b)

# nested dicts define menus/submenus to display
# instances of classes derived from MenuOption used as menu items
menu = Menu(
    structure={
        'Clock': Clock(backlight),
        'Network': MenuOption(),
        'Usage': MenuOption(),
        'Disk': MenuOption(),
        'Updates': MenuOption(),
        'Power': {
            'Display off': IdleDisplay(backlight),
            'Restart': MenuOption(),
            'Shutdown': MenuOption()
        },
        'Settings': {
            'Contrast': Contrast(lcd),
            'Backlight': Backlight(backlight)
        }
    },
    lcd=lcd,
    idle_handler=IdleDisplay(backlight),
    idle_time=60
    )

# use touch module to control menu
touch.bind_defaults(menu)

while 1:
    menu.redraw()
    time.sleep(0.05)
