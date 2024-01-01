import pandas as pd
import logging

from dataclasses import dataclass
from sqlalchemy import create_engine, URL, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from nuada.models import Base, Control, Term, Source

log = logging.getLogger()
log.setLevel('INFO')

@dataclass
class DBC:
    """
    'DBC' stands for 'Database Configuration': this dataclass can be used to configure the parameters for a remote SQL database connection
    """
    db_dialect: str = 'sqlite'
    db_api: str = 'pysqlite'
    db_user: str | None = ''
    db_pwd: str | None = ''
    db_host: str | None = ''
    db_port: str | None = ''
    db_name: str = ':memory:'
    echo: bool = False

def init_db(db_config: DBC = DBC()) -> Session:
    """
    Initialise a database 'session' for operating on the remote database. This abstraction essentially encapsulates a pool of database connections.

    This function will initialise the schema for this database if it has not been created in the target database already.
    """
    # Configure database parameters
    engine_config = {
        'drivername': f'{db_config.db_dialect}+{db_config.db_api}',
        'username': f'{db_config.db_user}',
        'password': f'{db_config.db_pwd}',
        'host': f'{db_config.db_host}',
        'database': f'{db_config.db_name}'
    }

    # Initialise connection pool ('engine')
    engine = create_engine(url=URL.create(**engine_config), echo=db_config.echo)
    Base.metadata.create_all(engine)
    
    # Establish session factory (which encapsulates a connection pool to the specified remote database URL)
    Session = sessionmaker(engine)
    return Session

def _ingest_term(db_session, terms_record: dict, source_id: int, control_id: int):
    """
    Ingest a single term record (`terms_record`) with *at least* keys: `term`, `year`, `month` and `frequency`
    """
    try:
        stmt = select(Term).where(Term.term == terms_record['term'], Term.year == terms_record['year'], Term.month == terms_record['month'])
        res = db_session.execute(stmt).first()
        if not res:
            term = Term(term=terms_record['term'],
                        year=terms_record['year'],
                        month=terms_record['month'],
                        source_id=source_id,
                        control_id=control_id,
                        frequency=terms_record['frequency'])
            db_session.add(term)
            db_session.flush()
    except SQLAlchemyError as e:
        log.error(e)
        db_session.rollback()

def ingest(db_session: Session, terms_df: pd.DataFrame, commentary: str = 'Batch', source_alias: str = 'New York Times'):
    """
    Ingests a `pd.DataFrame` object with at least columns: `term`, `year`, `month` and `frequency`.

    This object is inserted into the remote database instance specified by `db_config`.

    :param db_session: Configuration for the remote database instance where results will be stored
    :param terms_df: Generated output of `transformer.preprocess()` with columns `term`, `year`, `month` and `frequency`
    :param commentary: Brief note on the ingestion performed; defaults to `'Batch'`
    :param source_alias: Describes the source of ingestion; at present, this is simply set to the `'New York Times'` by default as it is the only outlet we process
    """
    try:
        # Set up a 'control' record for this batch run
        control = Control(commentary=commentary)
        db_session.add(control)
        db_session.flush()
        control_id = control.control_id
        # Set up a 'source' record for this batch run
        stmt = select(Source).where(Source.source_alias == source_alias)
        res = db_session.execute(stmt).first()
        if not res:
            source = Source(source_alias=source_alias)
            db_session.add(source)
            db_session.flush()
            source_id = source.source_id
        else:
            source_id = res[0].source_id
        # Ingest headline terms into database
        terms = terms_df.to_dict(orient='records')
        for terms_record in terms:
            _ingest_term(db_session, terms_record, source_id, control_id)
        resolution = update(Control).where(Control.control_id == control_id).values(status='Complete')
        db_session.execute(resolution)
    except SQLAlchemyError as e:
        log.error(e)
        db_session.rollback()
        resolution = update(Control).where(Control.control_id == control_id).values(status='Fatal')
        db_session.execute(resolution)
    finally:
        db_session.flush()
        db_session.commit()

if __name__ == '__main__':
    db_config = DBC()
    Session = init_db(db_config)
    sample_terms_df = pd.DataFrame(
        {
            'term': ['trump', 'biden'],
            'year': [2023, 2023],
            'month': [11, 11],
            'frequency': [100, 200]
        }
    )
    sample_terms_df2 = pd.DataFrame(
        {
            'term': ['trump', 'biden'],
            'year': [2023, 2023],
            'month': [12, 12],
            'frequency': [200, 400]
        }
    )
    with Session() as session:
        ingest(session, sample_terms_df)
        ingest(session, sample_terms_df2)
        res = session.query(Term).filter_by(term='trump').all()
        print(res)
