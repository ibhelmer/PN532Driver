# PN532 MicroPython Driver

A modular, memory-conscious MicroPython driver for the PN532 NFC controller supporting:

- I2C, SPI and UART (HSU)
- Full frame parsing (ACK + checksum validation)
- MIFARE Classic (read/write/auth)
- NTAG / Ultralight support
- Basic NDEF read/write (text records)
- Testable architecture with mock transport

---

## Features

### Core functionality
- PN532 command/response handling
- Full frame parsing with checksum validation
- Automatic ACK handling
- Transport abstraction layer

### Supported interfaces
- I2C (default address `0x24`)
- SPI (with status polling)
- UART (HSU mode)

### NFC support
- ISO14443A tag detection
- MIFARE Classic:
  - Authentication (Key A / B)
  - Block read/write
- NTAG / Ultralight:
  - Page read/write
- NDEF:
  - Read TLV messages
  - Write simple text records

---

## Project Structure
pn532/<br>
├── core.py # PN532 protocol logic<br>
├── frame.py # Frame build/parse (ACK + checksum)<br>
├── constants.py # Command + protocol constants<br>
├── utils.py # Helper functions<br>
├── errors.py # Custom exceptions<br>
├── transport_base.py # Abstract transport layer<br>
├── transport_i2c.py # I2C implementation<br>
├── transport_spi.py # SPI implementation<br>
├── transport_uart.py # UART implementation<br>
├── mifare.py # MIFARE Classic support<br>
├── ntag.py # NTAG / Ultralight support<br>
├── ndef.py # NDEF helper<br>
└── tests/
>	├── mock_transport.py<br>
>	└── test_frame.py<br>


---

## Quick Start

### I2C Example

```python
from machine import I2C, Pin
from pn532 import PN532, PN532I2CTransport

i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)
irq = Pin(10, Pin.IN, Pin.PULL_UP)
rst = Pin(11, Pin.OUT, value=1)

transport = PN532I2CTransport(i2c, irq=irq, reset=rst)
nfc = PN532(transport, debug=True)

print(nfc.begin())

card = nfc.read_passive_target()
print(card)