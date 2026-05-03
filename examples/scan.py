# Copyright (c) 2026 Ib Helmer Nielsen
# SPDX-License-Identifier: MIT
"""
    scan.py
    Scan continuetly for the address of the I2C devices on the bus.

    Print the result
"""
from machine import Pin, I2C
from time import sleep_ms

i2c = I2C(0, scl=Pin(20), sda=Pin(19), freq=100000)

while True:
    devices = i2c.scan()
    print([hex(d) for d in devices])
    sleep_ms(1000)