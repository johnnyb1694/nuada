# Relevant test fixtures are included in this file
import pytest
import pandas as pd

@pytest.fixture
def sample_nyt_response():
    """
    This fixture consists of 'one' sample entry of a typical NYT Archive Search response (please see underlying file for details)
    """
    with open('tests/fixtures/sample_nyt.json', 'rb') as fixture_json_response:
        yield {"Body": fixture_json_response}

@pytest.fixture
def sample_terms_df():
    """
    This fixture consists of a miniature dataframe containing two terms and their associated frequencies
    """
    sample_terms_df = pd.DataFrame(
        {
            'term': ['trump', 'biden'],
            'year': [2023, 2023],
            'month': [11, 11],
            'frequency': [100, 200]
        }
    )
    return sample_terms_df