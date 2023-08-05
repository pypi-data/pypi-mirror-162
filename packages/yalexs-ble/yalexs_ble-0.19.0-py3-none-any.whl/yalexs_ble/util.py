from dataclasses import dataclass

from bleak import BleakError


def _simple_checksum(buf: bytes) -> int:
    cs = 0
    for i in range(0x12):
        cs = (cs + buf[i]) & 0xFF

    return (-cs) & 0xFF


def _security_checksum(buffer: bytes) -> int:
    val1 = int.from_bytes(buffer[0x00:0x04], byteorder="little", signed=False)
    val2 = int.from_bytes(buffer[0x04:0x08], byteorder="little", signed=False)
    val3 = int.from_bytes(buffer[0x08:0x12], byteorder="little", signed=False)

    return (0 - (val1 + val2 + val3)) & 0xFFFFFFFF


def _copy(dest: bytearray, src: bytes, destLocation: int = 0) -> None:
    dest[destLocation : (destLocation + len(src))] = src  # noqa: E203


def serial_to_local_name(serial: str) -> str:
    """Convert a serial to a local name."""
    return f"{serial[0:2]}{serial[-5:]}"


def local_name_to_serial(serial: str) -> str:
    """Convert a local name to a serial."""
    return f"{serial[0:2]}XXX{serial[2:]}"


def is_disconnected_error(error: Exception) -> bool:
    """Check if the error is a disconnected error."""
    return bool(
        isinstance(error, BleakError)
        and (
            "disconnect" in str(error)
            or "Connection Rejected Due To Security Reasons" in str(error)
        )
    )


@dataclass
class ValidatedLockConfig:
    """A validated lock configuration."""

    name: str
    serial: str
    key: str
    slot: int

    @property
    def local_name(self) -> str:
        """Get the local name from the serial."""
        return serial_to_local_name(self.serial)
