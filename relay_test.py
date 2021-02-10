#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# Set up GPIO pins on Raspberry Pi
# Use the pinout command from the raspizero library to see your GPIO's pin numbers
relay1 = 16 # Pin 16 / GPIO 23 on a RasPi 4
relay2 = 18 # Pin 18 / GPIO 24 on a RasPi 4
GPIO.setmode(GPIO.BOARD)
GPIO.setup(relay1, GPIO.OUT)
GPIO.setup(relay2, GPIO.OUT)

# Initialize relays to "off" position
GPIO.output(relay1, GPIO.HIGH)
GPIO.output(relay2, GPIO.HIGH)

# Loop until CTRL-C is pressed and cycle relays on/off
print("Testing relays 1 and 2.  Press CTRL-C to quit.")
while True:
    print("Turning relay1 on")
    GPIO.output(relay1, GPIO.LOW)
    time.sleep(1)
    print("Turning relay2 on")
    GPIO.output(relay2, GPIO.LOW)
    time.sleep(1)
    print("Turning relay 1 off")
    GPIO.output(relay1, GPIO.HIGH)
    time.sleep(1)
    print("Turning relay 2 off")
    GPIO.output(relay2, GPIO.HIGH)
    time.sleep(1)

