"""Pure functions for normalizing US mailing addresses.

Nothing here touches a filesystem, the network, or stdin/stdout. Every
function takes plain data in and returns plain data out, so the whole
module can be tested without mocking anything.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Full name -> USPS two-letter abbreviation. Keyed lowercase for lookup.
STATE_ABBREVIATIONS = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT",
    "delaware": "DE", "florida": "FL", "georgia": "GA", "hawaii": "HI",
    "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME",
    "maryland": "MD", "massachusetts": "MA", "michigan": "MI",
    "minnesota": "MN", "mississippi": "MS", "missouri": "MO",
    "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM",
    "new york": "NY", "north carolina": "NC", "north dakota": "ND",
    "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode island": "RI", "south carolina": "SC", "south dakota": "SD",
    "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
    "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC",
}

VALID_STATE_CODES = frozenset(STATE_ABBREVIATIONS.values())

# Common USPS street suffix abbreviations. Keyed lowercase, no punctuation.
STREET_SUFFIXES = {
    "avenue": "Ave", "boulevard": "Blvd", "circle": "Cir", "court": "Ct",
    "drive": "Dr", "highway": "Hwy", "lane": "Ln", "loop": "Loop",
    "parkway": "Pkwy", "place": "Pl", "plaza": "Plz", "road": "Rd",
    "square": "Sq", "street": "St", "terrace": "Ter", "trail": "Trl",
    "way": "Way",
}

ZIP_PATTERN = re.compile(r"^\d{5}(-\d{4})?$")
CITY_STATE_ZIP_PATTERN = re.compile(
    r"^(?P<city>.+?),\s*(?P<state>[A-Za-z. ]+?)\s+(?P<zip>[\d-]+)$"
)


@dataclass(frozen=True)
class Address:
    street: str
    city: str
    state: str
    zip_code: str


def normalize_whitespace(text: str) -> str:
    """Collapse runs of whitespace to single spaces and trim the ends."""
    return re.sub(r"\s+", " ", text).strip()


def normalize_state(raw: str) -> str:
    """Return the two-letter USPS abbreviation for a state name or code.

    Accepts either a full name ("Illinois") or an existing abbreviation
    ("IL", case-insensitive). Raises ValueError if neither matches.
    """
    cleaned = normalize_whitespace(raw).rstrip(".")
    if len(cleaned) == 2 and cleaned.upper() in VALID_STATE_CODES:
        return cleaned.upper()
    abbreviation = STATE_ABBREVIATIONS.get(cleaned.lower())
    if abbreviation is None:
        raise ValueError(f"unrecognized state: {raw!r}")
    return abbreviation


def normalize_zip(raw: str) -> str:
    """Validate and return a ZIP code, either 5 digits or ZIP+4."""
    cleaned = normalize_whitespace(raw)
    if not ZIP_PATTERN.match(cleaned):
        raise ValueError(f"invalid zip code: {raw!r}")
    return cleaned


def abbreviate_street_suffix(street_line: str) -> str:
    """Replace a trailing street suffix word with its USPS abbreviation.

    Only the last word is considered, so "Main Street" becomes
    "Main St" but "Street of Dreams" is left alone. Unrecognized
    suffixes (or lines with no trailing word to check) pass through
    unchanged.
    """
    cleaned = normalize_whitespace(street_line)
    if not cleaned:
        return cleaned
    words = cleaned.split(" ")
    last_word = words[-1].strip(".").lower()
    abbreviation = STREET_SUFFIXES.get(last_word)
    if abbreviation is None:
        return cleaned
    words[-1] = abbreviation
    return " ".join(words)


def parse_address(lines: list[str]) -> Address:
    """Parse address lines into an Address.

    Expects at least two non-empty lines: one or more street lines,
    followed by a final "City, State ZIP" line. Raises ValueError if
    the input doesn't fit that shape.
    """
    non_empty = [line for line in lines if normalize_whitespace(line)]
    if len(non_empty) < 2:
        raise ValueError("expected a street line and a city/state/zip line")

    *street_lines, last_line = non_empty
    match = CITY_STATE_ZIP_PATTERN.match(normalize_whitespace(last_line))
    if match is None:
        raise ValueError(f"could not parse city/state/zip from: {last_line!r}")

    street = abbreviate_street_suffix(" ".join(street_lines))
    city = normalize_whitespace(match.group("city"))
    state = normalize_state(match.group("state"))
    zip_code = normalize_zip(match.group("zip"))
    return Address(street=street, city=city, state=state, zip_code=zip_code)


def format_address(address: Address) -> str:
    """Render an Address as a two-line USPS-style string."""
    return f"{address.street}\n{address.city}, {address.state} {address.zip_code}"
