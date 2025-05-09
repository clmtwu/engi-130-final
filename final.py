#!/usr/bin/env python3

import os
import glob
import time
import RPi.GPIO as GPIO  # Added GPIO library for pin control

# GPIO Setup - We'll use GPIO pin 17 (physical pin 11) for 3.3V output
# This is neither pin 1 nor pin 4 (pin 1 is 3.3V power, pin 4 is 5V power)
OUTPUT_PIN = 17  # Physical pin 11 on Raspberry Pi

# Set up GPIO
GPIO.setmode(GPIO.BCM)  # Use BCM numbering
GPIO.setup(OUTPUT_PIN, GPIO.OUT)  # Set pin as output

# Check if the sensor directory exists
base_dir = '/sys/bus/w1/devices/'
if not os.path.exists(base_dir):
    print("1-Wire directory not found! Enable in config!")
    exit(1)

# Try to find the device
device_folders = glob.glob(base_dir + '28*')
if not device_folders:
    print("DS18B20 temperature sensor not found! Check wiring!")
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

# Main loop to continuously read temperature
print("DS18B20 Temperature Sensor Reading")
print(f"Using sensor at: {device_folder}")
print(f"Outputting HIGH (3.3V) on GPIO {OUTPUT_PIN} (physical pin 11)")
print("Press Ctrl+C to exit")

try:
    # Set pin HIGH (3.3V)
    GPIO.output(OUTPUT_PIN, GPIO.HIGH)
    print(f"GPIO {OUTPUT_PIN} set to HIGH (3.3V)")
    
    while True:
        celsius, fahrenheit = read_temp()
        if celsius is not None and fahrenheit is not None:
            print(f"Temperature: {celsius:.1f}°C / {fahrenheit:.1f}°F")
        else:
            print("Error reading temperature")
        time.sleep(1)
except KeyboardInterrupt:
    print("\nMeasurement stopped by user")
finally:
    # Clean up GPIO on exit
    GPIO.cleanup()
    print("GPIO pins cleaned up")