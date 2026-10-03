from app.heuristic_parser import parse_transcript_heuristic


def test_correction_amount():
    label = parse_transcript_heuristic(
        "Ramesh ji ko 240 ka samaan nahi 240 nahi 340 udhaar"
    )
    assert label["amount"] == 340


def test_payment_phrase():
    label = parse_transcript_heuristic("Suresh ji ne 200 diye aaj ka hisaab chukta kiya")
    assert label["type"] == "payment_received"
    assert label["amount"] == 200


def test_missing_amount():
    label = parse_transcript_heuristic("Ramesh ji ka udhaar likho")
    assert label["amount"] is None
    assert label["error"] == "missing_amount"
