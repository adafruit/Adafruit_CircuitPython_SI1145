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


print("Default Vis Gain: {}".format(si1145.vis_gain))
print("Default IR Gain: {}".format(si1145.ir_gain))
print("Default Vis High range: {}".format(str(si1145.als_vis_range_high)))
print("Default IR High range: {}".format(str(si1145.als_ir_range_high)))
print()


### Low range
si1145.als_range_high = False  # both settings
# si1145.als_vis_range_high = False
# si1145.als_ir_range_high = False
time.sleep(0.5)

# test reading attributes
print("Vis High range: {}".format(str(si1145.als_vis_range_high)))
print("IR High range: {}".format(str(si1145.als_ir_range_high)))
print()


gain_list = (
    adafruit_si1145.GAIN_ADC_CLOCK_DIV_1,
    adafruit_si1145.GAIN_ADC_CLOCK_DIV_2,
    adafruit_si1145.GAIN_ADC_CLOCK_DIV_4,
    adafruit_si1145.GAIN_ADC_CLOCK_DIV_8,
    adafruit_si1145.GAIN_ADC_CLOCK_DIV_16,
    adafruit_si1145.GAIN_ADC_CLOCK_DIV_32,
    adafruit_si1145.GAIN_ADC_CLOCK_DIV_64,
    adafruit_si1145.GAIN_ADC_CLOCK_DIV_128,
)


for gain in gain_list:
    si1145.gain = gain  # both gains
    # si1145.vis_gain = gain
    # si1145.ir_gain = gain

    # test reading attributes
    print("Vis Gain: {}".format(si1145.vis_gain))
    print("IR Gain: {}".format(si1145.ir_gain))

    vis, ir = si1145.als
    uv_index = si1145.uv_index
    print("Visible = {}, Infrared = {}, UV Index = {}".format(vis, ir, uv_index))
    print()
    time.sleep(0.5)


### High range
# In high range mode, sensor gain should be ~14.5
si1145.als_range_high = True  # both settings
# si1145.als_vis_range_high = True
# si1145.als_ir_range_high = True
time.sleep(0.5)


# test reading attributes
print("Vis High range: {}".format(str(si1145.als_vis_range_high)))
print("IR High range: {}".format(str(si1145.als_ir_range_high)))
print()


vis, ir = si1145.als
uv_index = si1145.uv_index
print("Visible = {}, Infrared = {}, UV Index = {}".format(vis, ir, uv_index))
