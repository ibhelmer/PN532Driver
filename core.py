"""
===============================================================================
 Title:        PN532Driver-/core.py
 Description:  Micropython Driver for PN532 NFC/RFID from NXP
               https://github.com/ibhelmer/PN532Driver

 Author:       Ib Helmer Nielsen
 Created:      2026-04-21
 Version:      <0.5.0>

 Hardware:     ESP32-C6, PN532 NFC RFID Wireless Module V3
 Interfaces:   I2C / SPI / UART 
 Dependencies: machine, time, micropython
               Micropython v1.28.0

 License:      MIT 

===============================================================================
 Change Log:
 ------------------------------------------------------------------------------
 Version  Date        Author      Description
 -------  ----------  ----------  --------------------------------------------
 0.5.0    2026-04-21  Ib          Initial version
===============================================================================
"""
from .utils import build_frame

_HOST_TO_PN532 = 0xD4
_PN532_TO_HOST = 0xD5

_CMD_GET_FIRMWARE_VERSION = 0x02
_CMD_SAM_CONFIGURATION = 0x14

class PN532:
    def __init__(self, transport):
        self.transport = transport

    def _command(self, cmd, params=b""):
        payload = bytearray([_HOST_TO_PN532, cmd]) + params
        frame = build_frame(payload)

        self.transport.write_frame(frame)
        self.transport.wait_ready()

        data = self.transport.read_data(64)

        # TODO: implement proper frame parsing
        return data

    def get_firmware_version(self):
        return self._command(_CMD_GET_FIRMWARE_VERSION)

    def sam_configuration(self):
        return self._command(_CMD_SAM_CONFIGURATION, b"\x01\x14\x01")