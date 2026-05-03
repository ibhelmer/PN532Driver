# Copyright (c) 2026 Ib Helmer Nielsen
# SPDX-License-Identifier: MIT
from machine import I2C, Pin
from pn532 import PN532, PN532I2CTransport

i2c = I2C(0, scl=Pin(20), sda=Pin(19))
transport = PN532I2CTransport(i2c)

nfc = PN532(transport)

print(nfc.get_firmware_version())