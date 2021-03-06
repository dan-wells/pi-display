import time

from dot3k.menu import MenuOption, MenuIcon

class SimpleClock(MenuOption):
    def __init__(self):
        MenuOption.__init__(self)
        self._icons_setup = False

    def setup_icons(self, menu):
        menu.lcd.create_char(6, MenuIcon.bar_left)
        menu.lcd.create_char(7, MenuIcon.bar_right)
        menu.lcd.create_char(0, [0, 31, 0, 0, 0, 0, 31, 0]) # empty segment
        menu.lcd.create_char(1, [0, 31, 0, 16, 16, 0, 31, 0]) # first partial
        menu.lcd.create_char(2, [0, 31, 0, 24, 24, 0, 31, 0]) # second partial
        menu.lcd.create_char(3, [0, 31, 0, 28, 28, 0, 31, 0]) # third partial
        menu.lcd.create_char(4, [0, 31, 0, 30, 30, 0, 31, 0]) # fourth partial
        menu.lcd.create_char(5, MenuIcon.bar_full)
        self._icons_setup = True

    def cleanup(self):
        self._icons_setup = False

    def day_progress(self, menu):
        width = 12
        now = time.localtime(time.time())
        seconds_today = now.tm_sec + (now.tm_min * 60) + (now.tm_hour * 60 * 60)
        seconds_max = float(60 * 60 * 24)
        day_progress = seconds_today / seconds_max
        # 14 segments to fill bar, 2 for each end
        full_bars = int(width * day_progress)
        # pick from 5 partial bar segments for progress through this part of the day
        bar_seconds = seconds_max / width
        bar_progress = (seconds_today - (bar_seconds * full_bars)) / bar_seconds 
        partial_bar_idx = int(5 * bar_progress)
        progress_bar = chr(6) + (chr(5) * full_bars) + chr(partial_bar_idx) + (chr(0) * (width - full_bars - 1)) + chr(7)
        progress_bar = '{0: ^16}'.format(progress_bar)
        return progress_bar

    def redraw(self, menu):
        if not self._icons_setup:
            self.setup_icons(menu)

        time_str = time.strftime('  %a %H:%M:%S')
        menu.write_row(0, time_str)

        date_str = time.strftime('   %d %b %y')
        menu.write_row(1, date_str)

        menu.write_row(2, self.day_progress(menu))


class Clock(MenuOption):
    def __init__(self, backlight=None):
        self.modes = ['date', 'dim', 'bright']
        self.mode = 0
        self.running = False

        if backlight is None:
            import dot3k.backlight
            self.backlight = dot3k.backlight
        else:
            self.backlight = backlight

        self.option_time = 0

        self.dim_hour = 20
        self.bright_hour = 8

        self.is_setup = False

        MenuOption.__init__(self)

    def begin(self):
        self.is_setup = False
        self.running = True

    def setup(self, config):
        MenuOption.setup(self, config)
        self.load_options()

    def set_backlight(self, brightness):
        brightness += 0.01
        if brightness > 1.0:
            brightness = 1.0
        r = int(int(self.get_option('Backlight', 'r')) * brightness)
        g = int(int(self.get_option('Backlight', 'g')) * brightness)
        b = int(int(self.get_option('Backlight', 'b')) * brightness)
        if self.backlight is not None:
            self.backlight.rgb(r, g, b)

    def update_options(self):
        self.set_option('Clock', 'dim', str(self.dim_hour))
        self.set_option('Clock', 'bright', str(self.bright_hour))

    def load_options(self):
        self.dim_hour = int(self.get_option('Clock', 'dim', str(self.dim_hour)))
        self.bright_hour = int(self.get_option('Clock', 'bright', str(self.bright_hour)))
        self.brightness = float(self.get_option('Display', 'brightness', 1.0))

    def cleanup(self):
        self.running = False
        time.sleep(0.01)
        self.set_backlight(self.brightness)
        self.is_setup = False

    def left(self):
        if self.modes[self.mode] == 'dim':
            self.dim_hour = (self.dim_hour - 1) % 24
        elif self.modes[self.mode] == 'bright':
            self.bright_hour = (self.bright_hour - 1) % 24
        else:
            return False
        self.update_options()
        self.option_time = self.millis()
        return True

    def right(self):
        if self.modes[self.mode] == 'dim':
            self.dim_hour = (self.dim_hour + 1) % 24
        elif self.modes[self.mode] == 'bright':
            self.bright_hour = (self.bright_hour + 1) % 24
        self.update_options()
        self.option_time = self.millis()
        return True

    def up(self):
        self.mode = (self.mode - 1) % len(self.modes)
        self.option_time = self.millis()
        return True

    def down(self):
        self.mode = (self.mode + 1) % len(self.modes)
        self.option_time = self.millis()
        return True

    def redraw(self, menu):
        if not self.running:
            return False

        if self.millis() - self.option_time > 5000 and self.option_time > 0:
            self.option_time = 0
            self.mode = 0

        if not self.is_setup:
            # these were overwriting custom chars set for Brightness when 
            # switching between the two apps. 0 and 1 here are small empty/
            # filled circles used in the old binary clock display, so don't
            # need them here anyway
            #menu.lcd.create_char(0, [0, 0, 0, 14, 17, 17, 14, 0])
            #menu.lcd.create_char(1, [0, 0, 0, 14, 31, 31, 14, 0])
            menu.lcd.create_char(2, [0, 14, 17, 17, 17, 14, 0, 0])
            menu.lcd.create_char(3, [0, 14, 31, 31, 31, 14, 0, 0])
            menu.lcd.create_char(4, [0, 4, 14, 0, 0, 14, 4, 0])  # Up down arrow
            menu.lcd.create_char(5, [0, 0, 10, 27, 10, 0, 0, 0])  # Left right arrow
            self.is_setup = True

        hour = float(time.strftime('%H'))

        # want to keep manual control of brightness persistent, so only
        # auto-adjust here if we're at full brightness to start
        self.brightness = float(self.get_option('Display', 'brightness', 1.0))
        if int(self.brightness) == 1.0:
            if hour > self.dim_hour:
                self.brightness = 1.0 - ((hour - self.dim_hour) / (24.0 - self.dim_hour))
            elif hour < self.bright_hour:
                self.brightness = 1.0 * (hour / self.bright_hour)

            self.set_backlight(self.brightness)

        menu.write_row(0, time.strftime('  %a %H:%M:%S  '))

        # row separator
        menu.write_row(1, ' {0} '.format('-' * 14))

        if self.idling:
            menu.clear_row(2)
            return True

        bottom_row = ''

        if self.modes[self.mode] == 'date':
            bottom_row = '{0: ^16}'.format(time.strftime('%d %b %y'))
        elif self.modes[self.mode] == 'dim':
            bottom_row = ' Dim at ' + chr(5) + str(self.dim_hour).zfill(2)
        elif self.modes[self.mode] == 'bright':
            bottom_row = ' Bright at ' + chr(5) + str(self.bright_hour).zfill(2)

        menu.write_row(2, chr(4) + bottom_row)
