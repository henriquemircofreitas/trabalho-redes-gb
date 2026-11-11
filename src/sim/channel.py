"""AWGN and two-state burst-noise channels."""

import math

import numpy as np
from numpy.typing import NDArray

ComplexArray = NDArray[np.complex128]

SCENARIOS = ("awgn", "burst")
P_BAD = 0.01
MEAN_BURST = 20.0
BAD_EBN0_DB = 0.0


def generate_burst_mask(n_symbols: int, rng: np.random.Generator) -> NDArray[np.bool_]:
    """Generate a stationary Gilbert-Elliott bad-state mask efficiently."""
    if n_symbols < 0:
        raise ValueError("n_symbols must be non-negative")
    mask = np.zeros(n_symbols, dtype=bool)
    if not n_symbols:
        return mask

    p_bad_to_good = 1.0 / MEAN_BURST
    p_good_to_bad = P_BAD * p_bad_to_good / (1.0 - P_BAD)
    bad = bool(rng.random() < P_BAD)
    position = 0
    while position < n_symbols:
        transition_probability = p_bad_to_good if bad else p_good_to_bad
        run = int(rng.geometric(transition_probability))
        end = min(position + run, n_symbols)
        if bad:
            mask[position:end] = True
        position = end
        bad = not bad
    return mask


def _complex_noise(n: int, n0: float, rng: np.random.Generator) -> ComplexArray:
    if n0 == 0.0:
        return np.zeros(n, dtype=np.complex128)
    sigma = math.sqrt(n0 / 2.0)
    return sigma * (rng.standard_normal(n) + 1j * rng.standard_normal(n))


def transmit(
    symbols: NDArray[np.complexfloating],
    ebn0_db: float,
    bits_per_symbol: float,
    scenario: str,
    rng: np.random.Generator,
) -> ComplexArray:
    """Transmit symbols through AWGN or AWGN plus burst noise.

    Noise is scaled from the *measured* average energy of this symbol stream.
    This keeps Eb/N0 comparable even though ASCII does not use constellation
    labels uniformly.
    """
    if scenario not in SCENARIOS:
        raise KeyError(scenario)
    if bits_per_symbol <= 0:
        raise ValueError("bits_per_symbol must be positive")
    source = np.asarray(symbols, dtype=np.complex128)
    if source.ndim != 1:
        raise ValueError("symbols must be a one-dimensional array")
    if not source.size:
        return source.copy()

    es = float(np.mean(np.abs(source) ** 2))
    gamma = math.inf if math.isinf(ebn0_db) else 10.0 ** (ebn0_db / 10.0)
    n0 = 0.0 if math.isinf(gamma) else es / (bits_per_symbol * gamma)
    received = source + _complex_noise(source.size, n0, rng)

    if scenario == "burst":
        mask = generate_burst_mask(source.size, rng)
        bad_gamma = 10.0 ** (BAD_EBN0_DB / 10.0)
        bad_n0 = es / (bits_per_symbol * bad_gamma)
        burst_noise = _complex_noise(source.size, bad_n0, rng)
        received = received + burst_noise * mask
    return received
