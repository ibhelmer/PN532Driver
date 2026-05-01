from time import sleep_ms, ticks_ms, ticks_diff
from .errors import PN532TimeoutError, PN532TransportError
from .frame import PN532Frame

class PN532TransportBase:
    """
    Base transport interface for PN532 communication.

    Defines the common API used by the PN532 driver, regardless of
    whether the chip is accessed over I2C, SPI, or UART.
    """
    def __init__(self, irq=None, reset=None, read_buf_size=96):
        self.irq = irq
        self.reset = reset
        self._read_buf_size = read_buf_size

    def hardware_reset(self):
        if self.reset is None:
            return

        self.reset.value(0)
        sleep_ms(10)
        self.reset.value(1)
        sleep_ms(100)

    def wakeup(self):
        pass

    def is_ready(self):
        raise NotImplementedError

    def write_frame(self, frame):
        raise NotImplementedError

    def read_data(self, nbytes):
        raise NotImplementedError

    def wait_ready(self, timeout_ms=1000):
        start = ticks_ms()

        while ticks_diff(ticks_ms(), start) < timeout_ms:
            if self.irq is not None:
                if self.irq.value() == 0:
                    return True
            else:
                if self.is_ready():
                    return True

            sleep_ms(5)

        raise PN532TimeoutError("PN532 not ready")

    def read_ack(self, timeout_ms=100):
        self.wait_ready(timeout_ms)
        data = self.read_data(6)

        if not PN532Frame.is_ack(data):
            raise PN532TransportError("Invalid ACK frame: %r" % data)

        return True

    def read_frame(self, timeout_ms=1000):
        self.wait_ready(timeout_ms)
        raw = self.read_data(self._read_buf_size)
        return PN532Frame.parse(raw)
