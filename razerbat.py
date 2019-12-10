#!/usr/bin/env python3
from os import path
import time
import daemon
from openrazer.client import DeviceManager
from openrazer.client.constants import REACTIVE_500MS, WAVE_LEFT


SYS_CLASS_PATH = '/sys/class/power_supply/BAT0'
CAPACITY_THRESHOLD = 15
CHECK_INTERVAL = 10 # seconds


class Alert(object):

    def __init__(self, device=None):
        self.active = False
        if device is None:
            try:
                self.device = DeviceManager().devices[0]
            except IndexError:
                print('ERROR: No razer device found')
        else:
            self.device = device

    def start(self):
        self.active = True
        self.device.fx.wave(WAVE_LEFT)

    def stop(self):
        self.active = False
        self.set_previous_effect()

    def set_previous_effect(self):
        self.device.fx.reactive(255, 0, 0, REACTIVE_500MS)


def check(alert: Alert):
    with open(path.join(SYS_CLASS_PATH, 'status')) as f:
        status = f.readline().strip()

    with open(path.join(SYS_CLASS_PATH, 'capacity')) as f:
        capacity = int(f.readline().strip())

    if status == 'Discharging' and capacity <= CAPACITY_THRESHOLD:
        if not alert.active:
            alert.start()

    if status == 'Charging' or capacity > CAPACITY_THRESHOLD:
        if alert.active:
            alert.stop()


def run():
    device = DeviceManager().devices[0]
    alert = Alert(device)
    while True:
        check(alert)
        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    with daemon.DaemonContext():
        run()
