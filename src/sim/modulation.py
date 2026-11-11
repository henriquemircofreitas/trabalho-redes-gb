"""Gray-labelled BPSK, QPSK and 16-QAM modulation."""

import numpy as np
from numpy.typing import NDArray

UInt8Array = NDArray[np.uint8]
ComplexArray = NDArray[np.complex128]
NAMES = ("bpsk", "qpsk", "16qam")


def _build_constellations() -> dict[str, ComplexArray]:
    bpsk = np.array([1.0, -1.0], dtype=np.complex128)
    qpsk = np.array(
        [1 + 1j, 1 - 1j, -1 + 1j, -1 - 1j], dtype=np.complex128
    ) / np.sqrt(2.0)

    # Two-bit Gray labels: 00, 01, 11, 10 on each axis from -3 to +3.
    gray_level = {(0, 0): -3, (0, 1): -1, (1, 1): 1, (1, 0): 3}
    qam = []
    for index in range(16):
        label = tuple((index >> shift) & 1 for shift in (3, 2, 1, 0))
        qam.append(gray_level[label[:2]] + 1j * gray_level[label[2:]])
    qam16 = np.asarray(qam, dtype=np.complex128) / np.sqrt(10.0)
    return {"bpsk": bpsk, "qpsk": qpsk, "16qam": qam16}


_CONSTELLATIONS = _build_constellations()


def chips_per_symbol(mod: str) -> int:
    if mod not in _CONSTELLATIONS:
        raise KeyError(mod)
    return {"bpsk": 1, "qpsk": 2, "16qam": 4}[mod]


def constellation(mod: str) -> ComplexArray:
    try:
        return _CONSTELLATIONS[mod].copy()
    except KeyError:
        raise KeyError(mod) from None


def modulate(chips: NDArray[np.integer], mod: str) -> ComplexArray:
    """Map binary chips to complex symbols."""
    table = constellation(mod)
    values = np.asarray(chips, dtype=np.uint8)
    width = chips_per_symbol(mod)
    if values.ndim != 1 or np.any(values > 1):
        raise ValueError("chips must be a one-dimensional array containing 0 and 1")
    if values.size % width:
        raise ValueError(f"chip count must be divisible by {width} for {mod}")
    groups = values.reshape(-1, width)
    weights = 1 << np.arange(width - 1, -1, -1)
    indices = groups @ weights
    return table[indices]


def demodulate(symbols: NDArray[np.complexfloating], mod: str) -> UInt8Array:
    """Nearest-neighbour hard decision, returned as binary chips."""
    table = constellation(mod)
    received = np.asarray(symbols, dtype=np.complex128)
    if received.ndim != 1:
        raise ValueError("symbols must be a one-dimensional array")
    indices = np.argmin(np.abs(received[:, None] - table[None, :]) ** 2, axis=1)
    width = chips_per_symbol(mod)
    shifts = np.arange(width - 1, -1, -1)
    return ((indices[:, None] >> shifts) & 1).astype(np.uint8).ravel()
