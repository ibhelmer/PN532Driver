from .constants import (
    MIFARE_CMD_AUTH_A,
    MIFARE_CMD_AUTH_B,
    MIFARE_CMD_READ,
    MIFARE_CMD_WRITE,
)


class PN532MifareMixin:
    def mifare_classic_auth_block(self, block_number, uid, key, key_type='A', target=1):
        if len(uid) < 4:
            raise ValueError("UID must be at least 4 bytes")
        if len(key) != 6:
            raise ValueError("Key must be 6 bytes")

        cmd = MIFARE_CMD_AUTH_A if key_type == 'A' else MIFARE_CMD_AUTH_B
        data = bytearray(2 + 6 + 4)
        data[0] = cmd
        data[1] = block_number
        data[2:8] = key
        data[8:12] = uid[:4]
        self.in_data_exchange(target, data)
        return True

    def mifare_classic_read_block(self, block_number, target=1):
        data = bytes([MIFARE_CMD_READ, block_number])
        resp = self.in_data_exchange(target, data)
        if len(resp) != 16:
            raise ValueError("Expected 16 bytes, got %d" % len(resp))
        return resp

    def mifare_classic_write_block(self, block_number, block_data, target=1):
        if len(block_data) != 16:
            raise ValueError("Block data must be 16 bytes")
        data = bytearray(18)
        data[0] = MIFARE_CMD_WRITE
        data[1] = block_number
        data[2:] = block_data
        self.in_data_exchange(target, data)
        return True