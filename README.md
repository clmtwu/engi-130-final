# ENGI - 130 Final Project
## Main Author: Clement Wu (EE @ UCI)
## Date: 05/13/2025
### Team Members: Gabriella Acosta (ME @ SJSU), Jerome Foronda (ME @ SJSU), Isabela Greiner (ME @ UCD)

This is our code for the DS18B20 Temperature Sensor on the Raspberry Pi 4. Please see requirements.txt for the requirements to run this program on your local raspberry pi machine. No custom libraries were used for ease of replicability (and also because I don't have enough experience in Python to properly utilize them)

In development order from latest to earliest (that ran on our Pi):

jerome.py\
final.py\
temperaturev2.py\
temperature.py

You only need to run jerome.py to execute the full program!

## References
Physical/Wiring Pin 1: Powering the temperature probe with 3.3V\
Wiring Pin 9: Generic Ground Pin, feel free to use any other ground pin (25, 39, etc.)\
Physical Pin 17 / Wiring Pin 11: Pin to turn on the siren and lights\
Wiring Pin 25: General Ground Pin for siren and lights (see line 18 for reference)