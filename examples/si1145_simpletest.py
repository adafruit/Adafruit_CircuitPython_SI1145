# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2022 Carter Nelson for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

import time
import board
import adafruit_si1145

# setup I2C bus using board default
# change as needed for specific boards
i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

# setup sensor
si1145 = adafruit_si1145.SI1145(i2c)


# High Signal Range mode divides gain by 14.5
# Useful for direct sunlight operation
# si1145.als_vis_range_high = True
# si1145.als_ir_range_high = True


# Gain technically increases integration time
# adafruit_si1145.GAIN_ADC_CLOCK_DIV_1   (1x gain, default)
# adafruit_si1145.GAIN_ADC_CLOCK_DIV_2   (2x gain)
# adafruit_si1145.GAIN_ADC_CLOCK_DIV_4   (4x gain)
# adafruit_si1145.GAIN_ADC_CLOCK_DIV_8   (8x gain)
# adafruit_si1145.GAIN_ADC_CLOCK_DIV_16  (16x gain)
# adafruit_si1145.GAIN_ADC_CLOCK_DIV_32  (32x gain)
# adafruit_si1145.GAIN_ADC_CLOCK_DIV_64  (64x gain)
# adafruit_si1145.GAIN_ADC_CLOCK_DIV_128 (128x gain)


si1145.gain = adafruit_si1145.GAIN_ADC_CLOCK_DIV_16  # changes vis and ir gains
# si1145.vis_gain = adafruit_si1145.GAIN_ADC_CLOCK_DIV_16
# si1145.ir_gain = adafruit_si1145.GAIN_ADC_CLOCK_DIV_16


# loop forever printing values
while True:
    vis, ir = si1145.als
    print("Visible = {}, Infrared = {}".format(vis, ir))
    time.sleep(1)
