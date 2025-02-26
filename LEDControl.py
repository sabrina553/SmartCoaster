import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Dictionary to hold GPIO assignments
led_pins = {
    'red': [23, 24],
    'yellow': [12, 16],
    'green': [20,21]
}

# Function to set up GPIO pins
def setup_gpio(pins, state=GPIO.LOW):
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, state)

# Set up all LEDs
for color, pins in led_pins.items():
    setup_gpio(pins)

# Function to set LEDs on or off
def set_leds(color, state):
    for pin in led_pins[color]:
        GPIO.output(pin, state)

# Generalized flash function
def flash(color, duration, count=1):
    for _ in range(count):
        set_leds(color, GPIO.HIGH)
        time.sleep(duration)
        set_leds(color, GPIO.LOW)
        time.sleep(duration)

# Weight detection functions
def weight_detected():
    flash('yellow', 0.5, 2)

def weight_removed():
    flash('red', 0.5, 2)

def log1():
    flash('yellow', 0.1, 2)
def log2():
    
    flash('yellow', 0.1, 2)
    flash('yellow', 0.1, 1)

# Weight percentile function
def weight_percentile(percent):
    for color, pins in led_pins.items():
        set_leds(color, GPIO.LOW)  # Reset all LEDs to LOW

    thresholds = {
        'red': 1/6,
        'yellow': 3/6,
        'green': 5/6,
    }
    if percent >= 1:
        power_on_sequence()
        
    for color, threshold in thresholds.items():
        if percent > threshold:
            set_leds(color, GPIO.HIGH)
    
    time.sleep(2)
    for color, pins in led_pins.items():
        set_leds(color, GPIO.LOW)  # Turn off all LEDs after displaying
    time.sleep(2)
    for color, threshold in thresholds.items():
        if percent > threshold:
            set_leds(color, GPIO.HIGH)
    
    time.sleep(2)
    for color, pins in led_pins.items():
        set_leds(color, GPIO.LOW)  # Turn off all LEDs after displaying
# Power on sequence
def power_on_sequence():
    for _ in range(2):  # Repeat the sequence twice
        for color, pins in led_pins.items():
            for pin in pins:
                GPIO.output(pin, GPIO.HIGH)  # Turn on the pin
                time.sleep(0.075)              # Wait for 0.1 seconds
                GPIO.output(pin, GPIO.LOW)   # Turn off the pin
                # No need to sleep here if you want to move to the next pin immediately
        # No need to sleep here if you want to repeat the sequence immediately