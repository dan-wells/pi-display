import subprocess
import re
import time
from urllib.request import urlopen
from urllib.error import URLError
import socket

from dot3k.menu import MenuOption, MenuIcon

class NetworkStatus(MenuOption):
    def __init__(self):
        MenuOption.__init__(self)
        self.vpn_names = {
            "AirVPN_United-Kingdom_UDP-443": "UK",
            "AirVPN_United-States_UDP-443": "US",
            "AirVPN_Europe_UDP-443": "EU",
            "AirVPN_Asia_UDP-80": "AP",
            "None": "None"
        }
        self.vpn_labels = dict((v, k) for (k, v) in self.vpn_names.items())
        self.vpn_choices = ['UK', 'US', 'EU', 'AP', 'None']

    def setup(self, config):
        # sets self.vpn_name, self.vpn_status
        self.get_vpn_status()
        self.vpn_switch = self.vpn_label
        self._icons_setup = False
        self.mode = 0

    def setup_icons(self, menu):
        menu.lcd.create_char(0, MenuIcon.arrow_left_right)
        self._icons_setup = True

    def get_wifi_name(self):
        try:
            result = subprocess.check_output(['iwgetid']).decode('utf8')
            essid = re.search('ESSID:"(.*)"', result).group(1)
            return essid
        except subprocess.CalledProcessError as e:
            if e.returncode == 255:
                return 'No network'

    def get_vpn_status(self):
        # need to know if we're on tun0 or wlan0 first
        ip_route = subprocess.check_output(['ip', 'route']).decode('utf8')
        # can end up seeing tun0 but then dropping vpn while looking up name
        # if vpn status refreshes during connect/disconnect, so need a default
        vpn_name = 'None'
        if 'tun0' in ip_route:
            con_list_str = subprocess.check_output('nmcli -t -f name,type,device con show'.split()).decode('utf8')
            con_list = con_list_str.split('\n')
            for i in con_list:
                if ':vpn:wlan0' in i:
                    vpn_name = i.split(':')[0]
                    break
            self.vpn_label = self.vpn_names[vpn_name]
            self.vpn_name = vpn_name
        else:
            self.vpn_name = 'None'
            self.vpn_label = 'None'

    def get_daily_traffic(self, ifname):
        return ''

    def check_internet(self):
        try:
            response = urlopen('http://www.google.com', timeout=0.5)
            if response.getcode() == 200:
                return 'Online'
        except URLError:
            return 'Offline'
        except socket.timeout:
            return 'Offline'
        return 'Offline'

    def left(self):
        if self.mode == 0:
            self.mode = 1
            self.vpn_idx = self.vpn_choices.index(self.vpn_label)
        self.vpn_idx -= 1
        if self.vpn_idx == -1:
            self.vpn_idx = len(self.vpn_choices) - 1
        self.vpn_switch = self.vpn_choices[self.vpn_idx]
        if self.vpn_switch == self.vpn_label:
            self.mode = 0
        return True

    def right(self):
        if self.mode == 0:
            self.mode = 1
            self.vpn_idx = self.vpn_choices.index(self.vpn_label)
        self.vpn_idx += 1
        if self.vpn_idx == len(self.vpn_choices):
            self.vpn_idx = 0
        self.vpn_switch = self.vpn_choices[self.vpn_idx]
        if self.vpn_switch == self.vpn_label:
            self.mode = 0
        return True

    def select(self):
        if self.mode == 0:
            pass
        elif self.mode == 1:
            if self.vpn_name != 'None':
                self.mode = 2
                # disconnect current vpn
                p = subprocess.run(['nmcli', 'con', 'down', self.vpn_name])
                #p.wait()
                #self.get_vpn_status()
                self.mode = 0
            if self.vpn_switch != 'None':
                self.mode = 3
                # bring up new vpn
                p = subprocess.run(['nmcli', 'con', 'up', self.vpn_labels[self.vpn_switch]])
                #p.wait()
                #self.get_vpn_status()
                self.mode = 0

    def cleanup(self):
        self._icons_setup = False
        self.mode = 0

    def redraw(self, menu):
        if not self._icons_setup:
            self.setup_icons(menu)

        wifi_name = self.get_wifi_name()
        menu.write_row(0, wifi_name)

        self.get_vpn_status()
        # default mode, show connected vpn
        if self.mode == 0:
            menu.write_row(1, "VPN: {0}".format(self.vpn_label))
        # vpn switching mode, show option to change
        elif self.mode == 1:
            menu.write_row(1, "VPN: {0}{1}".format(chr(0), self.vpn_switch))
        # vpn disconnect mode
        elif self.mode == 2:
            menu.write_row(1, 'Disconnect {0}'.format(self.vpn_label))
        # vpn connect mode
        elif self.mode == 3:
            menu.write_row(1, 'Connect {0}'.format(self.vpn_switch))

        internet = self.check_internet()
        menu.write_row(2, internet)

        # slow it down
        time.sleep(0.5)

