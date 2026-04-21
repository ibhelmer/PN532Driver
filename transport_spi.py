from .transport_base import PN532TransportBase

_SPI_DATAWRITE = 0x01
_SPI_DATAREAD  = 0x03
_SPI_STATREAD  = 0x02

class PN532SPITransport(PN532TransportBase):
    """
    SPI transport layer for PN532.

    Handles low-level communication over SPI, including:
    - Writing command/data frames
    - Reading responses
    - Checking device readiness via status reads or IRQ

    Args:
        spi: Initialized machine.SPI instance
        cs (Pin): Chip select pin
        irq (Pin, optional): IRQ pin for ready signal
        reset (Pin, optional): Reset pin for hardware reset
    """
    def __init__(self, spi, cs, irq=None, reset=None):
        super().__init__(irq=irq, reset=reset)
        self.spi = spi
        self.cs = cs
        self.cs.value(1)

    def _select(self):
        self.cs.value(0)

    def _deselect(self):
        self.cs.value(1)

    def is_ready(self):
        self._select()
        self.spi.write(bytes([_SPI_STATREAD]))
        status = self.spi.read(1, 0x00)
        self._deselect()
        return status[0] == 0x01

    def write_frame(self, frame):
        self._select()
        self.spi.write(bytes([_SPI_DATAWRITE]))
        self.spi.write(frame)
        self._deselect()

    def read_data(self, nbytes):
        self._select()
        self.spi.write(bytes([_SPI_DATAREAD]))
        data = self.spi.read(nbytes, 0x00)
        self._deselect()
        return data