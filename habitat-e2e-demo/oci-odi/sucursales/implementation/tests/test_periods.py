import pytest

from datetime import date

from habitat_sucursales.periods import calculate_periods


def test_calculate_periods_uses_current_and_previous_calendar_month() -> None:
    periods = calculate_periods(date(2026, 7, 15))

    assert periods.as_of_date == "2026-07-15"
    assert periods.previous == "202606"
    assert periods.current == "202607"
    assert periods.to_dict() == {
        "as_of_date": "2026-07-15",
        "previous": "202606",
        "current": "202607",
        "previous_start_date": "2026-06-01",
        "previous_end_date": "2026-06-30",
        "current_start_date": "2026-07-01",
        "current_end_date": "2026-07-31",
    }
    assert periods.window("previous") == {
        "window": "previous",
        "period": "202606",
        "start_date": "2026-06-01",
        "end_date": "2026-06-30",
    }
    assert periods.window("current") == {
        "window": "current",
        "period": "202607",
        "start_date": "2026-07-01",
        "end_date": "2026-07-31",
    }


def test_calculate_periods_rolls_back_across_year_boundary() -> None:
    periods = calculate_periods("2026-01-01")

    assert periods.previous == "202512"
    assert periods.current == "202601"
    assert periods.previous_start_date == "2025-12-01"
    assert periods.previous_end_date == "2025-12-31"


def test_calculate_periods_handles_leap_year_month_end() -> None:
    periods = calculate_periods("2024-03-20")

    assert periods.previous == "202402"
    assert periods.previous_end_date == "2024-02-29"


def test_calculate_periods_rejects_invalid_date() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        calculate_periods("2026-02-30")
