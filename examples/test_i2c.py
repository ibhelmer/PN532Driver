from machine import I2C, Pin
from pn532 import PN532, PN532I2CTransport

i2c = I2C(0, scl=Pin(9), sda=Pin(8))
transport = PN532I2CTransport(i2c)

nfc = PN532(transport)

print(nfc.get_firmware_version())