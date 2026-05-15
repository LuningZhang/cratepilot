from decimal import Decimal

from cratepilot.metadata.adapter import _parse_decimal, _parse_int


def test_parse_int_handles_year_formats():
    assert _parse_int("2024") == 2024
    assert _parse_int("2024-03-10") == 2024
    assert _parse_int("10/12") == 10


def test_parse_decimal_handles_invalid_values():
    assert _parse_decimal("128.5") == Decimal("128.5")
    assert _parse_decimal("abc") is None
    assert _parse_decimal(None) is None
