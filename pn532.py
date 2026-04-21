"""
===============================================================================
 Title:        <Projekt-/filnavn>
 Description:  Micropython Driver for PN532 NFC/RFID from NXP
               https://github.com/ibhelmer/PN532Driver

 Author:       Ib Helmer Nielsen
 Created:      2026-04-21
 Version:      <0.5.0>

 Hardware:     ESP32-C6, PN532 NFC RFID Wireless Module V3
 Interfaces:   I2C / SPI / UART 
 Dependencies: machine, time, micropython
               Micropython v1.28.0

 License:      MIT 

===============================================================================
 Change Log:
 ------------------------------------------------------------------------------
 Version  Date        Author      Description
 -------  ----------  ----------  --------------------------------------------
 0.5.0    2026-04-21  Ib          Initial version
===============================================================================
"""
from micropython import const
from time import sleep_ms, ticks_ms, ticks_diff
from machine import Pin

# =========================
# Exceptions
# =========================

class PN532Error(Exception):
    pass

class PN532TimeoutError(PN532Error):
    pass

class PN532TransportError(PN532Error):
    pass


# =========================
# PN532 constants
# =========================

_PREAMBLE = const(0x00)
_STARTCODE1 = const(0x00)
_STARTCODE2 = const(0xFF)
_POSTAMBLE = const(0x00)

_HOST_TO_PN532 = const(0xD4)
_PN532_TO_HOST = const(0xD5)

# Common commands
_CMD_GET_FIRMWARE_VERSION = const(0x02)
_CMD_SAM_CONFIGURATION    = const(0x14)
_CMD_INLIST_PASSIVE_TARGET = const(0x4A)
_CMD_INDATA_EXCHANGE      = const(0x40)

# SAM modes
_SAM_NORMAL_MODE = const(0x01)

# ACK frame
_ACK_FRAME = b"\x00\x00\xFF\x00\xFF\x00"

# SPI specifics
_SPI_DATAWRITE = const(0x01)
_SPI_DATAREAD  = const(0x03)
_SPI_STATREAD  = const(0x02)

# I2C commonly used 7-bit address for PN532
_I2C_ADDR = const(0x24)


# =========================
# Utility
# =========================

def _checksum(data):
    """
    Calculate checksum for data
    """
    s = 0
    for b in data:
        s += b
    return (-s) & 0xFF


def _build_frame(payload):
    """
    payload includes TFI + CMD + params
    """
    length = len(payload)
    lcs = (-length) & 0xFF
    dcs = _checksum(payload)

    frame = bytearray(8 + length)
    frame[0] = _PREAMBLE
    frame[1] = _STARTCODE1
    frame[2] = _STARTCODE2
    frame[3] = length & 0xFF
    frame[4] = lcs
    frame[5:5+length] = payload
    frame[5+length] = dcs
    frame[6+length] = _POSTAMBLE
    return frame


def _find_frame_start(buf):
    """
    Find 00 00 FF inside a buffer.
    Returns index or -1.
    """
    n = len(buf)
    for i in range(n - 2):
        if buf[i] == 0x00 and buf[i+1] == 0x00 and buf[i+2] == 0xFF:
            return i
    return -1

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
        if self.reset is None:
            return
        self.reset.value(0)
        sleep_ms(10)
        self.reset.value(1)
        sleep_ms(100)

    def wait_ready(self, timeout_ms=1000):
        """
        Default wait: use IRQ if available, otherwise poll is_ready().
        """
        start = ticks_ms()
        while ticks_diff(ticks_ms(), start) < timeout_ms:
            if self.irq is not None:
                # Many breakout boards expose IRQ active-low or active-high differently.
                # Adjust here if needed for your board.
                if self.irq.value() == 0:
                    return True
            else:
                if self.is_ready():
                    return True
            sleep_ms(5)
        raise PN532TimeoutError("PN532 not ready")

    def wakeup(self):
        # Optional override in subclasses if required.
        pass

    def is_ready(self):
        raise NotImplementedError

    def write_frame(self, frame):
        raise NotImplementedError

    def read_data(self, nbytes):
        raise NotImplementedError

    def read_ack(self, timeout_ms=100):
        self.wait_ready(timeout_ms)
        data = self.read_data(len(_ACK_FRAME))
        if data != _ACK_FRAME:
            raise PN532TransportError("Invalid ACK: {}".format(data))
        return True

    def read_frame(self, timeout_ms=1000):
        self.wait_ready(timeout_ms)

        # Read a chunk large enough for typical replies.
        # Can be improved to stream incrementally.
        data = self.read_data(64)

        idx = _find_frame_start(data)
        if idx < 0:
            raise PN532TransportError("No PN532 frame header found")

        data = data[idx:]

        if len(data) < 6:
            raise PN532TransportError("Short frame")

        length = data[3]
        lcs = data[4]
        if ((length + lcs) & 0xFF) != 0:
            raise PN532TransportError("Length checksum error")

        total = 6 + length + 1  # preamble/start + len/lcs + data + dcs + postamble-ish slice handling
        if len(data) < total:
            # Retry with a larger read if transport supports fixed-size polling poorly
            more = self.read_data(128)
            idx2 = _find_frame_start(more)
            if idx2 >= 0:
                data = more[idx2:]
            if len(data) < total:
                raise PN532TransportError("Incomplete response frame")

        payload = data[5:5+length]
        dcs = data[5+length]
        if ((_checksum(payload) + dcs) & 0xFF) != 0:
            raise PN532TransportError("Data checksum error")

        return payload

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
    def __init__(self, i2c, addr=_I2C_ADDR, irq=None, reset=None):
        super().__init__(irq=irq, reset=reset)
        self.i2c = i2c
        self.addr = addr

    def is_ready(self):
        try:
            # PN532 I2C typically returns status byte first.
            status = self.i2c.readfrom(self.addr, 1)
            return len(status) == 1 and status[0] == 0x01
        except Exception:
            return False

    def write_frame(self, frame):
        # Many PN532 I2C implementations require a leading 0x00 host-to-chip write indicator.
        buf = bytearray(len(frame) + 1)
        buf[0] = 0x00
        buf[1:] = frame
        self.i2c.writeto(self.addr, buf)

    def read_data(self, nbytes):
        # For I2C, first byte is often status, remaining bytes are data.
        raw = self.i2c.readfrom(self.addr, nbytes + 1)
        if not raw:
            raise PN532TransportError("I2C empty read")
        if raw[0] != 0x01:
            raise PN532TransportError("I2C not-ready status: 0x{:02X}".format(raw[0]))
        return bytes(raw[1:])

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
        try:
            self.spi.write(bytes([_SPI_STATREAD]))
            status = self.spi.read(1, 0x00)
            if not status:
                return False
            return status[0] == 0x01
        finally:
            self._deselect()

    def write_frame(self, frame):
        self._select()
        try:
            self.spi.write(bytes([_SPI_DATAWRITE]))
            self.spi.write(frame)
        finally:
            self._deselect()

    def read_data(self, nbytes):
        self._select()
        try:
            self.spi.write(bytes([_SPI_DATAREAD]))
            data = self.spi.read(nbytes, 0x00)
            return data
        finally:
            self._deselect()


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

    def wakeup(self):
        # Some boards/modules need a wakeup preamble on HSU.
        # This may vary by module; can be tuned later.
        self.uart.write(b"\x55\x55\x00\x00\x00")
        sleep_ms(10)

    def is_ready(self):
        return self.uart.any() > 0

    def write_frame(self, frame):
        self.uart.write(frame)

    def read_data(self, nbytes):
        start = ticks_ms()
        buf = bytearray()

        while ticks_diff(ticks_ms(), start) < 1000:
            if self.uart.any():
                chunk = self.uart.read()
                if chunk:
                    buf.extend(chunk)
                    if len(buf) >= nbytes:
                        return bytes(buf[:nbytes])
            sleep_ms(2)

        if not buf:
            raise PN532TimeoutError("UART read timeout")
        return bytes(buf)

class PN532:
    """
    Driver for PN532 NFC controller.
    Supports communication with0 I2C, SPI and UART.

    Args:
        interface (str): Communicationinterface ('i2c', 'spi', 'uart').
        debug (bool): Activate debug output.

    Attributes:
        interface: Active communication interface.
        debug (bool): Debug flag.
    """
    def __init__(self, transport, debug=False):
        self.transport = transport
        self.debug = debug

    def _log(self, *args):
        if self.debug:
            print("[PN532]", *args)

    def _command(self, cmd, params=b"", timeout_ms=1000):
        payload = bytearray(2 + len(params))
        payload[0] = _HOST_TO_PN532
        payload[1] = cmd
        payload[2:] = params

        frame = _build_frame(payload)

        self._log("TX payload:", payload)
        self.transport.write_frame(frame)

        # ACK
        self.transport.read_ack(timeout_ms=100)

        # Response frame
        resp = self.transport.read_frame(timeout_ms=timeout_ms)
        self._log("RX payload:", resp)

        if len(resp) < 2:
            raise PN532TransportError("Response too short")

        if resp[0] != _PN532_TO_HOST:
            raise PN532TransportError("Invalid response TFI")

        if resp[1] != (cmd + 1):
            raise PN532TransportError(
                "Unexpected response code 0x{:02X}, expected 0x{:02X}".format(
                    resp[1], (cmd + 1) & 0xFF
                )
            )

        return resp[2:]

    def wakeup(self):
        self.transport.wakeup()

    def reset(self):
        self.transport.hardware_reset()

    def begin(self):
        self.reset()
        sleep_ms(100)
        try:
            self.wakeup()
        except Exception:
            pass
        sleep_ms(50)

        fw = self.get_firmware_version()
        self.sam_configuration()
        return fw

    def get_firmware_version(self):
        data = self._command(_CMD_GET_FIRMWARE_VERSION)
        if len(data) < 4:
            raise PN532TransportError("Firmware response too short")
        return {
            "ic": data[0],
            "ver": data[1],
            "rev": data[2],
            "support": data[3],
        }

    def sam_configuration(self, mode=_SAM_NORMAL_MODE, timeout=0x14, irq=0x01):
        # Typical normal mode init
        return self._command(
            _CMD_SAM_CONFIGURATION,
            bytes([mode, timeout, irq])
        )

    def in_list_passive_target(self, max_targets=1, baud=0x00):
        # baud=0x00 => 106 kbps, common for Mifare/ISO14443A
        data = self._command(
            _CMD_INLIST_PASSIVE_TARGET,
            bytes([max_targets, baud]),
            timeout_ms=1000
        )
        return data

    def read_passive_target_id(self):
        data = self.in_list_passive_target(1, 0x00)

        if not data or data[0] == 0:
            return None

        # Typical layout:
        # NbTg, Tg, SENS_RES(2), SEL_RES(1), NFCIDLen(1), NFCID(...)
        if len(data) < 7:
            return data

        uid_len = data[5]
        uid = data[6:6+uid_len]

        return {
            "count": data[0],
            "target": data[1],
            "sens_res": data[2:4],
            "sel_res": data[4],
            "uid": uid,
        }