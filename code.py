import time
from machine import Pin, PWM, ticks_ms

# Konstanta
BUTTON1 = 5  # Mode: Linear
BUTTON2 = 18 # Mode: Exponential
BUTTON3 = 19 # Direct End
LED1 = 23    # Analog Value
LED2 = 22    # On Going

# Setup Pins
btn1 = Pin(BUTTON1, Pin.IN, Pin.PULL_UP)
btn2 = Pin(BUTTON2, Pin.IN, Pin.PULL_UP)
btn3 = Pin(BUTTON3, Pin.IN, Pin.PULL_UP)
led1 = PWM(Pin(LED1))
led2 = PWM(Pin(LED2))

# Status
state = "standby"
analog_val = 0
mode = "linear"
begin_time = ticks_ms()
end_time = 0

# Fungsi Interrupt
def btn1_isr(pin):
    global state, mode, begin_time
    if debounce(pin):
        if state == "standby":
            mode = "linear"
            state = "begin"
            begin_time = ticks_ms()
        elif state == "on_going" and ticks_ms() - end_time <= 1500:
            end_time += 5000

def btn2_isr(pin):
    global state, mode, begin_time
    if debounce(pin):
        if state == "standby":
            mode = "exponential"
            state = "begin"
            begin_time = ticks_ms()
        elif state == "on_going" and ticks_ms() - end_time <= 1500:
            end_time += 5000

def btn3_isr(pin):
    global state, end_time
    if debounce(pin) and state == "on_going":
        state = "end"
        end_time = ticks_ms()

# Debounce Tombol
def debounce(pin):
    time.sleep_ms(50)
    return pin.value() == 0

# Delay Non-Blok
def delay(ms):
    start = ticks_ms()
    while ticks_ms() - start < ms:
        pass

# Setup Interrupts
btn1.irq(trigger=Pin.IRQ_FALLING, handler=btn1_isr)
btn2.irq(trigger=Pin.IRQ_FALLING, handler=btn2_isr)
btn3.irq(trigger=Pin.IRQ_FALLING, handler=btn3_isr)

# Fungsi Utama
def main_loop():
    global state, analog_val, end_time
    while True:
        if state == "standby":
            analog_val = 0
            led1.duty(0)
            led2.duty(0)
            print("standby")
            delay(3000)
        elif state == "begin":
            duration = 3500
            increment = 2048 / duration
            start_time = ticks_ms()
            while ticks_ms() - start_time < duration:
                if mode == "linear":
                    analog_val += increment
                elif mode == "exponential":
                    analog_val = 2048 * (1 - (1 - analog_val / 2048) ** 2)
                led1.duty(int(analog_val))
                delay(10)
            state = "on_going"
            end_time = ticks_ms() + 5000
        elif state == "on_going":
            led1.duty(0)
            led2.duty(1024)
            if ticks_ms() >= end_time - 1500:
                led2.duty(512 if (ticks_ms() // 250) % 2 == 0 else 0)
            if ticks_ms() >= end_time:
                state = "end"
        elif state == "end":
            duration = 1500
            decrement = analog_val / duration
            start_time = ticks_ms()
            while ticks_ms() - start_time < duration:
                analog_val -= decrement
                led2.duty(int(analog_val))
                delay(10)
            state = "standby"

main_loop()
