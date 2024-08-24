from machine import Pin, PWM, Timer
import utime

# Initialize pins and PWM
button1, button2, button3 = [Pin(p, Pin.IN, Pin.PULL_UP) for p in [5, 18, 19]]
led1, led2 = [PWM(Pin(p), freq=1000, duty=0) for p in [25, 26]]

# Global variables
state, mode, start_time, blink_timer, debounce_time = "standby", "linear", 0, Timer(0), 50
last_button_press = {5: 0, 18: 0, 19: 0}
current_value = 0  # To store the current N value when transitioning to 'end'

# Utility function
def map_value(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def set_analog_output(value):
    mapped_value = map_value(value, 0, 2048, 0, 255)
    if state == "begin":
        led1.duty(mapped_value)
        led2.duty(0)  # Ensure LED 2 is off
    elif state == "end":
        led1.duty(0)  # Ensure LED 1 is off
        led2.duty(mapped_value)

# State functions
def standby():
    global start_time
    led1.duty(0)
    led2.duty(0)
    set_analog_output(0)
    if utime.ticks_diff(utime.ticks_ms(), start_time) >= 3000:
        print("State: Standby")
        start_time = utime.ticks_ms()

def begin():
    global state, start_time, current_value
    elapsed = utime.ticks_diff(utime.ticks_ms(), start_time)
    if mode == "linear":
        value = map_value(elapsed, 0, 3500, 0, 2048)
    else:
        value = int(2048 * (1 - 2.71828 ** (-5 * elapsed / 3500)))
    set_analog_output(value)
    current_value = value  # Update the current value
    print(f"State: Begin, Mode: {mode}, N Value: {value}")
    if elapsed >= 3500:
        state = "on_going"
        start_time = utime.ticks_ms()

def on_going():
    global state, start_time, current_value
    led1.duty(0)
    led2.duty(255)
    elapsed = utime.ticks_diff(utime.ticks_ms(), start_time)
    set_analog_output(2048)  # Max value mapped to 255 for LED2
    current_value = 2048  # Update the current value to max
    print(f"State: On Going, LED2: 255, N Value: 2048")
    if elapsed >= 3500:
        blink_timer.init(period=250, mode=Timer.PERIODIC, callback=lambda t: led2.duty(255 if led2.duty() == 0 else 0))
    if elapsed >= 5000:
        state = "end"
        start_time = utime.ticks_ms()
        blink_timer.deinit()

def end():
    global state, start_time, current_value
    elapsed = utime.ticks_diff(utime.ticks_ms(), start_time)
    # Decay from the current value to 0
    value = int(current_value * 2.71828 ** (-5 * elapsed / 1500))
    set_analog_output(value)
    print(f"State: End, N Value: {value}")
    if elapsed >= 1500:
        state = "standby"
        start_time = utime.ticks_ms()

# Button interrupt handler
def button_handler(pin):
    global state, mode, start_time, current_value
    pin_num = {button1: 5, button2: 18, button3: 19}[pin]
    if utime.ticks_diff(utime.ticks_ms(), last_button_press[pin_num]) < debounce_time:
        return
    last_button_press[pin_num] = utime.ticks_ms()

    if state != "standby" and pin == button3:
        state, start_time = "end", utime.ticks_ms()
        print(f"Button Pressed: {pin_num}, Transition to: End")
    elif state == "standby" and pin in [button1, button2]:
        mode = "linear" if pin == button1 else "exponential"
        state, start_time = "begin", utime.ticks_ms()
        current_value = 0  # Reset current value
        print(f"Button Pressed: {pin_num}, Mode: {mode}, Transition to: Begin")

# Configure interrupts
for button in [button1, button2, button3]:
    button.irq(trigger=Pin.IRQ_FALLING, handler=button_handler)

# Main loop
while True:
    {"standby": standby, "begin": begin, "on_going": on_going, "end": end}[state]()
    utime.sleep_ms(10)
