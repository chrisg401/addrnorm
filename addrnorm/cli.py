"""Command-line entry point. All I/O lives here so core.py stays pure."""

from __future__ import annotations

import argparse
import sys

from addrnorm.core import format_address, parse_address


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="addrnorm",
        description=(
            "Normalize a US mailing address into a consistent, "
            "USPS-style two-line form."
        ),
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="file with one address line per line; reads stdin if omitted",
    )
    args = parser.parse_args(argv)

    if args.input:
        with open(args.input, encoding="utf-8") as handle:
            text = handle.read()
    else:
        text = sys.stdin.read()

    lines = text.splitlines()
    try:
        address = parse_address(lines)
    except ValueError as error:
        print(f"addrnorm: {error}", file=sys.stderr)
        return 1

    print(format_address(address))
    return 0


if __name__ == "__main__":
    sys.exit(main())
