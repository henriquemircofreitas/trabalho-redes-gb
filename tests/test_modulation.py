import numpy as np
import pytest

from sim import modulation


@pytest.mark.parametrize("name", modulation.NAMES)
def test_modulation_round_trip_and_unit_average_energy(name):
    width = modulation.chips_per_symbol(name)
    labels = np.arange(2**width, dtype=np.uint8)
    shifts = np.arange(width - 1, -1, -1)
    chips = ((labels[:, None] >> shifts) & 1).astype(np.uint8).ravel()
    symbols = modulation.modulate(chips, name)
    np.testing.assert_array_equal(modulation.demodulate(symbols, name), chips)
    assert np.mean(np.abs(modulation.constellation(name)) ** 2) == pytest.approx(1.0)


def test_16qam_nearest_horizontal_and_vertical_neighbours_are_gray():
    points = modulation.constellation("16qam")
    for index, point in enumerate(points):
        distances = np.abs(points - point)
        nearest_distance = np.min(distances[distances > 0])
        neighbours = np.flatnonzero(np.isclose(distances, nearest_distance))
        for neighbour in neighbours:
            assert (index ^ int(neighbour)).bit_count() == 1
