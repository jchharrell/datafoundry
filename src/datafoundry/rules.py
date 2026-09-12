from __future__ import annotations
import re

STATE_ALIASES = {
    "north carolina": "NC", "n.c.": "NC", "nc": "NC",
    "south carolina": "SC", "s.c.": "SC", "sc": "SC",
    "virginia": "VA", "va": "VA",
}


def normalize_email(value):
    if value is None:
        return None
    value = str(value).strip().lower()
    return value if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value) else None


def normalize_state(value):
    if value is None:
        return None
    key = str(value).strip().lower()
    return STATE_ALIASES.get(key, key.upper() if len(key) == 2 else None)


def valid_age(value) -> bool:
    try:
        age = int(value)
        return 0 <= age <= 120
    except (TypeError, ValueError):
        return False
