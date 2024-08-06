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
#si1145.als_vis_range_high = True
#si1145.als_ir_range_high = True


# set gains (1, 2, 4, 8, 16, 32, 64, 128)
si1145.vis_gain = 16
si1145.ir_gain = 16


# loop forever printing values
while True:
    vis, ir = si1145.als
    print("Visible = {}, Infrared = {}".format(vis, ir))
    time.sleep(1)
