from .constants import PREAMBLE, STARTCODE1, STARTCODE2, POSTAMBLE, ACK_FRAME, NACK_FRAME
from .errors import PN532ProtocolError
from .utils import checksum


from .constants import ACK_FRAME
from .errors import PN532ProtocolError


class PN532Frame:
    @staticmethod
    def build(payload):
        length = len(payload)
        lcs = (-length) & 0xFF

        s = 0
        for b in payload:
            s += b
        dcs = (-s) & 0xFF

        frame = bytearray(length + 8)
        frame[0] = 0x00
        frame[1] = 0x00
        frame[2] = 0xFF
        frame[3] = length
        frame[4] = lcs
        frame[5:5 + length] = payload
        frame[5 + length] = dcs
        frame[6 + length] = 0x00

        return frame

    @staticmethod
    def is_ack(data):
        return data == ACK_FRAME

    @staticmethod
    def parse(data):
        idx = -1

        for i in range(len(data) - 2):
            if data[i] == 0x00 and data[i + 1] == 0x00 and data[i + 2] == 0xFF:
                idx = i
                break

        if idx < 0:
            raise PN532ProtocolError("Frame header not found")

        data = data[idx:]

        if len(data) < 8:
            raise PN532ProtocolError("Frame too short")

        length = data[3]
        lcs = data[4]

        if ((length + lcs) & 0xFF) != 0:
            raise PN532ProtocolError("Length checksum error")

        payload = data[5:5 + length]
        dcs = data[5 + length]

        total = dcs
        for b in payload:
            total += b

        if (total & 0xFF) != 0:
            raise PN532ProtocolError("Data checksum error")

        return payload