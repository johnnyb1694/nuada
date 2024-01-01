import pytest

from nuada.models import Control, Term, Source
from sqlalchemy.exc import IntegrityError

class TestModel:

    def test_control_valid(self, db_session, valid_control):
        db_session.add(valid_control)
        db_session.commit()
        insertion = db_session.query(Control).filter_by(commentary='Test Control').first()
        assert insertion.control_id == 1
        assert insertion.status == 'In Progress'
        assert insertion.commentary == 'Test Control'
    
    def test_source_valid(self, db_session, valid_source):
        db_session.add(valid_source)
        db_session.commit()
        insertion = db_session.query(Source).filter_by(source_alias='Test Source').first()
        assert insertion.source_id == 1
        assert insertion.source_alias == 'Test Source'

    def test_term_valid(self, db_session, valid_source, valid_control):
        db_session.add(valid_control)
        db_session.add(valid_source)
        db_session.flush()
        valid_term = Term(term='Test', 
                          year=2023, 
                          month=11, 
                          control_id=valid_control.control_id, 
                          source_id=valid_source.source_id, 
                          frequency=100)
        db_session.add(valid_term)
        db_session.commit()
        insertion = db_session.query(Term).filter_by(term='Test').first()
        assert insertion.frequency == 100
        assert insertion.year == 2023
        assert insertion.month == 11

    @pytest.mark.xfail(raises=IntegrityError)
    def test_term_unique_constraint(self, db_session, valid_control, valid_source):
        db_session.add(valid_control)
        db_session.add(valid_source)
        db_session.flush()
        valid_term = Term(term='Test', 
                          year=2023, 
                          month=11, 
                          control_id=valid_control.control_id, 
                          source_id=valid_source.source_id, 
                          frequency=100)
        db_session.add(valid_term)
        db_session.commit()
        # Now we try to add an effective 'duplicate' of the valid term
        invalid_term = valid_term
        db_session.add(invalid_term)
        try:
            db_session.commit()
        except IntegrityError:
            db_session.rollback()

    