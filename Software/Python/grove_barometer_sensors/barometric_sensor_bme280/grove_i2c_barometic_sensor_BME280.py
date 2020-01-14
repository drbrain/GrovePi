#!/usr/bin/python
# coding=UTF-8

# References in "()" refer to the BME280 datasheet Revision 1.1

import time
from Adafruit_I2C import Adafruit_I2C
import math

class BME280:
  i2c = None

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
  __REG_CTRL_HUM  = 0xF2
  __CTRL_HUM_SKIP = 0b000
  __CTRL_HUM_X1   = 0b001
  __CTRL_HUM_X2   = 0b010
  __CTRL_HUM_X4   = 0b011
  __CTRL_HUM_X8   = 0b100
  __CTRL_HUM_X16  = 0b101

  # status (5.4.4)
  __REG_STATUS       = 0xF3
  __STATUS_MEASURING = 0b001
  __STATUS_UPDATING  = 0b100

  # ctrl_meas, pressure and temperature (5.4.5)
  __REG_CTRL_MEAS         = 0xF4
  __CTRL_MEAS_OSRS_P_SKIP = 0b000
  __CTRL_MEAS_OSRS_P_X1   = 0b001
  __CTRL_MEAS_OSRS_P_X2   = 0b010
  __CTRL_MEAS_OSRS_P_X4   = 0b011
  __CTRL_MEAS_OSRS_P_X8   = 0b100
  __CTRL_MEAS_OSRS_P_X16  = 0b101
  __CTRL_MEAS_OSRS_T_SKIP = 0b000
  __CTRL_MEAS_OSRS_T_X1   = 0b001
  __CTRL_MEAS_OSRS_T_X2   = 0b010
  __CTRL_MEAS_OSRS_T_X4   = 0b011
  __CTRL_MEAS_OSRS_T_X8   = 0b100
  __CTRL_MEAS_OSRS_T_X16  = 0b101
  __CTRL_MEAS_MODE_SLEEP  = 0b00
  __CTRL_MEAS_MODE_FORCE  = 0b01
  __CTRL_MEAS_MODE_NORMAL = 0b11

  # config, rate, filter and interface (5.4.6)
  __REG_CONFIG          = 0xF5
  __CONFIG_T_SB_0_5     = 0b000
  __CONFIG_T_SB_62_5    = 0b001
  __CONFIG_T_SB_125     = 0b010
  __CONFIG_T_SB_250     = 0b011
  __CONFIG_T_SB_500     = 0b100
  __CONFIG_T_SB_1000    = 0b101
  __CONFIG_T_SB_10      = 0b110
  __CONFIG_T_SB_20      = 0b111
  __CONFIG_T_FILTER_OFF = 0b000
  __CONFIG_T_FILTER_2   = 0b001
  __CONFIG_T_FILTER_4   = 0b010
  __CONFIG_T_FILTER_8   = 0b011
  __CONFIG_T_FILTER_16  = 0b100

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
               mode=__CTRL_MEAS_MODE_NORMAL,
               debug=False):
    self.i2c = Adafruit_I2C(address, debug=debug)

    self.address = address
    self.debug = debug

    self.setMode(mode)

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

  def setMode(self, mode):
    if ((mode < 0) | (mode > self.__CTRL_MEAS_MODE_NORMAL)):
      if (self.debug):
        print("Invalid mode, using NORMAL")
      self.mode = self.__CTRL_MEAS_MODE_NORMAL
    else:
      self.mode = mode

    ctrl_meas = self.i2c.readU8(self.__REG_CTRL_MEAS)
    ctrl_meas = (ctrl_meas & 0xfc) | mode

    self.i2c.write8(self.__REG_CTRL_MEAS, ctrl_meas)

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
