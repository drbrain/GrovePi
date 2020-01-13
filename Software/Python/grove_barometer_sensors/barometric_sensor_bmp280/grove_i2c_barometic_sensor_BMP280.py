#!/usr/bin/python

# References in "()" refer to the BME280 datasheet Revision 1.1

import time
from Adafruit_I2C import Adafruit_I2C
import math

class BME280:
    i2c = None

    # I²C address (6.2.1)
    __ADDRESS = 0x77

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
    __BME280_CHIP_ID    = 0x60

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
    __BME280_REG_PRESS = 0xF7

    # temp, raw temperature (5.4.8)
    __BME280_REG_TEMP = 0xFA

    # hum, raw humidity (5.4.9)
    __BME280_REG_TEMP = 0xFD

    def __init__(self,
                 address=self.__BME280_ADDRESS,
                 mode=self.__BME280_CTRL_MEAS_MODE_NORMAL,
                 debug=False):
        self.i2c = Adafruit_I2C(address)

        self.address = address
        self.debug = debug

        if (mode > __BME280_ADDRESS
