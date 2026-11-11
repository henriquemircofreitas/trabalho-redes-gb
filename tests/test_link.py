import math

import pytest

from sim import line_codes, modulation
from sim.link import run_link
from sim.source import load_source


@pytest.mark.parametrize("line_code", line_codes.NAMES)
@pytest.mark.parametrize("modulation_name", modulation.NAMES)
def test_noiseless_end_to_end_recovers_source(line_code, modulation_name):
    text = load_source()
    result = run_link(text, line_code, modulation_name, "awgn", math.inf, seed=0)
    assert result.bit_errors == 0
    assert result.ber == 0.0
    assert result.error_indices.size == 0
    assert result.violations == 0
    assert result.recovered_text == text


def test_noisy_link_identifies_error_indices():
    text = "A short ASCII message. " * 200
    result = run_link(text, "nrz", "bpsk", "awgn", -4.0, seed=3)
    assert result.bit_errors > 0
    assert result.bit_errors == result.error_indices.size
    assert result.n_bits == len(text) * 8
