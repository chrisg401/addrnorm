import unittest

from addrnorm.core import (
    Address,
    abbreviate_street_suffix,
    format_address,
    normalize_state,
    normalize_whitespace,
    normalize_zip,
    parse_address,
)


class NormalizeWhitespaceTest(unittest.TestCase):
    def test_collapses_and_trims(self):
        self.assertEqual(normalize_whitespace("  123   Main   St  "), "123 Main St")


class NormalizeStateTest(unittest.TestCase):
    def test_full_name(self):
        self.assertEqual(normalize_state("Illinois"), "IL")

    def test_existing_abbreviation(self):
        self.assertEqual(normalize_state("il"), "IL")

    def test_trailing_period(self):
        self.assertEqual(normalize_state("Ill."), "IL")

    def test_unknown_state_raises(self):
        with self.assertRaises(ValueError):
            normalize_state("Atlantis")


class NormalizeZipTest(unittest.TestCase):
    def test_five_digit(self):
        self.assertEqual(normalize_zip("62701"), "62701")

    def test_zip_plus_four(self):
        self.assertEqual(normalize_zip("62701-1234"), "62701-1234")

    def test_invalid_raises(self):
        with self.assertRaises(ValueError):
            normalize_zip("not-a-zip")


class AbbreviateStreetSuffixTest(unittest.TestCase):
    def test_known_suffix(self):
        self.assertEqual(abbreviate_street_suffix("123 Main Street"), "123 Main St")

    def test_unknown_suffix_unchanged(self):
        self.assertEqual(abbreviate_street_suffix("123 Main"), "123 Main")

    def test_empty_line(self):
        self.assertEqual(abbreviate_street_suffix("   "), "")


class ParseAddressTest(unittest.TestCase):
    def test_two_line_address(self):
        address = parse_address(["123 Main Street", "Springfield, Illinois 62701"])
        self.assertEqual(
            address,
            Address(street="123 Main St", city="Springfield", state="IL", zip_code="62701"),
        )

    def test_ignores_blank_lines(self):
        address = parse_address(["123 Main Street", "", "Springfield, IL 62701"])
        self.assertEqual(address.city, "Springfield")

    def test_too_few_lines_raises(self):
        with self.assertRaises(ValueError):
            parse_address(["Springfield, IL 62701"])

    def test_unparseable_last_line_raises(self):
        with self.assertRaises(ValueError):
            parse_address(["123 Main Street", "Springfield Illinois"])


class FormatAddressTest(unittest.TestCase):
    def test_round_trip(self):
        address = Address(street="123 Main St", city="Springfield", state="IL", zip_code="62701")
        self.assertEqual(format_address(address), "123 Main St\nSpringfield, IL 62701")


if __name__ == "__main__":
    unittest.main()
