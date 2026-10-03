"""Spoken amount formats for Hindi, Marathi, and digit/rupee styles."""

from __future__ import annotations

import random
import re
from typing import Literal

Lang = Literal["hindi", "marathi", "hinglish", "digits"]

# Core Hindi 1–19, tens, hundreds, thousands
_H_ONES = {
    1: "ek",
    2: "do",
    3: "teen",
    4: "chaar",
    5: "paanch",
    6: "chhe",
    7: "saat",
    8: "aath",
    9: "nau",
    10: "das",
    11: "gyarah",
    12: "barah",
    13: "terah",
    14: "chaudah",
    15: "pandrah",
    16: "solah",
    17: "satrah",
    18: "atharah",
    19: "unnees",
}
_H_TENS = {
    2: "bees",
    3: "tees",
    4: "chaalis",
    5: "pachaas",
    6: "saath",
    7: "sattar",
    8: "assi",
    9: "nabbe",
}
_M_ONES = {
    1: "ek",
    2: "don",
    3: "teen",
    4: "char",
    5: "paach",
    6: "sahaa",
    7: "saat",
    8: "aath",
    9: "nau",
    10: "dahaa",
    11: "akara",
    12: "bara",
    13: "tera",
    14: "chauda",
    15: "pandhra",
    16: "soola",
    17: "satra",
    18: "athara",
    19: "ekunis",
}
_M_TENS = {
    2: "vees",
    3: "tees",
    4: "chaalis",
    5: "pannas",
    6: "saath",
    7: "sattar",
    8: "aasii",
    9: "navvot",
}

IRREGULAR_HINDI: dict[int, tuple[str, ...]] = {
    125: ("sawa sau", "sava sau", "ek sau pachchees"),
    150: ("derh sau", "dedh sau", "ek sau pachaas"),
    175: ("sawa sau pachhattar", "ek sau pachhattar"),
    250: ("dhai sau", "dedh sau do sau", "do sau pachaas"),
    275: ("dhai sau pachhattar",),
    350: ("saade teen sau", "teen sau pachaas"),
    450: ("saade chaar sau", "chaar sau pachaas"),
    550: ("saade paanch sau", "paanch sau pachaas"),
    1500: ("pandrah sau", "derh hazaar", "dedh hazaar", "ek hazaar paanch sau"),
    2500: ("dhai hazaar", "dedh hazaar", "do hazaar paanch sau"),
    3500: ("saade teen hazaar", "teen hazaar paanch sau"),
}

IRREGULAR_MARATHI: dict[int, tuple[str, ...]] = {
    125: ("sava sha", "ek sha pachvis"),
    150: ("der sha", "dedh sha", "ek sha pannas"),
    250: ("dhai sha", "don sha pannas"),
    350: ("saade teen sha", "teen sha pannas"),
    525: ("paachshe", "paanch sha pachvis"),
    1500: ("pandhra sha", "der hazaar"),
}


def _hindi_under_100(n: int) -> str:
    if n < 20:
        return _H_ONES[n]
    tens, ones = divmod(n, 10)
    if ones == 0:
        return _H_TENS[tens]
    return f"{_H_TENS[tens]} {_H_ONES[ones]}"


def _marathi_under_100(n: int) -> str:
    if n < 20:
        return _M_ONES[n]
    tens, ones = divmod(n, 10)
    if ones == 0:
        return _M_TENS[tens]
    return f"{_M_TENS[tens]} {_M_ONES[ones]}"


def hindi_amount_words(n: int) -> str:
    """Canonical Hindi words for integer rupees (10–5000)."""
    if n < 10 or n > 5000:
        raise ValueError(f"amount out of range: {n}")
    if n in IRREGULAR_HINDI:
        return IRREGULAR_HINDI[n][0]
    if n >= 1000:
        thousands, rem = divmod(n, 1000)
        if thousands == 1:
            head = "ek hazaar"
        elif thousands < 20:
            head = f"{_H_ONES[thousands]} hazaar"
        else:
            head = f"{thousands} hazaar"
        if rem == 0:
            return head
        return f"{head} {hindi_amount_words(rem)}"
    if n >= 100:
        hundreds, rem = divmod(n, 100)
        head = f"{_H_ONES[hundreds]} sau" if hundreds > 1 else "ek sau"
        if rem == 0:
            return head
        return f"{head} {_hindi_under_100(rem)}"
    return _hindi_under_100(n)


def marathi_amount_words(n: int) -> str:
    if n < 10 or n > 5000:
        raise ValueError(f"amount out of range: {n}")
    if n in IRREGULAR_MARATHI:
        return IRREGULAR_MARATHI[n][0]
    if n >= 1000:
        thousands, rem = divmod(n, 1000)
        if rem == 0:
            return f"{_M_ONES[thousands]} hazaar"
        th = marathi_amount_words(thousands * 1000).replace(" hazaar", "")
        rest = marathi_amount_words(rem) if rem >= 10 else str(rem)
        return f"{th} hazaar {rest}"
    if n >= 100:
        hundreds, rem = divmod(n, 100)
        head = f"{_M_ONES[hundreds]} sha" if hundreds > 1 else "ek sha"
        if rem == 0:
            return head
        return f"{head} {_marathi_under_100(rem)}"
    return _marathi_under_100(n)


def digit_amount_formats(n: int, rng: random.Random | None = None) -> str:
    r = rng or random.Random(0)
    styles = [
        str(n),
        f"{n} rupaye",
        f"{n} rupees",
        f"₹{n:,}",
        f"Rs {n}",
        f"{n} ka",
    ]
    return r.choice(styles)


def spoken_amount(
    n: int,
    rng: random.Random,
    lang: Lang | None = None,
) -> str:
    """Random spoken or digit format for amount n."""
    if n < 10 or n > 5000:
        raise ValueError(n)
    lang = lang or rng.choice(["hindi", "marathi", "hinglish", "digits"])
    if lang == "digits":
        return digit_amount_formats(n, rng)
    if lang == "marathi":
        if n in IRREGULAR_MARATHI:
            return rng.choice(IRREGULAR_MARATHI[n])
        return marathi_amount_words(n)
    if lang == "hindi":
        if n in IRREGULAR_HINDI:
            return rng.choice(IRREGULAR_HINDI[n])
        return hindi_amount_words(n)
    # hinglish: mix
    if rng.random() < 0.5:
        base = hindi_amount_words(n) if n not in IRREGULAR_HINDI else rng.choice(IRREGULAR_HINDI[n])
        return f"{base} rupees" if rng.random() < 0.5 else base
    return digit_amount_formats(n, rng)


def all_irregular_forms() -> dict[int, set[str]]:
    out: dict[int, set[str]] = {}
    for d, forms in IRREGULAR_HINDI.items():
        out.setdefault(d, set()).update(forms)
    for d, forms in IRREGULAR_MARATHI.items():
        out.setdefault(d, set()).update(forms)
    return out


def normalize_spoken_amount(text: str) -> int | None:
    """Best-effort parse for verification in tests (not production parser)."""
    t = text.lower().strip()
    t = t.replace("₹", "").replace(",", "")
    m = re.search(r"\d+", t)
    if m and "kilo" not in t:
        return int(m.group())
    for amount, forms in sorted(all_irregular_forms().items(), key=lambda x: -x[0]):
        for f in forms:
            if f in t:
                return amount
    return None
