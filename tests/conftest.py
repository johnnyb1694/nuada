# Relevant test fixtures are included in this file
import pytest

@pytest.fixture
def sample_nyt_response():
    """
    This fixture consists of 'one' sample entry of a typical NYT Archive Search response (please see underlying file for details)
    """
    with open('tests/fixtures/sample_nyt.json', 'rb') as fixture_json_response:
        yield {"Body": fixture_json_response}