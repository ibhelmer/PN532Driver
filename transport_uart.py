from .transport_base import PN532TransportBase
from time import ticks_ms, ticks_diff, sleep_ms

class PN532UARTTransport(PN532TransportBase):
    """
    UART transport layer for PN532.

    Handles low-level communication over UART/HSU, including:
    - Writing command frames
    - Reading responses
    - Detecting available incoming data
    - Optional wakeup handling

    Args:
        uart: Initialized machine.UART instance
        irq (Pin, optional): IRQ pin for ready signal
        reset (Pin, optional): Reset pin for hardware reset
    """
    def __init__(self, uart, irq=None, reset=None):
        super().__init__(irq=irq, reset=reset)
        self.uart = uart

    def is_ready(self):
        return self.uart.any() > 0

    def write_frame(self, frame):
        self.uart.write(frame)

    def read_data(self, nbytes):
        start = ticks_ms()
        buf = bytearray()

        while ticks_diff(ticks_ms(), start) < 1000:
            if self.uart.any():
                buf.extend(self.uart.read())
                if len(buf) >= nbytes:
                    return buf[:nbytes]
            sleep_ms(2)

        return buf