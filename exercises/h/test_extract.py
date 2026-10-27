# test_extract.py - sjekker at extract.py gir samme utskrift som den gamle versjonen
# bruk: python3 test_extract.py
import os
import subprocess
import sys
import unittest
from pathlib import Path

MAPPE = Path(__file__).resolve().parent

# (argumenter, fil med utskrift fra det gamle skriptet)
KJORINGER = [
    (["1990", "1999"], "old-1990-1999.txt"),
    (["1990"], "old-1990.txt"),
    (["2000", "2005"], "old-2000-2005.txt"),
]


class TestExtract(unittest.TestCase):
    def test_samme_utskrift_som_gammel_versjon(self):
        for args, fasit in KJORINGER:
            with self.subTest(args=args):
                # utf-8 og tekstmodus, så testen også går på Windows (cp1252, \r\n)
                ny = subprocess.run(
                    [sys.executable, "extract.py", "cases.csv", *args],
                    cwd=MAPPE, capture_output=True, check=True, text=True,
                    encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                ).stdout
                gammel = (MAPPE / fasit).read_text(encoding="utf-8")
                self.assertEqual(ny, gammel)


if __name__ == "__main__":
    unittest.main()
