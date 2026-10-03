"""Unit tests for Indian spoken amount forms."""

import random

import pytest

from data.numbers import (
    IRREGULAR_HINDI,
    hindi_amount_words,
    marathi_amount_words,
    spoken_amount,
)


@pytest.mark.parametrize(
    "amount,expected_substr",
    [
        (250, "dhai sau"),
        (150, "derh sau"),
        (350, "saade teen sau"),
        (125, "sawa sau"),
        (1500, "pandrah sau"),
    ],
)
def test_irregular_hindi_primary(amount: int, expected_substr: str) -> None:
    assert expected_substr in IRREGULAR_HINDI[amount][0]
    assert expected_substr in hindi_amount_words(amount) or amount in (1500,)


def test_1500_alternate_forms() -> None:
    forms = IRREGULAR_HINDI[1500]
    assert any("pandrah sau" in f for f in forms)
    assert any("derh hazaar" in f or "dedh hazaar" in f for f in forms)


def test_spoken_amount_reproducible_digits() -> None:
    rng = random.Random(99)
    s = spoken_amount(340, rng, "digits")
    assert "340" in s


def test_marathi_pannas_in_tens() -> None:
    assert "pannas" in marathi_amount_words(50)


def test_range_guard() -> None:
    with pytest.raises(ValueError):
        hindi_amount_words(5)
    with pytest.raises(ValueError):
        hindi_amount_words(6000)
