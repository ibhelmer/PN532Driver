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

from .frame import PN532Frame
from .constants import (
    HOST_TO_PN532,
    PN532_TO_HOST,
    CMD_GET_FIRMWARE_VERSION,
    CMD_SAM_CONFIGURATION,
)
from .errors import PN532ProtocolError


class PN532:
    def __init__(self, transport, debug=False):
        self.transport = transport
        self.debug = debug

    def reset(self):
        self.transport.hardware_reset()

    def wakeup(self):
        self.transport.wakeup()

    def begin(self):
        try:
            self.reset()
        except Exception:
            pass

        try:
            self.wakeup()
        except Exception:
            pass

        fw = self.get_firmware_version()
        self.sam_configuration()
        return fw
    def in_list_passive_target(self, max_targets=1, baud=0x00):
        return self._command(
            0x4A,                      # InListPassiveTarget
            bytes([max_targets, baud]),
            timeout_ms=1000
        )

    def read_passive_target(self, timeout_ms=2000):
        try:
            data = self._command(
                0x4A,                  # InListPassiveTarget
                bytes([1, 0x00]),      # 1 target, ISO14443A / MIFARE
                timeout_ms=timeout_ms
            )
        except Exception as e:
            if "not ready" in str(e):
                return None
            raise e

        if not data or data[0] == 0:
            return None

        if len(data) < 7:
            raise Exception("Target response too short")

        uid_len = data[5]
        uid = data[6:6 + uid_len]

        return {
            "count": data[0],
            "target": data[1],
            "sens_res": data[2:4],
            "sel_res": data[4],
            "uid": uid,
        }
    
    def _command(self, cmd, params=b"", timeout_ms=1000):
        payload = bytearray(2 + len(params))
        payload[0] = HOST_TO_PN532
        payload[1] = cmd
        payload[2:] = params

        frame = PN532Frame.build(payload)

        self.transport.write_frame(frame)
        self.transport.read_ack(100)

        resp = self.transport.read_frame(timeout_ms)

        if len(resp) < 2:
            raise PN532ProtocolError("Response too short")

        if resp[0] != PN532_TO_HOST:
            raise PN532ProtocolError("Invalid response TFI")

        if resp[1] != ((cmd + 1) & 0xFF):
            raise PN532ProtocolError("Unexpected response code")

        return resp[2:]

    def get_firmware_version(self):
        data = self._command(CMD_GET_FIRMWARE_VERSION)

        if len(data) < 4:
            raise PN532ProtocolError("Firmware response too short")

        return {
            "ic": data[0],
            "ver": data[1],
            "rev": data[2],
            "support": data[3],
        }

    def sam_configuration(self, mode=0x01, timeout=0x14, irq=0x01):
        return self._command(
            CMD_SAM_CONFIGURATION,
            bytes([mode, timeout, irq])
        )