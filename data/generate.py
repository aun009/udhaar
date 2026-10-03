#!/usr/bin/env python3
"""Generate synthetic (transcript, label) JSONL for udhaar parser training."""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from pathlib import Path

from data.names import (
    format_customer_name,
    maybe_variant_name,
    split_train_test_names,
)
from data.numbers import spoken_amount
from data.schema import label_to_json, make_label
from data.templates import (
    HELD_OUT_TEMPLATE_IDS,
    ITEM_PHRASES,
    TRAIN_TEMPLATE_IDS,
    TEMPLATES,
    Template,
)

SEED = 42
AMOUNTS_POOL = sorted(
    {
        *range(10, 100, 5),
        125,
        150,
        175,
        250,
        275,
        350,
        450,
        550,
        *range(100, 1000, 50),
        1500,
        1750,
        2000,
        2500,
        3500,
        4000,
        5000,
    }
)
OUT_DIR = Path(__file__).resolve().parent / "out"


@dataclass
class Example:
    transcript: str
    label: dict
    template_id: str
    first_name: str
    split_hint: str


def _num_lang(t: Template, rng: random.Random) -> str:
    if t.lang == "marathi":
        return rng.choice(["marathi", "marathi", "digits"])
    if t.lang == "hindi":
        return rng.choice(["hindi", "hindi", "digits"])
    return rng.choice(["hinglish", "hindi", "digits"])


def _render(
    rng: random.Random,
    t: Template,
    customer: str,
    amount: int,
    note: str | None,
) -> tuple[str, str | None]:
    item = note or rng.choice(ITEM_PHRASES)
    amt_str = spoken_amount(amount, rng, _num_lang(t, rng))  # type: ignore[arg-type]
    transcript = t.text.format(customer=customer, amount=amt_str, note=note or "", item=item)
    if "{item}" in t.text or t.note_from_item:
        note = item
    return transcript.strip(), note


def _asr_noise(rng: random.Random, transcript: str) -> str:
    if rng.random() < 0.15:
        transcript = transcript.replace(" ji ", " ")
    if rng.random() < 0.1:
        transcript = f"uh {transcript}"
    if rng.random() < 0.08:
        transcript += " haan"
    return transcript


def normal_example(rng: random.Random, t: Template, first_name: str) -> Example:
    first = maybe_variant_name(rng, first_name)
    customer = format_customer_name(rng, first)
    amount = rng.choice(AMOUNTS_POOL)
    note: str | None = rng.choice(ITEM_PHRASES) if rng.random() < 0.25 else None
    transcript, note = _render(rng, t, customer, amount, note)
    transcript = _asr_noise(rng, transcript)
    return Example(
        transcript=transcript,
        label=make_label(
            customer=customer,
            amount=amount,
            entry_type=t.entry_type,
            note=note,
            error=None,
        ),
        template_id=t.id,
        first_name=first_name,
        split_hint="normal",
    )


def edge_examples(rng: random.Random, first_name: str) -> Example:
    kind = rng.randint(0, 4)
    customer = format_customer_name(rng, maybe_variant_name(rng, first_name))

    if kind == 0:
        a1, a2 = rng.sample(AMOUNTS_POOL, 2)
        final = max(a1, a2)
        t1, t2 = spoken_amount(a1, rng, "hindi"), spoken_amount(a2, rng, "hindi")
        transcript = f"{customer} ko {t1} udhaar nahi {t2} udhaar"
        label = make_label(customer=customer, amount=final, entry_type="credit_given")
        tid = "edge_dup_amount"
    elif kind == 1:
        transcript = f"{customer} ko 240 ka samaan nahi 240 nahi 340 udhaar"
        label = make_label(customer=customer, amount=340, entry_type="credit_given")
        tid = "edge_correction"
    elif kind == 2:
        item = rng.choice(ITEM_PHRASES)
        price = rng.choice([80, 120, 150, 200, 340])
        transcript = f"{customer} ko 2 kilo samaan, {price} ka udhaar {item}"
        label = make_label(
            customer=customer, amount=price, entry_type="credit_given", note=item
        )
        tid = "edge_quantity"
    elif kind == 3:
        transcript = f"{customer} ka udhaar likho"
        label = make_label(
            customer=customer,
            amount=None,
            entry_type="credit_given",
            error="missing_amount",
        )
        tid = "edge_no_amount"
    else:
        amt = rng.choice(AMOUNTS_POOL)
        amt_s = spoken_amount(amt, rng, "hindi")
        transcript = f"{customer} ne {amt_s} diye aaj ka hisaab chukta kiya"
        label = make_label(
            customer=customer, amount=amt, entry_type="payment_received"
        )
        tid = "edge_payment_phrase"

    return Example(
        transcript=transcript,
        label=label,
        template_id=tid,
        first_name=first_name,
        split_hint="edge",
    )


def row(ex: Example, split: str) -> dict:
    return {
        "transcript": ex.transcript,
        "label": ex.label,
        "label_json": label_to_json(ex.label),
        "split": split,
        "template_id": ex.template_id,
        "first_name": ex.first_name,
        "meta": {"split_hint": ex.split_hint},
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def generate_all(seed: int = SEED) -> dict:
    rng = random.Random(seed)
    train_names, held_names = split_train_test_names(seed)
    train_templates = [t for t in TEMPLATES if t.id in TRAIN_TEMPLATE_IDS]
    unseen_templates = [t for t in TEMPLATES if t.id in HELD_OUT_TEMPLATE_IDS]

    n_train, n_val = 4000, 300
    n_test = 400
    n_unseen = int(n_test * 0.30)  # 120
    n_test_seen = n_test - n_unseen
    n_edge_train, n_edge_val, n_edge_test = 50, 10, 20

    train_rows: list[dict] = []
    val_rows: list[dict] = []
    test_seen: list[dict] = []
    test_unseen: list[dict] = []

    def fill(count: int, split: str, dest: list[dict], *, train_name: bool) -> None:
        names = list(train_names if train_name else held_names)
        templates = train_templates if train_name else unseen_templates
        while len(dest) < count:
            t = rng.choice(templates)
            name = rng.choice(names)
            dest.append(row(normal_example(rng, t, name), split))

    fill(n_train - n_edge_train, "train", train_rows, train_name=True)
    fill(n_val - n_edge_val, "val", val_rows, train_name=True)
    fill(n_test_seen - n_edge_test, "test", test_seen, train_name=True)
    fill(n_unseen, "test_unseen", test_unseen, train_name=False)

    for _ in range(n_edge_train):
        train_rows.append(row(edge_examples(rng, rng.choice(list(train_names))), "train"))
    for _ in range(n_edge_val):
        val_rows.append(row(edge_examples(rng, rng.choice(list(train_names))), "val"))
    for _ in range(n_edge_test):
        test_seen.append(row(edge_examples(rng, rng.choice(list(train_names))), "test"))

    rng.shuffle(train_rows)
    rng.shuffle(val_rows)
    rng.shuffle(test_seen)
    rng.shuffle(test_unseen)

    test_all = test_seen + test_unseen
    rng.shuffle(test_all)

    stats = {
        "seed": seed,
        "train": len(train_rows),
        "val": len(val_rows),
        "test": len(test_all),
        "test_seen": len(test_seen),
        "test_unseen": len(test_unseen),
        "held_out_first_names": len(held_names),
        "held_out_template_ids": len(HELD_OUT_TEMPLATE_IDS),
        "template_count": len(TEMPLATES),
    }
    return {
        "stats": stats,
        "train": train_rows,
        "val": val_rows,
        "test": test_all,
        "test_unseen_only": test_unseen,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    data = generate_all(args.seed)
    out = args.out_dir
    write_jsonl(out / "train.jsonl", data["train"])
    write_jsonl(out / "val.jsonl", data["val"])
    write_jsonl(out / "test.jsonl", data["test"])
    write_jsonl(out / "test_unseen.jsonl", data["test_unseen_only"])
    with (out / "stats.json").open("w", encoding="utf-8") as f:
        json.dump(data["stats"], f, indent=2)
    print(json.dumps(data["stats"], indent=2))


if __name__ == "__main__":
    main()
