from dot3k.menu import MenuOption
from sys import version_info

if version_info[0] >= 3:
    import configparser as ConfigParser
else:
    import ConfigParser

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
        self.backlight.off()

    def cleanup(self):
        # reset backlight on resume
        self.backlight.rgb(self.r, self.g, self.b)
