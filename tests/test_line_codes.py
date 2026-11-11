import numpy as np
import pytest

from sim import line_codes


@pytest.mark.parametrize("name", line_codes.NAMES)
def test_line_code_round_trip(name):
    bits = np.array([0, 1, 1, 0, 1, 0, 0, 1], dtype=np.uint8)
    recovered, violations = line_codes.decode(line_codes.encode(bits, name), name)
    np.testing.assert_array_equal(recovered, bits)
    assert violations == 0


def test_known_manchester_vector_and_violations():
    bits = np.array([0, 1], dtype=np.uint8)
    np.testing.assert_array_equal(line_codes.encode(bits, "manchester"), [0, 1, 1, 0])
    recovered, violations = line_codes.decode(np.array([0, 0, 1, 1]), "manchester")
    np.testing.assert_array_equal(recovered, [0, 1])
    assert violations == 2


def test_differential_manchester_detects_missing_midbit_transition():
    recovered, violations = line_codes.decode(np.array([1, 1, 0, 1]), "diff_manchester")
    assert recovered.shape == (2,)
    assert violations == 1


def test_unknown_code_is_rejected():
    with pytest.raises(KeyError):
        line_codes.encode(np.array([0], dtype=np.uint8), "ami")
