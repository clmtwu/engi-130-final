# sudo modprobe w1-gpio
# sudo modprobe w1-therm

import glob
import time

# Base directory for 1-Wire devices
base_dir = '/sys/bus/w1/devices/'
# Find your device folder
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

def read_temp():
    lines = read_temp_raw()
    # Wait until the reading is ready
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    # Find the temperature in the details
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0  # Convert to Celsius
        temp_f = temp_c * 9.0 / 5.0 + 32.0    # Convert to Fahrenheit
        return temp_c, temp_f

# Main loop to continuously read temperature
try:
    while True:
        celsius, fahrenheit = read_temp()
        print(f"Temperature: {celsius:.1f}°C / {fahrenheit:.1f}°F")
        time.sleep(1)
except KeyboardInterrupt:
    print("Measurement stopped by user")