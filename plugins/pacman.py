import subprocess
import re
import time
import os

from dot3k.menu import MenuOption

class PacmanStats(MenuOption):
    def __init__(self):
        MenuOption.__init__(self)

    def last_update(self):
        last_update_log = subprocess.Popen(('tac', '/var/log/pacman.log'), stdout=subprocess.PIPE)
        last_update_line = subprocess.check_output(('grep', '-m1', 'upgraded'), stdin=last_update_log.stdout)
        result = last_update_line.decode('utf8')
        update_time = re.match('\[(.*?)\]', result).group(1)
        return update_time

    def update_count(self):
        update_count_file = '/root/available_updates.txt'
        if not os.path.exists(update_count_file):
            with open(update_count_file, 'w') as f:
                subprocess.run(('/usr/bin/checkupdates'), stdout=f)
        update_count = subprocess.check_output(('wc', '-l', update_count_file)).decode('utf8').split()[0]
        return update_count

    def redraw(self, menu):
        menu.write_row(0, "Last update:")

        last_update = self.last_update()
        menu.write_row(1, last_update)

        update_count = self.update_count()
        menu.write_row(2, '{0} available'.format(update_count))

        # can afford to slow this one down too, last_update is a bit heavy
        time.sleep(1)
