"""Smoke tests for synthetic dataset splits."""

import json
from pathlib import Path

from data.names import split_train_test_names
from data.templates import HELD_OUT_TEMPLATE_IDS, TRAIN_TEMPLATE_IDS

OUT = Path(__file__).resolve().parents[1] / "data" / "out"


def _load(name: str) -> list[dict]:
    path = OUT / f"{name}.jsonl"
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def test_output_counts_when_generated() -> None:
    train, val, test, unseen = (
        _load("train"),
        _load("val"),
        _load("test"),
        _load("test_unseen"),
    )
    if not train:
        return  # skip if generate.py not run in CI yet
    assert len(train) == 4000
    assert len(val) == 300
    assert len(test) == 400
    assert len(unseen) == 120


def test_unseen_generalisation_constraints() -> None:
    unseen = _load("test_unseen")
    if not unseen:
        return
    _, held_names = split_train_test_names(42)
    for row in unseen:
        assert row["first_name"] in held_names
        assert row["template_id"] in HELD_OUT_TEMPLATE_IDS


def test_train_templates_not_held_out() -> None:
    train = _load("train")
    if not train:
        return
    for row in train:
        tid = row["template_id"]
        if tid.startswith("edge"):
            continue
        assert tid in TRAIN_TEMPLATE_IDS
