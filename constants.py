try:
    from micropython import const
except ImportError:
    def const(x):
        return x

PREAMBLE = const(0x00)
STARTCODE1 = const(0x00)
STARTCODE2 = const(0xFF)
POSTAMBLE = const(0x00)

HOST_TO_PN532 = const(0xD4)
PN532_TO_HOST = const(0xD5)

ACK_FRAME = b"\x00\x00\xFF\x00\xFF\x00"
NACK_FRAME = b"\x00\x00\xFF\xFF\x00\x00"

I2C_ADDR = const(0x24)

SPI_DATAWRITE = const(0x01)
SPI_DATAREAD = const(0x03)
SPI_STATREAD = const(0x02)

CMD_GET_FIRMWARE_VERSION = const(0x02)
CMD_SAM_CONFIGURATION = const(0x14)
CMD_INLIST_PASSIVE_TARGET = const(0x4A)
CMD_INDATA_EXCHANGE = const(0x40)
CMD_RF_CONFIGURATION = const(0x32)

SAM_NORMAL_MODE = const(0x01)

MIFARE_CMD_AUTH_A = const(0x60)
MIFARE_CMD_AUTH_B = const(0x61)
MIFARE_CMD_READ = const(0x30)
MIFARE_CMD_WRITE = const(0xA0)

ULTRALIGHT_CMD_READ = const(0x30)
ULTRALIGHT_CMD_WRITE = const(0xA2)