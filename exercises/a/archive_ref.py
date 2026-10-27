"""Helpers for archive references and access periods.

Practice code for task A. It has no tests yet.
"""

import re
from datetime import date

# Example: RA/EA-4001/F/Fa/L0012
REF = re.compile(r"^([A-Z]{2,3})/([A-Z]{2,3}-\d+)/([A-Z])/([A-Z][a-z])/([A-Z]\d{4})$")

def get_expected_format():
    """Returns a string describing the expected archive reference format."""
    return "Expected format: [Archive(2-3 caps)]/[Creator(2-3 caps-digits)]/[Series(1 cap)]/[Subseries(Cap+lower)]/[Unit(Cap+4 digits)]"

def parse_ref(ref):
    """Split an archive reference into its parts."""
    m = REF.match(ref.strip())
    if not m:
        raise ValueError(f"invalid archive reference: {ref!r}. {get_expected_format()}")
    archive, creator, series, subseries, unit = m.groups()
    return {
        "archive": archive,
        "creator": creator,
        "series": series,
        "subseries": subseries,
        "unit": unit,
    }

def whole_years(start, end):
    """Number of whole years from start to end."""
    if end < start:
        raise ValueError("end is before start")
    years = end.year - start.year
    if (end.month, end.day) < (start.month, start.day):
        years -= 1
    return years

def is_open(created, today=None, years=60):
    """True when a record created on `created` is past its access period."""
    today = today or date.today()
    return whole_years(created, today) >= years

if __name__ == "__main__":
    print(parse_ref("RA/EA-4001/F/Fa/L0012"))
    print(is_open(date(1960, 5, 17), today=date(2020, 5, 17)))
