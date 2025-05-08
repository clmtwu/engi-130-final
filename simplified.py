#!/usr/bin/env python3

import os
import time

# Function to read temperature
def read_temp():
    # Check if the kernel modules are loaded
    if not os.path.isdir('/sys/bus/w1/devices/'):
        print("Error: 1-Wire interface not enabled")
        print("Run: sudo modprobe w1-gpio && sudo modprobe w1-therm")
        return None
    
    # Find the sensor
    try:
        sensor_dirs = os.listdir('/sys/bus/w1/devices/')
        sensor_dir = None
        for dir in sensor_dirs:
            if dir.startswith('28-'):
                sensor_dir = dir
                break
                
        if not sensor_dir:
            print("Error: No DS18B20 sensor found")
            return None
            
        # Read the temperature file
        with open(f'/sys/bus/w1/devices/{sensor_dir}/w1_slave', 'r') as f:
            lines = f.readlines()
            
        # Check if reading is valid
        if lines[0].strip()[-3:] != 'YES':
            print("Error: Invalid reading")
            return None
            
        # Get temperature
        temp_pos = lines[1].find('t=')
        if temp_pos == -1:
            print("Error: Temperature value not found")
            return None
            
        temp_string = lines[1][temp_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return (temp_c, temp_f)
        
    except Exception as e:
        print(f"Error: {e}")
        return None

# Main program
print("DS18B20 Temperature Reader")
print("Press Ctrl+C to exit")

try:
    while True:
        result = read_temp()
        if result:
            temp_c, temp_f = result
            print(f"Temperature: {temp_c:.1f}°C / {temp_f:.1f}°F")
        time.sleep(1)
except KeyboardInterrupt:
    print("\nProgram stopped by user")