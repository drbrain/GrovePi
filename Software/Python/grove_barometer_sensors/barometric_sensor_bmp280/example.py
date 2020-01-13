#!/usr/bin/python

import smbus
import RPi.GPIO as GPIO
#import grovepi
from grove_i2c_barometic_sensor_BME280 import BME280

# ===========================================================================
# Example Code
# ===========================================================================

# Initialize the sensor with defaults
bme = BME280()

rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
    bus = smbus.SMBus(1)
else:
    bus = smbus.SMBus(0)

bme.showCalibrationData()

exit()

temp = bmp.readTemperature()

# Read the current barometric pressure level
pressure = bmp.readPressure()

# To calculate altitude based on an estimated mean sea level pressure
# (1013.25 hPa) call the function as follows, but this won't be very accurate
# altitude = bmp.readAltitude()

# To specify a more accurate altitude, enter the correct mean sea level
# pressure level.  For example, if the current pressure level is 1023.50 hPa
# enter 102350 since we include two decimal places in the integer value
altitude = bmp.readAltitude(101560)

print("Temperature: %.2f C" % temp)
print("Pressure:    %.2f hPa" % (pressure / 100.0))
print("Altitude:    %.2f m" % altitude)
