import unittest
from datetime import date
from archive_ref import parse_ref, whole_years, is_open

class TestArchiveRef(unittest.TestCase):

    def test_parse_ref_valid(self):
        ref = "RA/EA-4001/F/Fa/L0012"
        expected = {
            "archive": "RA",
            "creator": "EA-4001",
            "series": "F",
            "subseries": "Fa",
            "unit": "L0012",
        }
        self.assertEqual(parse_ref(ref), expected)

    def test_parse_ref_valid_spaces(self):
        ref = "  RA/EA-4001/F/Fa/L0012  "
        expected = {
            "archive": "RA",
            "creator": "EA-4001",
            "series": "F",
            "subseries": "Fa",
            "unit": "L0012",
        }
        self.assertEqual(parse_ref(ref), expected)

    def test_parse_ref_invalid(self):
        invalid_refs = [
            "ra/EA-4001/F/Fa/L0012",  # Lowercase archive
            "RA/ea-4001/F/Fa/L0012",  # Lowercase creator
            "R/EA-4001/F/Fa/L0012",   # Too short archive
            "RA/EA-4001/F/Fa/L12",    # Too short unit
            "RA/EA-4001/F/Fa",        # Missing unit
            "nonsense",               # Totally wrong
        ]
        for ref in invalid_refs:
            with self.subTest(ref=ref):
                with self.assertRaises(ValueError):
                    parse_ref(ref)

    def test_whole_years_normal(self):
        self.assertEqual(whole_years(date(2000, 1, 1), date(2010, 1, 1)), 10)
        self.assertEqual(whole_years(date(2000, 1, 1), date(2010, 1, 2)), 10)

    def test_whole_years_boundary(self):
        start = date(2000, 1, 1)
        # Exactly 10 years later
        self.assertEqual(whole_years(start, date(2010, 1, 1)), 10)
        # One day before 10 years
        self.assertEqual(whole_years(start, date(2009, 12, 31)), 9)

    def test_whole_years_leap_day(self):
        # Leap day to leap day
        self.assertEqual(whole_years(date(2000, 2, 29), date(2004, 2, 29)), 4)
        # Leap day to non-leap year boundary
        # On Feb 28, 2001, you are not yet 1 year old if born on Feb 29, 2000.
        self.assertEqual(whole_years(date(2000, 2, 29), date(2001, 2, 28)), 0)
        self.assertEqual(whole_years(date(2000, 2, 29), date(2001, 3, 1)), 1)

    def test_whole_years_invalid_range(self):
        with self.assertRaises(ValueError):
            whole_years(date(2010, 1, 1), date(2000, 1, 1))

    def test_is_open_boundaries(self):
        created = date(1960, 5, 17)
        # Exactly 60 years later
        self.assertTrue(is_open(created, today=date(2020, 5, 17)))
        # One day before 60 years
        self.assertFalse(is_open(created, today=date(2020, 5, 16)))
        # Well past 60 years
        self.assertTrue(is_open(created, today=date(2021, 5, 17)))

    def test_is_open_custom_years(self):
        created = date(2000, 1, 1)
        # Open after 10 years
        self.assertTrue(is_open(created, today=date(2010, 1, 1), years=10))
        self.assertFalse(is_open(created, today=date(2009, 12, 31), years=10))

if __name__ == "__main__":
    unittest.main()
