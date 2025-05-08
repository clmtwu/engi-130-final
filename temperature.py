#!/usr/bin/env python3

import os
import glob
import time

# Check if the sensor directory exists
base_dir = '/sys/bus/w1/devices/'
if not os.path.exists(base_dir):
    print("Error: 1-Wire directory not found! Make sure you've enabled the 1-Wire interface.")
    print("Run these commands:")
    print("sudo modprobe w1-gpio")
    print("sudo modprobe w1-therm")
    exit(1)

# Try to find the device
device_folders = glob.glob(base_dir + '28*')
if not device_folders:
    print("Error: No DS18B20 temperature sensors found!")
    print("Check your wiring and make sure the sensor is properly connected.")
    exit(1)

device_folder = device_folders[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    try:
        with open(device_file, 'r') as f:
            lines = f.readlines()
        return lines
    except FileNotFoundError:
        print(f"Error: Could not open sensor file {device_file}")
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
        print("Error: Could not get a valid reading from the sensor")
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
print("Press Ctrl+C to exit")
try:
    while True:
        celsius, fahrenheit = read_temp()
        if celsius is not None and fahrenheit is not None:
            print(f"Temperature: {celsius:.1f}°C / {fahrenheit:.1f}°F")
        else:
            print("Error reading temperature")
        time.sleep(1)
except KeyboardInterrupt:
    print("\nMeasurement stopped by user")