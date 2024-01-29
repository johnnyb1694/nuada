import pandas as pd
from nuada.db import BatchConfig
from nuada.models import Control, Term, Source

def test_insert_batch_success(db_manager):
    '''
    Vanilla test that batch can be successfully loaded into the database
    '''
    batch_data = {'New York Times': pd.DataFrame({'term': ['apple', 'banana'], 'frequency': [10, 20]})}
    batch_config = BatchConfig(year=2022, month=1)
    control_id = db_manager.insert_batch(batch_config, batch_data)

    control_record = db_manager.db_session.query(Control).filter(Control.control_id == control_id).first()
    assert control_record is not None
    assert control_record.status == 'Success'

    term_records = db_manager.db_session.query(Term).all()
    source_records = db_manager.db_session.query(Source).all()

    assert len(term_records) == 2
    assert len(source_records) == 1

def test_insert_batch_failure(db_manager):
    '''
    Given an invalid input of batch data, the pipeline fails and registers a status of 'Fatal'
    '''
    batch_data = {'New York Times': pd.DataFrame({'term_XYZ': ['apple', 'banana'], 'frequency': ['XYZ', 20]})}
    batch_config = BatchConfig(year=2022, month=1)
    control_id = db_manager.insert_batch(batch_config, batch_data)

    control_record = db_manager.db_session.query(Control).filter(Control.control_id == control_id).first()
    assert control_record is not None
    assert control_record.status == 'Fatal'

def test_insert_batch_existing_source(db_manager):
    '''
    Given the source already exists, the pipeline succeeds and stores the terms as expected
    '''
    existing_source = Source(alias='Existing Source')
    db_manager.db_session.add(existing_source)
    db_manager.db_session.commit()

    batch_data = {'Existing Source': pd.DataFrame({'term': ['apple', 'banana'], 'frequency': [10, 20]})}
    batch_config = BatchConfig(year=2022, month=1)
    control_id = db_manager.insert_batch(batch_config, batch_data)

    control_record = db_manager.db_session.query(Control).filter(Control.control_id == control_id).first()
    assert control_record is not None
    assert control_record.status == 'Success'

    source_records = db_manager.db_session.query(Source).all()
    assert len(source_records) == 1
