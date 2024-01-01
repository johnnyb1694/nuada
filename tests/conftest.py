# Relevant test fixtures are included in this file
import pytest
import pandas as pd

from nuada.db import init_db
from nuada.models import Control, Source

@pytest.fixture
def sample_nyt_response():
    """
    Consists of 'one' sample entry of a typical NYT Archive Search response (please see underlying file for details)
    """
    with open('tests/fixtures/sample_nyt.json', 'rb') as fixture_json_response:
        yield {"Body": fixture_json_response}

@pytest.fixture
def db_session():
    """
    Constructs a basic session with the remote database (defaults to an in-memory SQLite instance)
    """
    Session = init_db() 
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def valid_control():
    """
    Constructs a valid `Control` record
    """
    valid_control = Control(commentary='Test Control')
    return valid_control

@pytest.fixture
def valid_source():
    """
    Constructs a valid `Source` record
    """
    valid_source = Source(source_alias='Test Source')
    return valid_source

@pytest.fixture
def valid_terms_df():
    """
    A (valid) miniature dataframe containing two terms and their associated frequencies
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

@pytest.fixture
def valid_terms_df2():
    """
    A (valid) miniature dataframe containing two terms and their associated frequencies - same as `valid_terms_df` but with a different `month` and `frequency` settings
    """
    sample_terms_df = pd.DataFrame(
        {
            'term': ['trump', 'biden'],
            'year': [2023, 2023],
            'month': [12, 12],
            'frequency': [200, 400]
        }
    )
    return sample_terms_df


