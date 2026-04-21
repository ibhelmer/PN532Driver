from machine import Pin, SPI
from pn532 import PN532, PN532SPITransport

spi = SPI(1, baudrate=1000000, polarity=0, phase=0)
cs = Pin(5, Pin.OUT, value=1)
irq = Pin(6, Pin.IN, Pin.PULL_UP)
rst = Pin(7, Pin.OUT, value=1)

transport = PN532SPITransport(spi, cs=cs, irq=irq, reset=rst)
nfc = PN532(transport, debug=True)

print(nfc.begin())
print(nfc.read_passive_target_id())