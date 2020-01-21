import subprocess
import re
import time
import os

from dot3k.menu import MenuOption

class PacmanStats(MenuOption):
    def __init__(self):
        self.last_update_set = 0
        self.update_count_set = 0
        MenuOption.__init__(self)

    def get_last_update(self):
        # use context manager otherwise PIPE stays open, one per refresh
        with subprocess.Popen(('tac', '/var/log/pacman.log'), stdout=subprocess.PIPE) as last_update_log:
            last_update_line = subprocess.check_output(('grep', '-m1', 'upgraded'), stdin=last_update_log.stdout)
            result = last_update_line.decode('utf8')
            self.last_update = re.match('\[(.*?)\]', result).group(1)
            self.last_update = re.sub('(?<=\d)T(?=\d)', ' ', self.last_update)
            self.last_update_set = 1

    def get_update_count(self):
        try:
            result = subprocess.check_output(['checkupdates'])
            update_list = result.decode('utf8').split('\n')
            # this is [''] if no updates available
            if update_list[0]:
                self.update_count = len(update_list)
            else:
                self.update_count = 0
            self.update_count_set = 1
        # this is probably no internet connection
        except subprocess.CalledProcessError:
            self.update_count_set = 0
            raise

    def redraw(self, menu):
        if (not self.last_update_set) and (not self.update_count_set):
            menu.write_row(0, "Getting update")
            menu.write_row(1, "information...")
            menu.clear_row(2)

        self.get_last_update()
        try:
            self.get_update_count()
        except subprocess.CalledProcessError:
            menu.write_option(row=2, text='ERROR: Cannot fetch updates',
                              scroll=True, scroll_delay=1000, scroll_repeat=0,
                              scroll_padding=' ')

        if self.last_update_set:
            menu.write_row(0, "Last update:")
            menu.write_row(1, self.last_update)

        if self.update_count_set:
            menu.write_row(2, '{0} available'.format(self.update_count))

        # can afford to slow this one down too, last_update is a bit heavy
        time.sleep(1)
