import json
import unittest
from pathlib import Path

from pretf.api import log
from pretf.parser import get_variables_from_file


class TestParser(unittest.TestCase):
    def find_test_files(self):
        test_files_path = Path(__file__).parent / "test_parser_files"
        test_files = set(test_files_path.iterdir())
        for test_file_path in sorted(test_files):
            if not test_file_path.name.endswith(".expected.json"):
                expected_file_path = test_file_path.with_name(
                    test_file_path.name + ".expected.json"
                )
                if expected_file_path in test_files:
                    yield (test_file_path, expected_file_path)

    def test_get_variables_from_file(self):
        for test_file_path, expected_file_path in self.find_test_files():
            with self.subTest(test_file_path.name):
                with expected_file_path.open() as open_file:
                    expected = json.load(open_file)
                result = list(get_variables_from_file(test_file_path))
                self.assertEqual(expected, result)
                log.ok(f"success: {test_file_path.name}")
