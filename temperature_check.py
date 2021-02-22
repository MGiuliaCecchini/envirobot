#!/usr/bin/env python3

import time
from datetime import datetime
import telegram
from bme280 import BME280

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

import logging

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("""compensated-temperature.py - Use the CPU temperature
to compensate temperature readings from the BME280 sensor.
Method adapted from Initial State's Enviro pHAT review:
https://medium.com/@InitialState/tutorial-review-enviro-phat-for-raspberry-pi-4cd6d8c63441

Press Ctrl+C to exit!

""")

bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)


# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read()
        temp = int(temp) / 1000.0
    return temp


# Tuning factor for compensation. Decrease this number to adjust the
# temperature down, and increase to adjust up
factor = 2.25

cpu_temps = [get_cpu_temperature()] * 5
last_max=datetime.now()
TEN_MINUTES=10*60

while True:
    cpu_temp = get_cpu_temperature()
    # Smooth out with some averaging to decrease jitter
    cpu_temps = cpu_temps[1:] + [cpu_temp]
    avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
    raw_temp = bme280.get_temperature()
    comp_temp = raw_temp - ((avg_cpu_temp - raw_temp) / factor)
    if comp_temp > 25:
        duration = datetime.now()-last_max
        if duration.total_seconds() > TEN_MINUTES:
            telegram.send_message("ALERT:{:05.2f} C".format(comp_temp))
            logging.info("Sent alert")
            last_max=datetime.now()
    logging.info("Compensated temperature: {:05.2f} *C".format(comp_temp))
    time.sleep(1.0)
