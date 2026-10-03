"""Sentence templates for synthetic udhaar transcripts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

EntryType = Literal["credit_given", "payment_received"]
Lang = Literal["hindi", "marathi", "hinglish"]


@dataclass(frozen=True)
class Template:
    id: str
    lang: Lang
    entry_type: EntryType
    # Placeholders: {customer}, {amount}, {note}, {item}
    text: str
    note_from_item: bool = False


# 30+ core templates
TEMPLATES: tuple[Template, ...] = (
    # Hindi credit
    Template("hi_cr_01", "hindi", "credit_given", "{customer} ko {amount} ka samaan diya udhaar"),
    Template("hi_cr_02", "hindi", "credit_given", "{customer} ka {amount} udhaar likh do"),
    Template("hi_cr_03", "hindi", "credit_given", "{amount} rupaye {customer} ji ka udhaar"),
    Template("hi_cr_04", "hindi", "credit_given", "{customer} ko {item} diya {amount} ka udhaar mein"),
    Template("hi_cr_05", "hindi", "credit_given", "udhaar {customer} {amount}"),
    Template("hi_cr_06", "hindi", "credit_given", "{customer} ne {amount} ka maal liya udhaar pe"),
    Template("hi_cr_07", "hindi", "credit_given", "likho {customer} udhaar {amount}"),
    Template("hi_cr_08", "hindi", "credit_given", "{customer} ko {amount} ka bill udhaar"),
    Template("hi_cr_09", "hindi", "credit_given", "aaj {customer} ko {amount} udhaar diya"),
    Template("hi_cr_10", "hindi", "credit_given", "{customer} ji {amount} ka khata badhao"),
    # Hindi payment
    Template("hi_py_01", "hindi", "payment_received", "{customer} ne {amount} diye"),
    Template("hi_py_02", "hindi", "payment_received", "{customer} ji ne {amount} ka payment kiya"),
    Template("hi_py_03", "hindi", "payment_received", "{amount} liye {customer} se"),
    Template("hi_py_04", "hindi", "payment_received", "{customer} ka {amount} hisaab chukta"),
    Template("hi_py_05", "hindi", "payment_received", "aaj ka hisaab chukta kiya {customer} {amount}"),
    Template("hi_py_06", "hindi", "payment_received", "{customer} ne udhaar {amount} clear kiya"),
    Template("hi_py_07", "hindi", "payment_received", "payment received {customer} {amount}"),
    Template("hi_py_08", "hindi", "payment_received", "{customer} se {amount} jama"),
    # Marathi credit
    Template("mr_cr_01", "marathi", "credit_given", "{customer} la {amount} udhaar dile"),
    Template("mr_cr_02", "marathi", "credit_given", "{customer} cha {amount} udhaar liha"),
    Template("mr_cr_03", "marathi", "credit_given", "{amount} rupaye {customer} udhaar"),
    Template("mr_cr_04", "marathi", "credit_given", "{customer} la {item} {amount} la udhaar"),
    Template("mr_cr_05", "marathi", "credit_given", "udhaar {customer} {amount}"),
    Template("mr_cr_06", "marathi", "credit_given", "{customer} ne {amount} che saaman udhaar ghetle"),
    # Marathi payment
    Template("mr_py_01", "marathi", "payment_received", "{customer} ne {amount} dile"),
    Template("mr_py_02", "marathi", "payment_received", "{customer} cha {amount} hisaab band"),
    Template("mr_py_03", "marathi", "payment_received", "{amount} ghetle {customer} kadun"),
    Template("mr_py_04", "marathi", "payment_received", "aaj cha hisaab {customer} {amount}"),
    # Hinglish credit
    Template("he_cr_01", "hinglish", "credit_given", "{customer} ko {amount} ka samaan diya on credit"),
    Template("he_cr_02", "hinglish", "credit_given", "udhaar entry {customer} {amount}"),
    Template("he_cr_03", "hinglish", "credit_given", "{customer} ka {amount} add kar udhaar mein"),
    Template("he_cr_04", "hinglish", "credit_given", "{amount} udhaar for {customer}"),
    Template("he_cr_05", "hinglish", "credit_given", "{customer} liya {item} {amount} udhaar"),
    # Hinglish payment
    Template("he_py_01", "hinglish", "payment_received", "{customer} paid {amount}"),
    Template("he_py_02", "hinglish", "payment_received", "{customer} ne {amount} pay kiya"),
    Template("he_py_03", "hinglish", "payment_received", "received {amount} from {customer}"),
    Template("he_py_04", "hinglish", "payment_received", "{customer} cleared {amount}"),
    # Noisy / filler variants (same semantics)
    Template("hi_cr_n1", "hindi", "credit_given", "uh {customer} ko {amount} udhaar diya haan"),
    Template("hi_cr_n2", "hindi", "credit_given", "{customer} {customer} ko {amount} udhaar"),
    Template("hi_py_n1", "hindi", "payment_received", "umm {customer} ne {amount} diye ji"),
    Template("he_cr_n1", "hinglish", "credit_given", "bas {customer} {amount} udhaar note kar"),
)

ITEM_PHRASES: tuple[str, ...] = (
    "do kilo chawal",
    "doodh ka packet",
    "tel ki bottle",
    "cheeni half kilo",
    "sabun",
    "biscuit ka dabba",
    "masala",
    "aata ek kilo",
    "chai patti",
    "namak",
)

# Held-out template IDs for generalisation test (no overlap with train)
HELD_OUT_TEMPLATE_IDS: frozenset[str] = frozenset(
    {
        "hi_cr_09",
        "hi_cr_10",
        "hi_py_05",
        "hi_py_08",
        "mr_cr_04",
        "mr_cr_06",
        "mr_py_04",
        "he_cr_04",
        "he_cr_05",
        "he_py_03",
        "he_py_04",
        "hi_cr_n2",
        "hi_py_n1",
        "he_cr_n1",
    }
)

TRAIN_TEMPLATE_IDS: frozenset[str] = frozenset(t.id for t in TEMPLATES if t.id not in HELD_OUT_TEMPLATE_IDS)


def get_template(tid: str) -> Template:
    for t in TEMPLATES:
        if t.id == tid:
            return t
    raise KeyError(tid)
