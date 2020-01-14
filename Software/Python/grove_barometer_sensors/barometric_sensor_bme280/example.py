#!/usr/bin/python

import datetime
import signal
import time
from grove_i2c_barometic_sensor_BME280 import BME280

def handler(signal, frame):
    exit(0)

signal.signal(signal.SIGINT, handler)

# Initialize the sensor with defaults
bme = BME280()

while(True):
  now = datetime.datetime.now().isoformat()

  # Read latest sensor values (these are cached)
  bme.readSensor()
  
  # return compensated values (calculate temperature first!)
  temp = bme.temperature()
  pres = bme.pressure() / 100
  hum  = bme.humidity()
  
  # display compensated values
  print("{0} {1:0.2f}℃ {2:0.2f}hPa {3:0.3f}%RH".format(now, temp, pres, hum))

  time.sleep(1)
