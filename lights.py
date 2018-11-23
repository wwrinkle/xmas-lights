import threading
from time import sleep
import random
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

LEGS = [17, 27, 22, 5]

for leg in LEGS:
    GPIO.setup(leg, GPIO.OUT, initial=GPIO.LOW)

class LightMode(threading.Thread):
    def __init__(self, interval=1):
        super().__init__()
        self._stop = threading.Event()
        self._interval = interval

    def run(self):
        while True:
            GPIO.output(LEGS, GPIO.HIGH)

            is_stopped = self._stop.wait(self._interval)
            if is_stopped:
                break

    def stop(self):
        self._stop.set()

class Alternating(LightMode):
    def run(self):
        leg_groups = [{
            'legs': [17, 27],
            'is_on': False
        }, {
            'legs': [22, 5],
            'is_on': True
        }]
        while True:
            for leg_group in leg_groups:
                leg_group['is_on'] = not leg_group['is_on']
                GPIO.output(leg_group['legs'], GPIO.HIGH if leg_group['is_on'] else GPIO.LOW)

            is_stopped = self._stop.wait(self._interval)
            if is_stopped:
                break
            sleep(self._interval)

class Chasing(LightMode):
    def run(self):
        active_leg_index = 0
        while True:
            inactive_legs = [for leg in LEGS if leg != LEGS[active_leg_index]]
            GPIO.output(inactive_legs, GPIO.LOW)
            GPIO.output(LEGS[active_leg_index], GPIO.HIGH)

            active_leg_index += 1
            if active_leg_index > len(LEGS):
                active_leg_index = 0

            is_stopped = self._stop.wait(self._interval)
            if is_stopped:
                break
            sleep(self._interval)

class Blinking(LightMode):
    def run(self):
        lights_are_on = False
        while True:
            GPIO.output(LEGS, GPIO.HIGH if lights_are_on else GPIO.LOW)
            lights_are_on = not lights_are_on 

            is_stopped = self._stop.wait(self._interval)
            if is_stopped:
                break
            sleep(self._interval)

class SingleLegThread(LightMode):
    def __init__(self, leg):
        super().__init__()
        self._leg = leg

    def run(self):
        leg_is_on = False
        while True:
            GPIO.output(self._leg, GPIO.HIGH if leg_is_on else GPIO.LOW)
            leg_is_on = not leg_is_on 

            is_stopped = self._stop.wait(self._interval)
            if is_stopped:
                break
            sleep(self._interval * random.uniform(0, 1))

class Random():
    _threads = []

    def __init__(self, interval=1):
        super().__init__()
        self._interval = interval

    def start(self):
        for leg in LEGS:
            thread = SingleLegThread(leg)
            self._threads.append(thread)
            thread.start()

    def stop(self):
        for thread in self._threads:
            thread.stop()


def init_lights():
    try:
        initial_settings_file = open('initial-settings.txt', 'r')
        initial_settings_text = initial_settings_file.read()
        initial_settings_file.close()
        mode = initial_settings_text.split('|')[0]
        interval = float(initial_settings_text.split('|')[1])
        set_lights(mode, interval)
    except FileNotFoundError:
        set_lights('steady', 1)


def set_lights(mode, interval):
    initial_settings_file = open('initial-settings.txt', 'w')
    initial_settings_file.write('{}|{}'.format(mode, str(interval)))
    if mode == 'Alternating':
        Alternating(interval)
    elif mode == 'Chasing':
        Chasing(interval)
    elif mode == 'Blinking':
        Blinking(interval)
    elif mode == 'Random':
        Random(interval)
    elif mode == 'Steady':
        LightMode(interval)
    