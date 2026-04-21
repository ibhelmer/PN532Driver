from .transport_base import PN532TransportBase

class PN532I2CTransport(PN532TransportBase):
    """
    I2C transport layer for PN532.

    Handles low-level communication over I2C, including:
    - Writing PN532 frames (with leading control byte)
    - Reading responses (skipping status byte)
    - Checking device readiness via polling or IRQ

    Args:
        i2c: Initialized machine.I2C instance
        addr (int): I2C address (default 0x24)
        irq (Pin, optional): IRQ pin for ready signal
        reset (Pin, optional): Reset pin for hardware reset
    """ 

    def __init__(self, i2c, addr=0x24, irq=None, reset=None):
        super().__init__(irq=irq, reset=reset)
        self.i2c = i2c
        self.addr = addr

    def is_ready(self):
        try:
            status = self.i2c.readfrom(self.addr, 1)
            return status[0] == 0x01
        except:
            return False

    def write_frame(self, frame):
        buf = bytearray(len(frame) + 1)
        buf[0] = 0x00
        buf[1:] = frame
        self.i2c.writeto(self.addr, buf)

    def read_data(self, nbytes):
        raw = self.i2c.readfrom(self.addr, nbytes + 1)
        return raw[1:]