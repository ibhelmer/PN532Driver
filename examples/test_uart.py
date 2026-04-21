from machine import Pin, UART
from pn532 import PN532, PN532UARTTransport

uart = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
rst = Pin(6, Pin.OUT, value=1)

transport = PN532UARTTransport(uart, reset=rst)
nfc = PN532(transport, debug=True)

print(nfc.begin())
print(nfc.read_passive_target_id())