try:
    import time
    from machine import Pin, PWM, ticks_ms
except ImportError:
    from mock_machine import Pin, PWM, ticks_ms

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

# Interrupt Functions
def btn1_isr(pin):
    global state, mode, begin_time
    print(f"Button {pin} pressed")
    if debounce(pin):
        print(f"Button {pin} debounce passed")
        if state == "standby":
            mode = "linear"
            state = "begin"
            begin_time = ticks_ms()
        elif state == "on_going":
            if ticks_ms() - end_time <= 1500:
                end_time += 5000

def btn2_isr(pin):
    global state, mode, begin_time
    if debounce(pin):
        if state == "standby":
            mode = "exponential"
            state = "begin"
            begin_time = ticks_ms()
        elif state == "on_going":
            if ticks_ms() - end_time <= 1500:
                end_time += 5000

def btn3_isr(pin):
    global state, end_time
    if debounce(pin):
        if state == "on_going":
            state = "end"
            end_time = ticks_ms()

# Debounce Buttons
def debounce(pin):
    time.sleep_ms(50)
    return pin.value() == 0

# Non-Blocking Delay
def delay(ms):
    start = ticks_ms()
    while ticks_ms() - start < ms:
        pass

# Setup Interrupts
btn1.irq(trigger=Pin.IRQ_FALLING, handler=btn1_isr)
btn2.irq(trigger=Pin.IRQ_FALLING, handler=btn2_isr)
btn3.irq(trigger=Pin.IRQ_FALLING, handler=btn3_isr)
while True:
    print(f"Waiting for button press. Current state: {state}")
    delay(1000)  # Simple delay to prevent busy-waiting
