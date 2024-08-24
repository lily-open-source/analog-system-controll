import time

class Pin:
    IN = 0
    OUT = 1
    PULL_UP = 2
    IRQ_FALLING = 3

    def __init__(self, pin, mode=IN, pull=None):
        pass

    def irq(self, trigger, handler):
        pass

    def value(self):
        return 0

def ticks_ms():
    return int(time.time() * 1000)

class PWM:
    def __init__(self, pin):
        pass

    def duty(self, value):
        pass

    def freq(self, frequency):
        pass
