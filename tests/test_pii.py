from app.logging_config import scrub_event
from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_common_vietnamese_phone_formats() -> None:
    phone_numbers = (
        "0901234567",
        "090 123 4567",
        "090.123.4567",
        "090-123-4567",
        "+84 90 123 4567",
    )

    for phone_number in phone_numbers:
        out = scrub_text(f"Contact: {phone_number}")
        assert phone_number not in out
        assert "REDACTED_PHONE_VN" in out


def test_scrub_test_credit_card() -> None:
    card_number = "4111 1111 1111 1111"
    out = scrub_text(f"Test card: {card_number}")
    assert card_number not in out
    assert "REDACTED_CREDIT_CARD" in out


def test_log_processor_scrubs_nested_and_context_values() -> None:
    event = {
        "session_id": "student@vinuni.edu.vn",
        "payload": {"nested": ["Call 090 123 4567"]},
    }

    scrubbed = scrub_event(None, "info", event)

    assert "student@vinuni.edu.vn" not in str(scrubbed)
    assert "090 123 4567" not in str(scrubbed)
