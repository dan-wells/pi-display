import os

from dot3k.menu import MenuOption

class DiskUsage(MenuOption):
    def __init__(self):
        MenuOption.__init__(self)

    def get_free_space(self, fs):
        fs_stats = os.statvfs(fs)
        block_size = fs_stats.f_frsize
        free_blocks = fs_stats.f_bavail
        gib = 2.**30
        # return free space in GiB, consistent with `df -h`
        free_space = (block_size * free_blocks) / gib
        free_str = '{0:.1f}G'.format(free_space)
        return free_str

    def redraw(self, menu):
        menu.write_row(0, 'Free Space')

        root_free_space = self.get_free_space('/')
        root_str = 'root: {0}'.format(root_free_space)
        menu.write_row(1, root_str)

        nashdd1_free_space = self.get_free_space('/mnt/nashdd1')
        nashdd1_str = 'nashdd1: {0}'.format(nashdd1_free_space)
        menu.write_row(2, nashdd1_str)

