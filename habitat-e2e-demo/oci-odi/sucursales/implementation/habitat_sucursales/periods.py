"""Calendar-period behavior from ``transf_obtenerPeriodoExtraer.ktr``."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from typing import Literal


@dataclass(frozen=True, slots=True)
class ProcessingPeriods:
    """Current and previous calendar months in the Pentaho ``yyyyMM`` shape."""

    as_of_date: str
    previous: str
    current: str
    previous_start_date: str
    previous_end_date: str
    current_start_date: str
    current_end_date: str

    def to_dict(self) -> dict[str, str]:
        return {
            "as_of_date": self.as_of_date,
            "previous": self.previous,
            "current": self.current,
            "previous_start_date": self.previous_start_date,
            "previous_end_date": self.previous_end_date,
            "current_start_date": self.current_start_date,
            "current_end_date": self.current_end_date,
        }

    def window(
        self, name: Literal["previous", "current"]
    ) -> dict[str, str]:
        if name not in {"previous", "current"}:
            raise ValueError("window must be 'previous' or 'current'")
        return {
            "window": name,
            "period": getattr(self, name),
            "start_date": getattr(self, f"{name}_start_date"),
            "end_date": getattr(self, f"{name}_end_date"),
        }


def calculate_periods(as_of_date: date | str) -> ProcessingPeriods:
    """Return the current month and its immediate predecessor."""

    parsed_date = _parse_date(as_of_date)
    current = parsed_date.strftime("%Y%m")
    if parsed_date.month == 1:
        previous = f"{parsed_date.year - 1}12"
    else:
        previous = f"{parsed_date.year}{parsed_date.month - 1:02d}"
    previous_start, previous_end = _month_bounds(previous)
    current_start, current_end = _month_bounds(current)
    return ProcessingPeriods(
        as_of_date=parsed_date.isoformat(),
        previous=previous,
        current=current,
        previous_start_date=previous_start,
        previous_end_date=previous_end,
        current_start_date=current_start,
        current_end_date=current_end,
    )


def _parse_date(value: date | str) -> date:
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise TypeError("as_of_date must be a date or ISO date string")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("as_of_date must use YYYY-MM-DD") from exc


def _month_bounds(period: str) -> tuple[str, str]:
    year = int(period[:4])
    month = int(period[4:])
    last_day = calendar.monthrange(year, month)[1]
    return (
        date(year, month, 1).isoformat(),
        date(year, month, last_day).isoformat(),
    )
