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

try:
    from typing import Tuple, Union
    from busio import I2C
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_SI1145.git"

# Registers
_DEFAULT_ADDRESS = const(0x60)
_PART_ID = const(0x00)
_HW_KEY = const(0x07)
_COEFF_0 = const(0x13)
_COEFF_1 = const(0x14)
_COEFF_2 = const(0x15)
_COEFF_3 = const(0x16)
_PARAM_WR = const(0x17)
_COMMAND = const(0x18)
_RESPONSE = const(0x20)
_ALS_VIS_DATA0 = const(0x22)
_UV_INDEX_DATA0 = const(0x2C)
_PARAM_RD = const(0x2E)

# Commands (for COMMAND register)
_CMD_PARAM_QUERY = const(0b10000000)
_CMD_PARAM_SET = const(0b10100000)
_CMD_NOP = const(0b00000000)
_CMD_RESET = const(0b00000001)
_CMD_ALS_FORCE = const(0b00000110)

# RAM Parameter Offsets (use with PARAM_QUERY / PARAM_SET)
_RAM_CHLIST = const(0x01)


class SI1145:
    """Driver for the SI1145 UV, IR, Visible Light Sensor."""

    _device_info = Struct(_PART_ID, "<BBB")
    _ucoeff_0 = Struct(_COEFF_0, "<B")
    _ucoeff_1 = Struct(_COEFF_1, "<B")
    _ucoeff_2 = Struct(_COEFF_2, "<B")
    _ucoeff_3 = Struct(_COEFF_3, "<B")
    _als_data = Struct(_ALS_VIS_DATA0, "<HH")
    _aux_data = Struct(_UV_INDEX_DATA0, "<H")

    def __init__(self, i2c: I2C, address: int = _DEFAULT_ADDRESS) -> None:
        self.i2c_device = i2c_device.I2CDevice(i2c, address)
        dev_id, dev_rev, dev_seq = self.device_info
        if dev_id != 69 or dev_rev != 0 or dev_seq != 8:
            raise RuntimeError("Failed to find SI1145.")
        self.reset()
        self._write_register(_HW_KEY, 0x17)
        self._als_enabled = True
        self._uv_index_enabled = True
        self.als_enabled = self._als_enabled
        self.uv_index_enabled = self._uv_index_enabled

    @property
    def device_info(self) -> Tuple[int, int, int]:
        """A three tuple of part, revision, and sequencer ID"""
        return self._device_info

    @property
    def als_enabled(self) -> bool:
        """The Ambient Light System enabled state."""
        return self._als_enabled

    @als_enabled.setter
    def als_enabled(self, enable: bool) -> None:
        chlist = self._param_query(_RAM_CHLIST)
        if enable:
            chlist |= 0b00110000
        else:
            chlist &= ~0b00110000
        self._param_set(_RAM_CHLIST, chlist)
        self._als_enabled = enable

    @property
    def als(self) -> Tuple[int, int]:
        """A two tuple of the Ambient Light System (ALS) visible and infrared raw sensor values."""
        self._send_command(_CMD_ALS_FORCE)
        return self._als_data

    @property
    def uv_index_enabled(self) -> bool:
        """The UV Index system enabled state"""
        return self._uv_index_enabled

    @uv_index_enabled.setter
    def uv_index_enabled(self, enable: bool) -> None:
        chlist = self._param_query(_RAM_CHLIST)
        if enable:
            chlist |= 0b10000000
        else:
            chlist &= ~0b10000000
        self._param_set(_RAM_CHLIST, chlist)
        self._als_enabled = enable

        self._ucoeff_0 = (0x29,)
        self._ucoeff_1 = (0x89,)
        self._ucoeff_2 = (0x02,)
        self._ucoeff_3 = (0x00,)

        self._uv_index_enabled = enable

    @property
    def uv_index(self) -> float:
        """The UV Index value"""
        self._send_command(_CMD_ALS_FORCE)
        return self._aux_data[0] / 100

    def reset(self) -> None:
        """Perform a software reset of the firmware."""
        self._send_command(_CMD_RESET)
        time.sleep(0.05)  # doubling 25ms datasheet spec

    def clear_error(self) -> None:
        """Clear any existing error code."""
        self._send_command(_CMD_NOP)

    def _param_query(self, param: int) -> int:
        self._send_command(_CMD_PARAM_QUERY | (param & 0x1F))
        return self._read_register(_PARAM_RD)

    def _param_set(self, param: int, value: int) -> None:
        self._write_register(_PARAM_WR, value)
        self._send_command(_CMD_PARAM_SET | (param & 0x1F))

    def _send_command(self, command: int) -> int:
        counter = self._read_register(_RESPONSE) & 0x0F
        self._write_register(_COMMAND, command)
        if command in (_CMD_NOP, _CMD_RESET):
            return 0
        response = self._read_register(_RESPONSE)
        while counter == response & 0x0F:
            if response & 0xF0:
                raise RuntimeError(f"SI1145 Error: {response:#x}")
            response = self._read_register(_RESPONSE)
        return response

    def _read_register(self, register: int, length: int = 1) -> Union[int, bytearray]:
        buffer = bytearray(length)
        with self.i2c_device as i2c:
            i2c.write_then_readinto(bytes([register]), buffer)
        return buffer[0] if length == 1 else buffer

    def _write_register(
        self, register: int, buffer: Union[int, bytes, bytearray]
    ) -> None:
        if isinstance(buffer, int):
            buffer = bytes([buffer])
        with self.i2c_device as i2c:
            i2c.write(bytes([register]) + buffer)
