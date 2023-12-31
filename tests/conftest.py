# Relevant test fixtures are included in this file

import pytest
import json

@pytest.fixture
def sample_nyt_json_decoded():
    """
    This fixture consists of 'one' sample entry of a typical NYT Archive Search response (please see underlying file for details)
    """
    with open('tests/fixtures/sample_nyt_archive_search.json') as file:
        return json.load(file)