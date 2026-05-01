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

```text
micropython-pn532/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── manifest.py
├── pyproject.toml
├── .gitignore
│
├── pn532/
│   ├── __init__.py
│   ├── constants.py
│   ├── errors.py
│   ├── utils.py
│   ├── frame.py
│   ├── core.py
│   ├── transport_base.py
│   ├── transport_i2c.py
│   ├── transport_spi.py
│   ├── transport_uart.py
│   ├── mifare.py
│   ├── ntag.py
│   └── ndef.py
│
├── examples/
│   ├── read_card_i2c.py
│   ├── read_card_spi.py
│   ├── read_card_uart.py
│   ├── read_mifare_classic.py
│   ├── read_ntag.py
│   └── write_ndef_text.py
│
├── tests/
│   ├── mock_transport.py
│   ├── test_frame.py
│   ├── test_checksum.py
│   └── test_ndef.py
│
└── docs/
    ├── wiring.md
    ├── api.md
    ├── pn532_frames.md
    ├── link.txt
    └── troubleshooting.md
```
---
## License

Copyright (c) 2026 Ib Helmer Nielsen.

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
---
## Quick Start

### I2C Example

```python
from machine import I2C, Pin
from pn532 import PN532, PN532I2CTransport

i2c = I2C(0, scl=Pin(20), sda=Pin(19), freq=100000)

transport = PN532I2CTransport(i2c, irq=None, reset=None)
nfc = PN532(transport, debug=True)

print(nfc.begin())

card = nfc.read_passive_target()
print(card)