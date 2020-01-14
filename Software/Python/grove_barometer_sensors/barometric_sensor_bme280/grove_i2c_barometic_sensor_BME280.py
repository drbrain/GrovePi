#!/usr/bin/python
# coding=UTF-8

# References in "()" refer to the BME280 datasheet Revision 1.1

import time
from Adafruit_I2C import Adafruit_I2C
import math

class BME280:

  class Error(Exception):
    pass

  # I²C address (6.2.1)
  __ADDRESS = 0x76

  # Compensation parameters (4.2.2)
  __REG_DIG_T1 = 0x88
  __REG_DIG_T2 = 0x8A
  __REG_DIG_T3 = 0x8C

  __REG_DIG_P1 = 0x8E
  __REG_DIG_P2 = 0x90
  __REG_DIG_P3 = 0x92
  __REG_DIG_P4 = 0x94
  __REG_DIG_P5 = 0x96
  __REG_DIG_P6 = 0x98
  __REG_DIG_P7 = 0x9A
  __REG_DIG_P8 = 0x9C
  __REG_DIG_P9 = 0x9E

  __REG_DIG_H1 = 0xA1
  __REG_DIG_H2 = 0xE1
  __REG_DIG_H3 = 0xE3
  __REG_DIG_H4 = 0xE4
  __REG_DIG_H5 = 0xE5
  __REG_DIG_H6 = 0xE6

  # Chip ID (5.4.1)
  __REG_CHIP_ID = 0xD0
  __CHIP_ID     = 0x60

  # Soft reset (5.4.2)
  __REG_RESET  = 0xE0
  __SOFT_RESET = 0xB6

  # ctrl_hum, humidity (5.4.3)
  __REG_CTRL_HUM = 0xF2

  HUMIDITY_SKIP  = 0b000
  HUMIDITY_X1    = 0b001
  HUMIDITY_X2    = 0b010
  HUMIDITY_X4    = 0b011
  HUMIDITY_X8    = 0b100
  HUMIDITY_X16   = 0b101

  # status (5.4.4)
  __REG_STATUS     = 0xF3

  STATUS_MEASURING = 0b001
  STATUS_UPDATING  = 0b100

  # ctrl_meas, pressure and temperature (5.4.5)
  __REG_CTRL_MEAS = 0xF4

  PRESSURE_SKIP = 0b000
  PRESSURE_X1   = 0b001
  PRESSURE_X2   = 0b010
  PRESSURE_X4   = 0b011
  PRESSURE_X8   = 0b100
  PRESSURE_X16  = 0b101

  TEMPERATURE_SKIP = 0b000
  TEMPERATURE_X1   = 0b001
  TEMPERATURE_X2   = 0b010
  TEMPERATURE_X4   = 0b011
  TEMPERATURE_X8   = 0b100
  TEMPERATURE_X16  = 0b101

  MODE_SLEEP  = 0b00
  MODE_FORCE  = 0b01
  MODE_NORMAL = 0b11

  # config, rate, filter and interface (5.4.6)
  __REG_CONFIG = 0xF5

  STANDBY_0_5  = 0b000
  STANDBY_62_5 = 0b001
  STANDBY_125  = 0b010
  STANDBY_250  = 0b011
  STANDBY_500  = 0b100
  STANDBY_1000 = 0b101
  STANDBY_10   = 0b110
  STANDBY_20   = 0b111

  FILTER_OFF = 0b000
  FILTER_2   = 0b001
  FILTER_4   = 0b010
  FILTER_8   = 0b011
  FILTER_16  = 0b100

  # press, raw pressure (5.4.7)
  __REG_PRESS = 0xF7

  # temp, raw temperature (5.4.8)
  __REG_TEMP = 0xFA

  # hum, raw humidity (5.4.9)
  __REG_TEMP = 0xFD

  # Private fields
  _cal_T1 = 0
  _cal_T2 = 0
  _cal_T3 = 0
  _cal_P1 = 0
  _cal_P2 = 0
  _cal_P3 = 0
  _cal_P4 = 0
  _cal_P5 = 0
  _cal_P6 = 0
  _cal_P7 = 0
  _cal_P8 = 0
  _cal_P9 = 0
  _cal_H1 = 0
  _cal_H2 = 0
  _cal_H3 = 0
  _cal_H4 = 0
  _cal_H5 = 0
  _cal_H6 = 0

  def __init__(self,
               address=__ADDRESS,
               mode=MODE_NORMAL,
               pressure=HUMIDITY_X1,
               temperature=TEMPERATURE_X1,
               humidity=PRESSURE_X1,
               standby=STANDBY_1000,
               filter=FILTER_OFF,
               debug=False):
    self.i2c = Adafruit_I2C(address, debug=debug)

    self.address = address
    self.debug = debug

    self.pressure_sampling    = pressure
    self.temperature_sampling = temperature
    self.humidity_sampling    = humidity

    self.standby = standby
    self.filter  = filter
    self.mode    = mode

    self.writeSettings()

    self.readCalibrationData()

  def readChipID(self):
    return self.i2c.readU8(self.__REG_CHIP_ID)

  def readCalibrationData(self):
    "Reads the calibration data from the device"
    self._cal_T1 = self.i2c.readU16(self.__REG_DIG_T1)
    self._cal_T2 = self.i2c.readS16(self.__REG_DIG_T2)
    self._cal_T3 = self.i2c.readS16(self.__REG_DIG_T3)
    self._cal_P1 = self.i2c.readU16(self.__REG_DIG_P1)
    self._cal_P2 = self.i2c.readS16(self.__REG_DIG_P2)
    self._cal_P3 = self.i2c.readS16(self.__REG_DIG_P3)
    self._cal_P4 = self.i2c.readS16(self.__REG_DIG_P4)
    self._cal_P5 = self.i2c.readS16(self.__REG_DIG_P5)
    self._cal_P6 = self.i2c.readS16(self.__REG_DIG_P6)
    self._cal_P7 = self.i2c.readS16(self.__REG_DIG_P7)
    self._cal_P8 = self.i2c.readS16(self.__REG_DIG_P8)
    self._cal_P9 = self.i2c.readS16(self.__REG_DIG_P9)
    self._cal_H1 = self.i2c.readU8(self.__REG_DIG_H1)
    self._cal_H2 = self.i2c.readS16(self.__REG_DIG_H2)
    self._cal_H3 = self.i2c.readU8(self.__REG_DIG_H3)
    self._cal_H4 = self.i2c.readS16(self.__REG_DIG_H4)
    self._cal_H5 = self.i2c.readS16(self.__REG_DIG_H5)
    self._cal_H6 = self.i2c.readS8(self.__REG_DIG_H6)

  def readSensor(self):
    data = self.i2c.readList(self.__REG_PRESS, 8)

    press_msb = data[0]
    press_lsb = data[1]
    press_xlsb = data[2] >> 4

    temp_msb = data[3]
    temp_lsb = data[4]
    temp_xlsb = data[5] >> 4

    hum_msb = data[6]
    hum_lsb = data[7]

    raw_pressure    = (press_msb << 12) | (press_lsb << 4) | press_xlsb
    raw_temperature = (temp_msb << 12) | (temp_lsb << 4) | temp_xlsb
    raw_humidity    = (hum_msb << 8) | hum_lsb

    return [raw_pressure, raw_temperature, raw_humidity]

  def readStatus(self):
    return self.i2c.readU8(self.__REG_STATUS)

  def showCalibrationData(self):
    "Displays the calibration data from the device"
    print("DBG: _cal_T1 = %6d" % (self._cal_T1))
    print("DBG: _cal_T2 = %6d" % (self._cal_T2))
    print("DBG: _cal_T3 = %6d" % (self._cal_T3))
    print("DBG: _cal_P1 = %6d" % (self._cal_P1))
    print("DBG: _cal_P2 = %6d" % (self._cal_P2))
    print("DBG: _cal_P3 = %6d" % (self._cal_P3))
    print("DBG: _cal_P4 = %6d" % (self._cal_P4))
    print("DBG: _cal_P5 = %6d" % (self._cal_P5))
    print("DBG: _cal_P6 = %6d" % (self._cal_P6))
    print("DBG: _cal_P7 = %6d" % (self._cal_P7))
    print("DBG: _cal_P8 = %6d" % (self._cal_P8))
    print("DBG: _cal_P9 = %6d" % (self._cal_P9))
    print("DBG: _cal_H1 = %6d" % (self._cal_H1))
    print("DBG: _cal_H2 = %6d" % (self._cal_H2))
    print("DBG: _cal_H3 = %6d" % (self._cal_H3))
    print("DBG: _cal_H4 = %6d" % (self._cal_H4))
    print("DBG: _cal_H5 = %6d" % (self._cal_H5))
    print("DBG: _cal_H6 = %6d" % (self._cal_H6))

  def showSettings(self):
    "Displays all configuration and measurement settings"
    ctrl_hum  = self.i2c.readU8(self.__REG_CTRL_HUM)
    ctrl_meas = self.i2c.readU8(self.__REG_CTRL_MEAS)
    config    = self.i2c.readU8(self.__REG_CONFIG)

    osrs_h = ctrl_hum & 0x07

    osrs_t = (ctrl_meas & 0xe0) >> 5
    osrs_p = (ctrl_meas & 0x1c) >> 2
    mode   = ctrl_meas & 0x03

    t_sb     = (config & 0xe0) >> 5
    filter   = (config & 0x1c) >> 2
    spi3w_en = config & 0x01

    print("DBG: osrs_h   = {0:03b}".format(osrs_h))
    print("DBG: osrs_t   = {0:03b}".format(osrs_t))
    print("DBG: osrs_p   = {0:03b}".format(osrs_p))
    print("DBG: mode     = {0:02b}".format(mode))
    print("DBG: t_sb     = {0:03b}".format(t_sb))
    print("DBG: filter   = {0:03b}".format(filter))
    print("DBG: spi3w_en = {0:01b}".format(spi3w_en))

  def writeSettings(self):
    if ((self.humidity_sampling < 0) |
        (self.humidity_sampling > self.HUMIDITY_X16)):
      raise self.Error("Invalid humidity sampling value {0}".format(self.humidity_sampling))
    osrs_h = self.humidity_sampling

    ctrl_hum = osrs_h

    if ((self.temperature_sampling < 0) |
        (self.temperature_sampling > self.TEMPERATURE_X16)):
      raise self.Error("Invalid temperature sampling value {0}".format(self.temperature_sampling))

    if ((self.pressure_sampling < 0) |
        (self.pressure_sampling > self.PRESSURE_X16)):
      raise self.Error("Invalid pressure sampling value {0}".format(self.pressure_sampling))

    if ((self.mode < 0) |
        (self.mode > self.MODE_NORMAL)):
      raise self.Error("Invalid mode {0}".format(self.mode))

    osrs_t = self.temperature_sampling << 5
    osrs_p = self.pressure_sampling << 2
    mode   = self.mode

    ctrl_meas = osrs_t | osrs_p | mode

    if ((self.standby < 0) |
        (self.standby > self.STANDBY_20)):
      raise self.Error("Invalid standby value {0}".format(self.standby))

    if ((self.filter < 0) |
        (self.filter > self.FILTER_16)):
      raise self.Error("Invalid filter value {0}".format(self.filter))

    t_sb     = self.standby << 5
    filter   = self.filter  << 2
    spi3w_en = 0 # SPI interface not supported

    config = t_sb | filter | spi3w_en

    wrote_ctrl_hum  = self.i2c.write8(self.__REG_CTRL_HUM, ctrl_hum)
    wrote_ctrl_meas = self.i2c.write8(self.__REG_CTRL_MEAS, ctrl_meas)
    wrote_config    = self.i2c.write8(self.__REG_CONFIG, config)
