import pandas as pd

from nuada.db import DBC, init_db, ingest

def test_ingestion(sample_terms_df):
    Session = init_db()
    with Session() as db_session:
        ingest(db_session, sample_terms_df)