import numpy as np
import pytest

from sim.source import bits_to_text, text_to_bits


def test_known_ascii_vector_and_round_trip():
    assert text_to_bits("A").tolist() == [0, 1, 0, 0, 0, 0, 0, 1]
    text = "Linha 1\nLinha 2"
    assert bits_to_text(text_to_bits(text)) == text


def test_non_printable_byte_becomes_question_mark():
    assert bits_to_text(np.zeros(8, dtype=np.uint8)) == "?"


def test_non_ascii_and_partial_byte_are_rejected():
    with pytest.raises(UnicodeEncodeError):
        text_to_bits("ação")
    with pytest.raises(ValueError):
        bits_to_text(np.array([0, 1, 0], dtype=np.uint8))
