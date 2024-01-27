from nuada.pipeline.db import ingest
from nuada.models import Control, Source, Term

def test_ingest(db_session, valid_terms_df):
    """
    Tests basic ingestion works as expected for a miniature dataframe of terms (see relevant fixture `valid_terms_df`)
    """
    ingest(db_session, valid_terms_df, commentary='Test', source_alias='Test')
    trump = db_session.query(Term).filter_by(term='trump').first()
    biden = db_session.query(Term).filter_by(term='biden').first()
    assert trump.frequency == 100
    assert biden.frequency == 200

def test_ingest_repetition(db_session, valid_terms_df, valid_terms_df2):
    """
    Tests (in principal) that, given an existing ingestion on an existing `Source`, a repeat ingestion can be made on the same `Source` successfully without
    throwing any errors (if not, we wouldn't be able to schedule this contraption!)
    """
    with db_session:
        # First time
        ingest(db_session, valid_terms_df, commentary='Test Repetition (1)', source_alias='Test')
        # Second time
        ingest(db_session, valid_terms_df2, commentary='Test Repetition (2)', source_alias='Test')
        # Test that insertions operated as expected
        trump_11 = db_session.query(Term).filter_by(term='trump', month=11).first()
        trump_12 = db_session.query(Term).filter_by(term='trump', month=12).first()
        assert trump_11.frequency == 100
        assert trump_12.frequency == 200


