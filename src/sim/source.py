"""ASCII source loading and conversion to/from message bits."""

from pathlib import Path

import numpy as np
from numpy.typing import NDArray

UInt8Array = NDArray[np.uint8]


def load_source(path: str | Path = "data/source.txt") -> str:
    """Load a 7-bit ASCII source file without changing its line endings."""
    return Path(path).read_bytes().decode("ascii")


def text_to_bits(text: str) -> UInt8Array:
    """Convert ASCII text to uint8 bits, eight per character, MSB first."""
    raw = np.frombuffer(text.encode("ascii", errors="strict"), dtype=np.uint8)
    return np.unpackbits(raw, bitorder="big")


def bits_to_text(bits: NDArray[np.integer]) -> str:
    """Convert bits to readable ASCII, replacing corrupted bytes with ``?``.

    Newline is accepted because it is present in the source text. A bit count
    that is not a multiple of eight is a protocol error rather than padding.
    """
    values = np.asarray(bits, dtype=np.uint8)
    if values.ndim != 1 or values.size % 8:
        raise ValueError("the number of message bits must be a multiple of 8")
    if np.any(values > 1):
        raise ValueError("bits must contain only 0 and 1")

    raw = np.packbits(values, bitorder="big")
    chars = [chr(int(value)) if value == 10 or 32 <= value <= 126 else "?" for value in raw]
    return "".join(chars)
