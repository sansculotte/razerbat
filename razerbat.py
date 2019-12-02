#!/usr/bin/env python3
from os import path
import time
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
        if not self.active:
            self.active = True
            self.device.fx.wave(WAVE_LEFT)

    def stop(self):
        if self.active:
            self.active = False
            self.set_previous_effect()

    def set_previous_effect(self):
        self.device.fx.reactive(255, 0, 0, REACTIVE_500MS)


def check(alert):
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
        else:
            time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    device = DeviceManager().devices[0]
    alert = Alert(device)
    while 1:
        check(alert)
