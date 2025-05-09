#!/usr/bin/env python3

import os
import glob
import time
import RPi.GPIO as GPIO  # Import GPIO library

# GPIO setup
ALERT_PIN = 17  # GPIO17 (physical pin 11) - not pin 1 or 4
TEMP_THRESHOLD = 80.0  # Temperature threshold in Fahrenheit

# Initialize GPIO
GPIO.setmode(GPIO.BCM)  # Use BCM numbering scheme
GPIO.setup(ALERT_PIN, GPIO.OUT)  # Set pin as output
GPIO.output(ALERT_PIN, GPIO.LOW)  # Start with pin low (0V)

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
print("DS18B20 Temperature Sensor Reading with Alert")
print(f"Using sensor at: {device_folder}")
print(f"Alert will trigger on GPIO{ALERT_PIN} when temperature exceeds {TEMP_THRESHOLD}°F")
print("Press Ctrl+C to exit")

try:
    while True:
        celsius, fahrenheit = read_temp()
        if celsius is not None and fahrenheit is not None:
            print(f"Temperature: {celsius:.1f}°C / {fahrenheit:.1f}°F")
            
            # Check if temperature is above threshold
            if fahrenheit > TEMP_THRESHOLD:
                GPIO.output(ALERT_PIN, GPIO.HIGH)  # Set pin high (3.3V)
                print(f"ALERT: Temperature above {TEMP_THRESHOLD}°F! GPIO{ALERT_PIN} set HIGH (3.3V)")
            else:
                GPIO.output(ALERT_PIN, GPIO.LOW)  # Set pin low (0V)
                
        else:
            print("Error reading temperature")
            
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nMeasurement stopped by user")
finally:
    # Clean up GPIO settings
    GPIO.cleanup()
    print("GPIO cleaned up")