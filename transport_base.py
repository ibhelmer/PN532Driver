from time import sleep_ms, ticks_ms, ticks_diff

class PN532TransportBase:
    """
    Base transport interface for PN532 communication.

    Defines the common API used by the PN532 driver, regardless of
    whether the chip is accessed over I2C, SPI, or UART.
    """
    def __init__(self, irq=None, reset=None):
        self.irq = irq
        self.reset = reset

    def hardware_reset(self):
        if self.reset:
            self.reset.value(0)
            sleep_ms(10)
            self.reset.value(1)
            sleep_ms(100)

    def wait_ready(self, timeout_ms=1000):
        start = ticks_ms()
        while ticks_diff(ticks_ms(), start) < timeout_ms:
            if self.irq:
                if self.irq.value() == 0:
                    return True
            else:
                if self.is_ready():
                    return True
            sleep_ms(5)
        raise Exception("PN532 timeout")

    def is_ready(self):
        raise NotImplementedError

    def write_frame(self, frame):
        raise NotImplementedError

    def read_data(self, nbytes):
        raise NotImplementedError