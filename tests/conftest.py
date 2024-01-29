import pytest
import pandas as pd

from nuada.db import DatabaseManager, DatabaseConfig

@pytest.fixture
def db_manager():
    db_config = DatabaseConfig(db_name=':memory:', echo=True)
    db_manager = DatabaseManager(db_config)
    return db_manager

@pytest.fixture
def sample_headlines_df():
    return pd.DataFrame({
        'year': [2023, 2023, 2023],
        'month': [9, 9, 9],
        'headline': ["apple orange banana", "apple banana", "orange banana"]
    })