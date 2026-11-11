"""End-to-end digital communication link."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from sim import channel, line_codes, modulation, source


@dataclass(frozen=True)
class LinkResult:
    ber: float
    bit_errors: int
    n_bits: int
    error_indices: NDArray[np.int64]
    violations: int
    spectral_efficiency: float
    recovered_text: str
    rx_symbols: NDArray[np.complex128]


def run_link(
    text: str,
    line_code: str,
    modulation_name: str,
    scenario: str,
    ebn0_db: float,
    seed: int,
) -> LinkResult:
    """Run text through the complete transmitter, channel and receiver."""
    message_bits = source.text_to_bits(text)
    tx_chips = line_codes.encode(message_bits, line_code)
    tx_symbols = modulation.modulate(tx_chips, modulation_name)
    eta = modulation.chips_per_symbol(modulation_name) / line_codes.chips_per_bit(line_code)
    rng = np.random.default_rng(seed)
    rx_symbols = channel.transmit(tx_symbols, ebn0_db, eta, scenario, rng)
    rx_chips = modulation.demodulate(rx_symbols, modulation_name)
    recovered_bits, violations = line_codes.decode(rx_chips, line_code)

    error_indices = np.flatnonzero(message_bits != recovered_bits).astype(np.int64)
    bit_errors = int(error_indices.size)
    return LinkResult(
        ber=bit_errors / message_bits.size,
        bit_errors=bit_errors,
        n_bits=int(message_bits.size),
        error_indices=error_indices,
        violations=violations,
        spectral_efficiency=float(eta),
        recovered_text=source.bits_to_text(recovered_bits),
        rx_symbols=rx_symbols,
    )
