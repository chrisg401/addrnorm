# addrnorm

Mailing addresses that mean the same thing get typed a dozen different
ways: "Street" vs "St", "Illinois" vs "IL", extra spaces, a ZIP typed
with or without the +4. If you're deduplicating a spreadsheet of
addresses or comparing user-entered data against a database, those
differences turn identical addresses into apparent mismatches.

addrnorm takes a US address and rewrites it into one consistent
two-line form: street with USPS-style suffix abbreviations, city name
as given, state as a two-letter code, and a validated ZIP.

## Usage

Input is one or more street lines followed by a final "City, State
ZIP" line, read from a file or stdin:

```
$ printf '123 Main Street\nSpringfield, Illinois 62701\n' | python -m addrnorm.cli
123 Main St
Springfield, IL 62701
```

Or from a file:

```
$ cat address.txt
742 Evergreen Terrace
Springfield, IL 62704

$ python -m addrnorm.cli address.txt
742 Evergreen Ter
Springfield, IL 62704
```

State names and abbreviations are both accepted, case-insensitively.
ZIP codes may be 5 digits or ZIP+4. Malformed input exits with status
1 and an error on stderr instead of guessing.

An apartment, suite, or unit line between the street and the
city/state/zip line is folded into the street line, with its
designator abbreviated:

```
$ printf '123 Main Street\nApartment 4B\nSpringfield, IL 62701\n' | python -m addrnorm.cli
123 Main St Apt 4B
Springfield, IL 62701
```

## Library use

The parsing and formatting logic lives in `addrnorm.core` as plain
functions with no I/O, so it can be used directly:

```python
from addrnorm.core import parse_address, format_address

address = parse_address(["123 Main Street", "Springfield, Illinois 62701"])
print(format_address(address))
```

## Status

Early skeleton. Currently handles the common two-line US address
shape only. See the roadmap for what's next.

## Running tests

```
python -m unittest discover
```

## License

MIT, see LICENSE.
