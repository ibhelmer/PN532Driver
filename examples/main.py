# Copyright (c) 2026 Ib Helmer Nielsen
# SPDX-License-Identifier: MIT
# OLED 0.96" on I2C bus 
from machine import Pin, I2C
import ssd1306
from pn532 import PN532, PN532I2CTransport
from time import sleep_ms

SDA_PIN = 19
SCL_PIN = 20

i2c = I2C(
    0,
    sda=Pin(SDA_PIN),
    scl=Pin(SCL_PIN),
    freq=100000      
)

display = ssd1306.SSD1306_I2C(128, 64, i2c)

def uid_to_hex(uid):
    return ":".join("{:02X}".format(b) for b in uid)

print("Scanning I2C bus",0,1)

devices = i2c.scan()
print("Found:", [hex(d) for d in devices])

if 0x24 not in devices:
    raise RuntimeError("PN532 not found on I2C address 0x24")

transport = PN532I2CTransport(
    i2c,
    addr=0x24,
    irq=None,
    reset=None
)

nfc = PN532(transport)

print("Starting PN532...")
fw = nfc.begin()
print("Firmware:", fw)

print("Hold a card near the reader...")

last_uid = None

while True:
    try:
        card = nfc.read_passive_target(timeout_ms=3000)

        if card:
            display.fill(0)
            uid = bytes(card["uid"])
            display.text("Card detected",0,0,1)
            display.text("UID:",0,9,1)
            uidtxt = uid_to_hex(uid) 
            display.text(uidtxt[:12],0,18,1)
            display.text(uidtxt[-8:],0,27,1)
            print(uidtxt)
    except Exception as e:
        print("Read error:", e)
      
    display.show()
    sleep_ms(2000)