class PN532Error(Exception):
    pass


class PN532TimeoutError(PN532Error):
    pass


class PN532TransportError(PN532Error):
    pass


class PN532ProtocolError(PN532Error):
    pass