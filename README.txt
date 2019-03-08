Code must be run as root to execute commands over /dev interfaces
    pip install dot3k   (then use dothat module)
Installed as pi-display systemd service.

Modules:
    - Clock (import time)
        |  Thu 16:43:01  |  time.strftime('  %a %H:%M:%S  ')
        | -------------- |
        |    07 Mar 19   |  time.strftime('    %d %b %y   ')

    - Network
        |wifi network
        |vpn status (switch vpns subcommand?)
        |u/d speed? over eth0? rx day/week/month?

    - Usage
        |uptime
        |cpu
        |memory

    - Disk
        |root
        |nashdd1

    - Pacman
        |time since last update $(tac /var/log/pacman.log | grep -m1 upgraded)
        |num available updates $(checkupdates | wc)
        |excess packages in cache $(paccache -d)
        ----------------
        |Last update:
        |$(tac /var/log/pacman.log | grep -m1 upgraded)
        |$(checkupdates | wc) available

    - Power
        |restart
        |shutdown
        |display off
