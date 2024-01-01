# Relevant test fixtures are included in this file
import pytest
import pandas as pd

from nuada.db import init_db, DBC
from nuada.models import Control, Term, Source

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

@pytest.fixture
def db_session():
    Session = init_db() 
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def valid_control():
    valid_control = Control(commentary='Test Control')
    return valid_control

@pytest.fixture
def valid_source():
    valid_source = Source(source_alias='Test Source')
    return valid_source


