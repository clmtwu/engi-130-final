#!/usr/bin/env python3

# pip freeze > requirements.txt

import os
import glob
import time
import RPi.GPIO as GPIO  # Import the GPIO library

# GPIO Setup
CONTROL_PIN = 17  # GPIO 17 (physical pin 11) - you can change this to any available GPIO pin that's not pin 1 or 4
TEMP_THRESHOLD = 100.0  # Temperature threshold in Fahrenheit

# Initialize GPIO
GPIO.setmode(GPIO.BCM)  # Use BCM numbering
GPIO.setup(CONTROL_PIN, GPIO.OUT)
GPIO.output(CONTROL_PIN, GPIO.LOW)  # Start with the pin off

# Check if the sensor directory exists
base_dir = '/sys/bus/w1/devices/'
if not os.path.exists(base_dir):
    print("1-Wire directory not found! Enable in config!")
    GPIO.cleanup()
    exit(1)

# Try to find the device
device_folders = glob.glob(base_dir + '28*')
if not device_folders:
    print("DS18B20 temperature sensor not found! Check wiring!")
    GPIO.cleanup()
    exit(1)

device_folder = device_folders[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    try:
        with open(device_file, 'r') as f:
            lines = f.readlines()
        return lines
    except FileNotFoundError:
        print(f"Error: Could not open sensor file {device_file}!")
        return ["", ""]

def read_temp():
    lines = read_temp_raw()
    if len(lines) < 2:
        return None, None
        
    # Wait until the reading is ready
    retries = 0
    while lines[0].strip()[-3:] != 'YES' and retries < 5:
        time.sleep(0.2)
        lines = read_temp_raw()
        retries += 1
        
    if retries >= 5:
        print("No valid reads!")
        return None, None
        
    # Find the temperature in the details
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        try:
            temp_c = float(temp_string) / 1000.0  # Convert to Celsius
            temp_f = temp_c * 9.0 / 5.0 + 32.0    # Convert to Fahrenheit
            return temp_c, temp_f
        except ValueError:
            print(f"Error: Could not convert temperature value: {temp_string}")
            return None, None
    return None, None

# Control function to manage the GPIO output based on temperature
def control_output(temperature_f):
    if temperature_f is None:
        # Safety measure: turn off output if temperature reading failed
        GPIO.output(CONTROL_PIN, GPIO.LOW)
        return False
        
    if temperature_f > TEMP_THRESHOLD:
        # Turn on 3.3V output when temperature exceeds threshold
        if GPIO.input(CONTROL_PIN) == GPIO.LOW:
            GPIO.output(CONTROL_PIN, GPIO.HIGH)
            print(f"Temperature above {TEMP_THRESHOLD}°F - Output ON")
        return True
    else:
        # Turn off output when temperature is below threshold
        if GPIO.input(CONTROL_PIN) == GPIO.HIGH:
            GPIO.output(CONTROL_PIN, GPIO.LOW)
            print(f"Temperature below {TEMP_THRESHOLD}°F - Output OFF")
        return False

# Main loop to continuously read temperature and control output
print("DS18B20 Temperature Sensor with GPIO Control")
print(f"Using sensor at: {device_folder}")
print(f"Control pin: GPIO {CONTROL_PIN}")
print(f"Temperature threshold: {TEMP_THRESHOLD}°F")
print("Press Ctrl+C to exit")

try:
    while True:
        celsius, fahrenheit = read_temp()
        if celsius is not None and fahrenheit is not None:
            output_state = control_output(fahrenheit)
            print(f"Temperature: {celsius:.1f}°C / {fahrenheit:.1f}°F | Output: {'ON' if output_state else 'OFF'}")
        else:
            print("Error reading temperature")
            # Safety measure: turn off output if temperature reading failed
            GPIO.output(CONTROL_PIN, GPIO.LOW)
            
        time.sleep(1)
except KeyboardInterrupt:
    print("\nMeasurement stopped by user")
finally:
    # Clean up GPIO on exit
    GPIO.cleanup()
    print("GPIO pins have been cleaned up")