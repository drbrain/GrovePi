#!/usr/bin/python

import smbus
import RPi.GPIO as GPIO
#import grovepi
from grove_i2c_barometic_sensor_BME280 import BME280

# ===========================================================================
# Example Code
# ===========================================================================

# Initialize the sensor with defaults
bme = BME280(debug=True)

rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
    bus = smbus.SMBus(1)
else:
    bus = smbus.SMBus(0)

chip_id = bme.readChipID()
print("Chip ID: 0x%02X" % (chip_id))
print("")

bme.readCalibrationData()

bme.showCalibrationData()
print("")

bme.showSettings()
print("")

status = bme.readStatus()
measuring = (status & 0x08) >> 4
im_update = (status & 0x01)
print("measuring: {0}, im_update: {1}".format(measuring, im_update))
print("")

data = bme.readSensor()
print("sensor data: {0}".format(data))
