"""NRZ, Manchester and Differential Manchester line coding."""

import numpy as np
from numpy.typing import NDArray

UInt8Array = NDArray[np.uint8]
NAMES = ("nrz", "manchester", "diff_manchester")


def _bits(values: NDArray[np.integer]) -> UInt8Array:
    result = np.asarray(values, dtype=np.uint8)
    if result.ndim != 1 or np.any(result > 1):
        raise ValueError("bits/chips must be a one-dimensional array containing 0 and 1")
    return result


def chips_per_bit(code: str) -> int:
    if code not in NAMES:
        raise KeyError(code)
    return 1 if code == "nrz" else 2


def encode(bits: NDArray[np.integer], code: str) -> UInt8Array:
    """Encode message bits as binary chips."""
    source = _bits(bits)
    if code == "nrz":
        return source.copy()
    if code == "manchester":
        # IEEE convention used by this project: 0 -> 01, 1 -> 10.
        return np.column_stack((source, 1 - source)).ravel().astype(np.uint8)
    if code == "diff_manchester":
        # Always transition in the middle. A zero also transitions at the
        # beginning; a one does not. The shared initial reference is low (0).
        result = np.empty(source.size * 2, dtype=np.uint8)
        previous = 0
        for index, bit in enumerate(source):
            first = previous if bit else 1 - previous
            second = 1 - first
            result[2 * index : 2 * index + 2] = (first, second)
            previous = second
        return result
    raise KeyError(code)


def decode(chips: NDArray[np.integer], code: str) -> tuple[UInt8Array, int]:
    """Decode chips and return message bits plus line-code violations."""
    received = _bits(chips)
    if code == "nrz":
        return received.copy(), 0
    if code not in NAMES:
        raise KeyError(code)
    if received.size % 2:
        raise ValueError("Manchester codes require an even number of chips")

    pairs = received.reshape(-1, 2)
    violations = int(np.count_nonzero(pairs[:, 0] == pairs[:, 1]))
    if code == "manchester":
        # The first chip is also the deterministic hard-decision fallback for
        # violations (00 and 11).
        return pairs[:, 0].copy(), violations

    result = np.empty(pairs.shape[0], dtype=np.uint8)
    previous = 0
    for index, (first, second) in enumerate(pairs):
        result[index] = 1 if first == previous else 0
        previous = int(second)
    return result, violations
