import json
from pathlib import Path

import pytest

from pretf.variables import get_variables_from_file


def find_test_files():
    test_files_path = Path(__file__).parent / "test_variables_files"
    test_files = set(test_files_path.iterdir())
    for test_file_path in sorted(test_files):
        if not test_file_path.name.endswith(".expected.json"):
            expected_file_path = test_file_path.with_name(
                test_file_path.name + ".expected.json"
            )
            if expected_file_path in test_files:
                yield (test_file_path, expected_file_path)


@pytest.mark.parametrize("test_file_path,expected_file_path", find_test_files())
def test_get_variables_from_file(test_file_path, expected_file_path):
    print("test", test_file_path, expected_file_path)
    with expected_file_path.open() as open_file:
        expected = json.load(open_file)
    result = []
    for var in get_variables_from_file(test_file_path):
        result.append(dict(var))
    assert expected == result
