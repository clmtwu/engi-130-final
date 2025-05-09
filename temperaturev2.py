#!/usr/bin/env python3

import os
import glob
import time
import RPi.GPIO as GPIO  # Import GPIO library

#sudo pip3 install RPi.GPIO

# GPIO Setup
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
GPIO_PIN1 = 17  # GPIO pin 17 (you can change these pins as needed)
GPIO_PIN2 = 27  # GPIO pin 27 (you can change these pins as needed)
GPIO.setup(GPIO_PIN1, GPIO.OUT)  # Set pins as output
GPIO.setup(GPIO_PIN2, GPIO.OUT)
# Initialize pins to OFF
GPIO.output(GPIO_PIN1, GPIO.LOW)
GPIO.output(GPIO_PIN2, GPIO.LOW)

# Temperature threshold in Fahrenheit
TEMP_THRESHOLD = 90.0

# Check if the sensor directory exists
base_dir = '/sys/bus/w1/devices/'
if not os.path.exists(base_dir):
    print("1-Wire directory not found! Enable in config!")
    GPIO.cleanup()  # Clean up GPIO on exit
    exit(1)

# Try to find the device
device_folders = glob.glob(base_dir + '28*')
if not device_folders:
    print("DS18B20 temperature sensor not found! Check wiring!")
    GPIO.cleanup()  # Clean up GPIO on exit
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

def control_gpio(temperature_f):
    if temperature_f >= TEMP_THRESHOLD:
        # Turn ON GPIO pins - set to 3.3V
        GPIO.output(GPIO_PIN1, GPIO.HIGH)
        GPIO.output(GPIO_PIN2, GPIO.HIGH)
        return True
    else:
        # Turn OFF GPIO pins
        GPIO.output(GPIO_PIN1, GPIO.LOW)
        GPIO.output(GPIO_PIN2, GPIO.LOW)
        return False

# Main loop to continuously read temperature
print("DS18B20 Temperature Sensor Reading with GPIO Control")
print(f"Using sensor at: {device_folder}")
print(f"Temperature threshold: {TEMP_THRESHOLD}°F")
print(f"GPIO pins: {GPIO_PIN1}, {GPIO_PIN2}")
print("Press Ctrl+C to exit")

# Status tracking
pins_active = False

try:
    while True:
        celsius, fahrenheit = read_temp()
        if celsius is not None and fahrenheit is not None:
            print(f"Temperature: {celsius:.1f}°C / {fahrenheit:.1f}°F", end=" ")
            
            # Control GPIO based on temperature
            current_state = control_gpio(fahrenheit)
            
            # Only print status change
            if current_state != pins_active:
                if current_state:
                    print("- GPIO pins ON (3.3V)")
                else:
                    print("- GPIO pins OFF")
                pins_active = current_state
            else:
                print()  # Just end the line
                
        else:
            print("Error reading temperature")
        
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nMeasurement stopped by user")
finally:
    # Clean up GPIO when exiting
    GPIO.cleanup()
    print("GPIO pins cleaned up")