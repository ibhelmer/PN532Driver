def checksum(data, start=0, end=None):
    """
    Calculate checksum for data from start
    """
    if end is None:
        end = len(data)
    s = 0
    for i in range(start, end):
        s += data[i]
    return (-s) & 0xFF


def build_frame(payload):
    """
    payload includes TFI + CMD + params
    """
    length = len(payload)
    lcs = (-length) & 0xFF
    dcs = checksum(payload)

    frame = bytearray(8 + length)
    frame[0] = 0x00
    frame[1] = 0x00
    frame[2] = 0xFF
    frame[3] = length
    frame[4] = lcs
    frame[5:5+length] = payload
    frame[5+length] = dcs
    frame[6+length] = 0x00
    return frame

def u16_be(msb, lsb):
    return (msb << 8) | lsb