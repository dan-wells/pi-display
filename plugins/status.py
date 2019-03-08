import subprocess
import re
import psutil
import time

from dot3k.menu import MenuOption

class SystemStatus(MenuOption):
    def __init__(self):
        MenuOption.__init__(self)
        self.uptime_pat = re.compile('up( (?P<days>\d+) days,)?\s+((?P<hours>\d+):)?(?P<mins>\d+)( min)?,')

    def get_uptime(self):
        result = subprocess.run(['uptime'], stdout=subprocess.PIPE)
        # decode bytes-like object to str
        result_str = result.stdout.decode('utf8').strip()
        uptime_match = re.search(self.uptime_pat, result_str)
        uptime_str = 'Up: '
        if uptime_match.group('days') is not None:
            uptime_str += '{0}d '.format(uptime_match.group('days'))
        if uptime_match.group('hours') is not None:
            uptime_str += '{0}h '.format(uptime_match.group('hours'))
        if uptime_match.group('mins') is not None:
            uptime_str += '{0}m'.format(uptime_match.group('mins'))
        return uptime_str

    def get_cpu(self):
        cpu_usage = psutil.cpu_percent()
        cpu_str = 'CPU: {0: >4}%'.format(cpu_usage)
        return cpu_str

    def get_memory(self):
        memory_usage = psutil.virtual_memory()
        memory_str = 'MEM: {0: >4}%'.format(memory_usage.percent)
        return memory_str

    def redraw(self, menu):
        uptime = self.get_uptime()
        menu.write_row(0, uptime)

        cpu = self.get_cpu()
        menu.write_row(1, cpu)

        memory = self.get_memory()
        menu.write_row(2, memory)

        time.sleep(1.0)

