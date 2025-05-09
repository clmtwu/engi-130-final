#!/usr/bin/env python3

import os
import time

print("DS18B20 Simple Reader")
print("Press Ctrl+C to exit")

try:
    while True:
        # Try to find the sensor
        sensor_found = False
        for dir in os.listdir('/sys/bus/w1/devices/'):
            if dir.startswith('28-'):
                sensor_found = True
                sensor_file = f'/sys/bus/w1/devices/{dir}/w1_slave'
                
                # Read temperature
                with open(sensor_file, 'r') as f:
                    data = f.readlines()
                
                if 'YES' in data[0]:
                    temp_pos = data[1].find('t=')
                    if temp_pos != -1:
                        temp = float(data[1][temp_pos+2:]) / 1000.0
                        print(f"Temperature: {temp:.1f}°C / {(temp * 9/5 + 32):.1f}°F")
                    else:
                        print("Error: Temperature value not found")
                else:
                    print("Error: Sensor reading not valid")
                break
        
        if not sensor_found:
            print("Error: No DS18B20 sensor found")
                
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nProgram stopped by user")
except Exception as e:
    print(f"Error: {e}")