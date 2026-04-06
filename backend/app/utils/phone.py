"""Phone number validation and normalization."""

import phonenumbers


def validate_phone(raw: str) -> tuple[bool, str, str]:
    """
    Validate and normalize a phone number.
    Returns (is_valid, normalized_number, error_message).
    """
    raw = raw.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

    # Ensure + prefix
    if not raw.startswith("+"):
        raw = "+" + raw

    try:
        parsed = phonenumbers.parse(raw, None)
        if not phonenumbers.is_valid_number(parsed):
            return False, raw, "Invalid phone number"
        formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        return True, formatted, ""
    except phonenumbers.NumberParseException as e:
        return False, raw, str(e)
