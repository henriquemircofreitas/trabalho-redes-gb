import numpy as np
import pytest

from sim.channel import MEAN_BURST, P_BAD, generate_burst_mask, transmit


def test_awgn_is_reproducible_and_has_expected_power():
    symbols = np.ones(300_000, dtype=np.complex128)
    first = transmit(symbols, 10.0, 1.0, "awgn", np.random.default_rng(42))
    second = transmit(symbols, 10.0, 1.0, "awgn", np.random.default_rng(42))
    np.testing.assert_array_equal(first, second)
    measured_n0 = np.mean(np.abs(first - symbols) ** 2)
    assert measured_n0 == pytest.approx(0.1, rel=0.015)


def test_noiseless_channel_and_burst_statistics():
    symbols = np.array([1, -1, 1], dtype=np.complex128)
    np.testing.assert_array_equal(
        transmit(symbols, float("inf"), 1.0, "awgn", np.random.default_rng(0)), symbols
    )

    mask = generate_burst_mask(2_000_000, np.random.default_rng(7))
    assert mask.mean() == pytest.approx(P_BAD, rel=0.12)
    starts = np.flatnonzero(mask & ~np.r_[False, mask[:-1]])
    ends = np.flatnonzero(mask & ~np.r_[mask[1:], False])
    lengths = ends - starts + 1
    assert lengths.mean() == pytest.approx(MEAN_BURST, rel=0.12)
