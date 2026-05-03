# Wiring Guide

This guide shows typical wiring for PN532 NFC modules using MicroPython.

The driver supports

- I2C
- SPI
- UART  HSU

---

## PN532 Interface Mode

Most PN532 breakout boards must be configured for the interface you want to use.

Check the DIP switches or jumpers on your board.

Typical modes

 Interface  Notes 
------
 I2C  Uses SDA, SCL <br>
 SPI  Uses SCK, MOSI, MISO, CS<br> 
 UART  HSU  Uses TX, RX<br> 

 The exact switch positions depend on your PN532 module. Always check the silkscreen or datasheet for your board.<br>
 Example Etechouse NFC Module V3:<br>
 UART Dip 1 On, Dip 2 Off<br>
 I2C Dip 1 On, Dip 2 Off<br>
 SPI Dip 1 off, Dip 2 On<br>
 
---

## I2C Wiring

### Raspberry Pi Pico  RP2040

 PN532  Pico 
------
 VCC  3V3 
 GND  GND 
 SDA  GP8 
 SCL  GP9 

Example

```python
from machine import Pin, I2C

i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100000)
```