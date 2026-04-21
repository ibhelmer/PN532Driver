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