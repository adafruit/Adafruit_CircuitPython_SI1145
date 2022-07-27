# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2022 Carter Nelson for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_si1145`
================================================================================

CircuitPython helper library for the SI1145 Digital UV Index IR Visible Light Sensor


* Author(s): Carter Nelson

Implementation Notes
--------------------

**Hardware:**

* https://www.adafruit.com/product/1777

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
"""

import time
from micropython import const
from adafruit_bus_device import i2c_device
from adafruit_register.i2c_struct import Struct

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_SI1145.git"

# Registers
SI1145_DEFAULT_ADDRESS = const(0x60)
SI1145_PART_ID = const(0x00)
SI1145_HW_KEY = const(0x07)
_COEFF_0 = const(0x13)
_COEFF_1 = const(0x14)
_COEFF_2 = const(0x15)
_COEFF_3 = const(0x16)
SI1145_PARAM_WR = const(0x17)
SI1145_COMMAND = const(0x18)
SI1145_RESPONSE = const(0x20)
SI1145_ALS_VIS_DATA0 = const(0x22)
SI1145_UV_INDEX_DATA0 = const(0x2C)
SI1145_PARAM_RD = const(0x2E)

# Commands (for COMMAND register)
SI1145_CMD_PARAM_QUERY = const(0b10000000)
SI1145_CMD_PARAM_SET = const(0b10100000)
SI1145_CMD_NOP = const(0b00000000)
SI1145_CMD_RESET = const(0b00000001)
SI1145_CMD_ALS_FORCE = const(0b00000110)

# RAM Parameter Offsets (use with PARAM_QUERY / PARAM_SET)
SI1145_RAM_CHLIST = const(0x01)


class SI1145:
    """Driver for the SI1145 UV, IR, Visible Light Sensor."""

    _device_info = Struct(SI1145_PART_ID, "<BBB")
    _ucoeff_0 = Struct(_COEFF_0, "<B")
    _ucoeff_1 = Struct(_COEFF_1, "<B")
    _ucoeff_2 = Struct(_COEFF_2, "<B")
    _ucoeff_3 = Struct(_COEFF_3, "<B")
    _als_data = Struct(SI1145_ALS_VIS_DATA0, "<HH")
    _aux_data = Struct(SI1145_UV_INDEX_DATA0, "<H")

    def __init__(self, i2c, address=SI1145_DEFAULT_ADDRESS):
        self.i2c_device = i2c_device.I2CDevice(i2c, address)
        dev_id, dev_rev, dev_seq = self.device_info
        if dev_id != 69 or dev_rev != 0 or dev_seq != 8:
            raise RuntimeError("Failed to find SI1145.")
        self.reset()
        self._write_register(SI1145_HW_KEY, 0x17)
        self._als_enabled = True
        self._uv_index_enabled = True
        self.als_enabled = self._als_enabled
        self.uv_index_enabled = self._uv_index_enabled

    @property
    def device_info(self):
        """A three tuple of part, revision, and sequencer ID"""
        return self._device_info

    @property
    def als_enabled(self):
        """The Ambient Light System enabled state."""
        return self._als_enabled

    @als_enabled.setter
    def als_enabled(self, enable):
        chlist = self._param_query(SI1145_RAM_CHLIST)
        if enable:
            chlist |= 0b00110000
        else:
            chlist &= ~0b00110000
        self._param_set(SI1145_RAM_CHLIST, chlist)
        self._als_enabled = enable

    @property
    def als(self):
        """A two tuple of the Ambient Light System (ALS) visible and infrared raw sensor values."""
        self._send_command(SI1145_CMD_ALS_FORCE)
        return self._als_data

    @property
    def uv_index_enabled(self):
        """The UV Index system enabled state"""
        return self._uv_index_enabled

    @uv_index_enabled.setter
    def uv_index_enabled(self, enable):
        chlist = self._param_query(SI1145_RAM_CHLIST)
        if enable:
            chlist |= 0b01000000
        else:
            chlist &= ~0b01000000
        self._param_set(SI1145_RAM_CHLIST, chlist)
        self._als_enabled = enable

        self._ucoeff_0 = 0x00
        self._ucoeff_1 = 0x02
        self._ucoeff_2 = 0x89
        self._ucoeff_3 = 0x29

    @property
    def uv_index(self):
        """The UV Index value"""
        return self._aux_data[0] / 100

    def reset(self):
        """Perform a software reset of the firmware."""
        self._send_command(SI1145_CMD_RESET)
        time.sleep(0.05)  # doubling 25ms datasheet spec

    def clear_error(self):
        """Clear any existing error code."""
        self._send_command(SI1145_CMD_NOP)

    def _param_query(self, param):
        self._send_command(SI1145_CMD_PARAM_QUERY | (param & 0x1F))
        return self._read_register(SI1145_PARAM_RD)

    def _param_set(self, param, value):
        self._write_register(SI1145_PARAM_WR, value)
        self._send_command(SI1145_CMD_PARAM_SET | (param & 0x1F))

    def _send_command(self, command):
        counter = self._read_register(SI1145_RESPONSE) & 0x0F
        self._write_register(SI1145_COMMAND, command)
        if command in (SI1145_CMD_NOP, SI1145_CMD_RESET):
            return 0
        response = self._read_register(SI1145_RESPONSE)
        while counter == response & 0x0F:
            if response & 0xF0:
                raise RuntimeError("SI1145 Error: 0x{:02x}".format(response & 0xF0))
            response = self._read_register(SI1145_RESPONSE)
        return response

    def _read_register(self, register, length=1):
        buffer = bytearray(length)
        with self.i2c_device as i2c:
            i2c.write_then_readinto(bytes([register]), buffer)
        return buffer[0] if length == 1 else buffer

    def _write_register(self, register, buffer):
        if isinstance(buffer, int):
            buffer = bytes([buffer])
        with self.i2c_device as i2c:
            i2c.write(bytes([register]) + buffer)
