import colorsys

from dot3k.menu import MenuIcon
from dot3k.menu import MenuOption


class Backlight(MenuOption):
    def __init__(self, backlight):
        self.backlight = backlight
        self.hue = 0
        self.sat = 100
        self.val = 100
        self.mode = 0
        self.r = 0
        self.g = 0
        self.b = 0
        self.modes = ['h', 's', 'v', 'r', 'g', 'b']
        self.from_hue()
        self._icons_setup = False
        MenuOption.__init__(self)

    def from_hue(self):
        rgb = colorsys.hsv_to_rgb(self.hue, self.sat / 100.0, self.val / 100.0)
        self.r = int(255 * rgb[0])
        self.g = int(255 * rgb[1])
        self.b = int(255 * rgb[2])

    def from_rgb(self):
        self.hue = colorsys.rgb_to_hsv(self.r / 255.0, self.g / 255.0, self.b / 255.0)[0]

    def setup(self, config):
        self.config = config
        self.mode = 0

        self.r = int(self.get_option('Backlight', 'r', 255))
        self.g = int(self.get_option('Backlight', 'g', 255))
        self.b = int(self.get_option('Backlight', 'b', 255))

        self.hue = float(self.get_option('Backlight', 'h', 0)) / 359.0
        self.sat = int(self.get_option('Backlight', 's', 0))
        self.val = int(self.get_option('Backlight', 'v', 100))

        self.backlight.rgb(self.r, self.g, self.b)

    def setup_icons(self, menu):
        menu.lcd.create_char(0, MenuIcon.arrow_left_right)
        menu.lcd.create_char(1, MenuIcon.arrow_up_down)
        menu.lcd.create_char(2, MenuIcon.arrow_left)
        self._icons_setup = True

    def update_bl(self):
        self.set_option('Backlight', 'r', str(self.r))
        self.set_option('Backlight', 'g', str(self.g))
        self.set_option('Backlight', 'b', str(self.b))
        self.set_option('Backlight', 'h', str(int(self.hue * 359)))
        self.set_option('Backlight', 's', str(self.sat))
        self.set_option('Backlight', 'v', str(self.val))

        self.backlight.rgb(self.r, self.g, self.b)

    def down(self):
        self.mode += 1
        if self.mode >= len(self.modes):
            self.mode = 0
        return True

    def up(self):
        self.mode -= 1
        if self.mode < 0:
            self.mode = len(self.modes) - 1
        return True

    def right(self):
        if self.mode == 6:
            return False

        if self.mode == 0:  # r
            self.r += 1
            if self.r > 255:
                self.r = 0
            self.from_rgb()
        elif self.mode == 1:  # g
            self.g += 1
            if self.g > 255:
                self.g = 0
            self.from_rgb()
        elif self.mode == 2:  # b
            self.b += 1
            if self.b > 255:
                self.b = 0
            self.from_rgb()

        elif self.mode == 3:  # hue
            self.hue += (1.0 / 359.0)
            if self.hue > 1:
                self.hue = 0
            self.from_hue()
        elif self.mode == 4:  # sat
            self.sat += 1
            if self.sat > 100:
                self.sat = 0
            self.from_hue()
        elif self.mode == 5:  # val
            self.val += 1
            if self.val > 100:
                self.val = 0
            self.from_hue()

        self.update_bl()
        return True

    def left(self):
        if self.mode == 0:  #r
            self.r -= 1
            if self.r < 0:
                self.r = 255
            self.from_rgb()
        elif self.mode == 1:  # g
            self.g -= 1
            if self.g < 0:
                self.g = 255
            self.from_rgb()
        elif self.mode == 2:  # b
            self.b -= 1
            if self.b < 0:
                self.b = 255
            self.from_rgb()

        elif self.mode == 3:  # hue
            self.hue -= (1.0 / 359.0)
            if self.hue < 0:
                self.hue = 1
            self.from_hue()
        elif self.mode == 4:  # sat
            self.sat -= 1
            if self.sat < 0:
                self.sat = 100
            self.from_hue()
        elif self.mode == 5:  # val
            self.val -= 1
            if self.val < 0:
                self.val = 100
            self.from_hue()

        self.update_bl()
        return True

    def cleanup(self):
        self._icons_setup = False
        self.mode = 0

    def redraw(self, menu):
        if not self._icons_setup:
            self.setup_icons(menu)

        menu.write_row(0, chr(1) + 'Backlight')
        if self.mode < 6:
            row_1 = 'RGB: ' + str(self.r).zfill(3) + ' ' + str(self.g).zfill(3) + ' ' + str(self.b).zfill(3)
            row_2 = 'HSV: ' + str(int(self.hue * 359)).zfill(3) + ' ' + str(self.sat).zfill(3) + ' ' + str(self.val).zfill(3)

            row_1 = list(row_1)
            row_2 = list(row_2)

            icon_char = 0

            # Position the arrow
            if self.mode == 0:  # hue
                row_1[4] = chr(icon_char)
            elif self.mode == 1:  # sat
                row_1[8] = chr(icon_char)
            elif self.mode == 2:  # val
                row_1[12] = chr(icon_char)
            elif self.mode == 3:  # r
                row_2[4] = chr(icon_char)
            elif self.mode == 4:  # g
                row_2[8] = chr(icon_char)
            elif self.mode == 5:  # b
                row_2[12] = chr(icon_char)

            menu.write_row(1, ''.join(row_1))
            menu.write_row(2, ''.join(row_2))


class Contrast(MenuOption):
    def __init__(self, lcd):
        self.lcd = lcd
        self.contrast = 30
        self._icons_setup = False
        MenuOption.__init__(self)

    def right(self):
        self.contrast += 1
        if self.contrast > 63:
            self.contrast = 0
        self.update_contrast()
        return True

    def left(self):
        self.contrast -= 1
        if self.contrast < 0:
            self.contrast = 63
        self.update_contrast()
        return True

    def setup_icons(self, menu):
        menu.lcd.create_char(0, MenuIcon.arrow_left_right)
        menu.lcd.create_char(1, MenuIcon.arrow_up_down)
        menu.lcd.create_char(2, MenuIcon.arrow_left)
        self._icons_setup = True

    def cleanup(self):
        self._icons_setup = False

    def setup(self, config):
        self.config = config
        self.contrast = int(self.get_option('Display', 'contrast', 40))
        self.lcd.set_contrast(self.contrast)

    def update_contrast(self):
        self.set_option('Display', 'contrast', str(self.contrast))
        self.lcd.set_contrast(self.contrast)

    def redraw(self, menu):
        if not self._icons_setup:
            self.setup_icons(menu)

        menu.write_row(0, 'Contrast')
        menu.write_row(1, chr(0) + 'Value: ' + str(self.contrast))
        menu.clear_row(2)


class Brightness(MenuOption):
    def __init__(self, backlight):
        self.backlight = backlight
        self.brightness = 1.0
        self._icons_setup = False
        MenuOption.__init__(self)

    def setup(self, config):
        self.config = config
        self.mode = 0
        self.r = int(self.get_option('Backlight', 'r', 255))
        self.g = int(self.get_option('Backlight', 'g', 255))
        self.b = int(self.get_option('Backlight', 'b', 255))
        self.brightness = float(self.get_option('Display', 'brightness', 1.0))
        #self.backlight.rgb(self.r, self.g, self.b)
        self.set_brightness(self.brightness)

    def setup_icons(self, menu):
        menu.lcd.create_char(0, MenuIcon.arrow_left)
        menu.lcd.create_char(1, MenuIcon.arrow_right)
        self._icons_setup = True

    def set_brightness(self, brightness=None):
        # set brightness from config if none passed in
        # using this to initialize brightness on start-up
        if brightness == None:
            brightness = self.brightness
        brightness += 0.01
        if brightness > 1.0:
            brightness = 1.0
        r = int(int(self.get_option('Backlight', 'r')) * brightness)
        g = int(int(self.get_option('Backlight', 'g')) * brightness)
        b = int(int(self.get_option('Backlight', 'b')) * brightness)
        if self.backlight is not None:
            self.backlight.rgb(r, g, b)
        # now this will persist in config
        self.set_option('Display', 'brightness', str(self.brightness))

    def left(self):
        self.brightness -= 0.1
        if self.brightness < 0:
            self.brightness = 0
        return True

    def right(self):
        self.brightness += 0.1
        if self.brightness > 1:
            self.brightness = 1
        return True

    def redraw(self, menu):
        if not self._icons_setup:
            self.setup_icons(menu)
        brightness_pct = self.brightness * 100
        brightness_str = 'Brightness: {0: >3.0f}%'.format(brightness_pct)
        menu.write_row(0, brightness_str)

        bar_len = int(self.brightness * 10)
        bar_str = '  {0}{1: <10}{2}  '.format(chr(0), '|' * bar_len, chr(1))
        menu.write_row(1, bar_str)

        menu.clear_row(2)

        self.set_brightness(self.brightness)

    def cleanup(self):
        # this will force custom chars to be redefined on reentry to this app
        self._icons_setup = False

