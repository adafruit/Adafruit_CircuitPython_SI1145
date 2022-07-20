# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2022 Carter Nelson for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

import time
import board
import adafruit_si1145

# setup I2C bus using board default
# change as needed for specific boards
i2c = board.I2C()

# setup sensor
si1145 = adafruit_si1145.SI1145(i2c)

# loop forever printing values
while True:
    vis, ir = si1145.als
    print("Visible = {}, Infrared = {}".format(vis, ir))
    time.sleep(1)
