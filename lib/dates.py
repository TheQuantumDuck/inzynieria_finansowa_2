from datetime import date


def year_fraction(start: date, end: date, base: int) -> float:
    return (end - start).days / base
