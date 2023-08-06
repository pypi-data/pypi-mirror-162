import json
from pathlib import Path

from django_tools.unittest_utils.assertments import assert_is_dir, assert_is_file

import findmydevice_project


FIXTURES_PATH = Path(findmydevice_project.__file__).parent / 'tests' / 'fixtures'
assert_is_dir(FIXTURES_PATH)


def get_fixtures(rel_path):
    file_path = FIXTURES_PATH / rel_path
    assert_is_file(file_path)

    return file_path.read_text(encoding='utf-8')


def get_json_fixtures(rel_path):
    data = get_fixtures(rel_path)
    return json.loads(data)
