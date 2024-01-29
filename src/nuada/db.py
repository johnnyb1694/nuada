import pandas as pd
import logging

from datetime import datetime
from dataclasses import dataclass
from sqlalchemy import create_engine, URL, select, update
from sqlalchemy.orm import Session
from .models import Base, Control, Term, Source

@dataclass
class DatabaseConfig:
    '''
    Configure the parameters for a remote SQL database connection
    '''
    db_dialect: str = 'sqlite'
    db_api: str = 'pysqlite'
    db_user: str | None = ''
    db_pwd: str | None = ''
    db_host: str | None = ''
    db_port: str | None = ''
    db_name: str = ':memory:'
    echo: bool = False

    def __repr__(self) -> str:
        return f'(Database: {self.db_dialect}, Name: {self.db_name})'

@dataclass
class BatchConfig:
    '''
    Configure the parameters for batch ingestion (see `DatabaseManager()` for more detail).

    :param year: Year of batch upload
    :param month: Month of batch upload
    :param commentary: String identifier for the batch run description
    :param resource_extracts: Set of `pd.DataFrame` objects identifying different source extracts (e.g. 'New York Times')
    '''
    year: int
    month: int
    commentary: str = 'Production'

    def __repr__(self) -> str:
        return f'(Period (Yyyy/Mm): {self.year}/{self.month}, Commentary: {self.commentary})'
    

def _init_db_session(db_config: DatabaseConfig = DatabaseConfig()) -> Session:
    '''
    Initialise a database 'session' for operating on the remote database. This abstraction essentially encapsulates a pool of database connections.

    This function will initialise the schema for this database if it has not been created in the target database already.
    '''
    # Configure database parameters
    if db_config.db_dialect.lower() == 'sqlite':
        # For SQLite, handle the URL format differently
        db_url = f'{db_config.db_dialect}:///{db_config.db_name}'
    else:
        # For other databases
        engine_config = {
            'drivername': f'{db_config.db_dialect}+{db_config.db_api}',
            'username': f'{db_config.db_user}',
            'password': f'{db_config.db_pwd}',
            'host': f'{db_config.db_host}',
            'database': f'{db_config.db_name}'
        }
        if db_config.db_port:
            engine_config['port'] = db_config.db_port
        db_url = URL.create(**engine_config)

    # Initialise connection pool ('engine')
    engine = create_engine(url=db_url, echo=db_config.echo)
    Base.metadata.create_all(engine)
    
    return Session(engine)

class DatabaseManager():
    '''
    Repository pattern for efficient and secure database interactions. With this abstraction you can load headline terms into the database.
    '''
    def __init__(self, database_config: DatabaseConfig):
        self.db_session = _init_db_session(database_config)

    def _insert_control(self, year: int, month: int, commentary: str = 'Production') -> int:
        '''
        Insert `control` record into the database

        :param year: Integer year of extraction
        :param month: Integer year of extraction
        :param commentary: String description for the pipeline being administered (defaults to 'Production')
        '''
        stmt = select(Control).where(Control.year == year, Control.month == month)
        res = self.db_session.execute(stmt).first()
        if not res:
            control = Control(year=year, month=month, commentary=commentary)
            self.db_session.add(control)
            self.db_session.commit()
            control_status = control.status
            control_id = control.control_id
        else:
            control_status = res[0].status
            control_id = res[0].control_id
        return control_id, control_status
    
    def _update_control(self, control_id: int, status: str, commentary: str) -> None:
        '''
        Update `control` record in the database

        :param control_id: Integer identifier for the control record to be updated
        :param status: String description of the execution 'status' of the pipeline
        '''
        resolution = update(Control).where(Control.control_id == control_id).values(timestamp=datetime.now(), 
                                                                                    status=status, 
                                                                                    commentary=commentary)
        self.db_session.execute(resolution)
    
    def _insert_source(self, alias: str) -> int:
        '''
        Insert `source` record into the database (e.g. 'New York Times'); if source with `alias` already exists, the corresponding ID is returned instead

        :param alias: A string-based description of the media source
        '''
        stmt = select(Source).where(Source.alias == alias)
        res = self.db_session.execute(stmt).first()
        if not res:
            source = Source(alias=alias)
            self.db_session.add(source)
            self.db_session.flush()
            source_id = source.source_id
        else:
            source_id = res[0].source_id
        return source_id

    def _insert_term(self, token: str, frequency: int, source_id: int, control_id: int) -> int:
        '''
        Insert an individual term (`token`) and frequency into the database

        :param token: String identifying the term of interest
        :param frequency: Integer indicating the frequency that the term had been observed for this control and source
        :param source_id: Integer identifying the source record
        :param control_id: Integer identifying the control record
        '''
        stmt = select(Term).where(Term.term == token, Term.control_id == control_id)
        res = self.db_session.execute(stmt).first()
        if not res:
            term = Term(term=token,
                        source_id=source_id,
                        control_id=control_id,
                        frequency=frequency)
            self.db_session.add(term)
            self.db_session.flush()
            term_id = term.term_id
        else:
            term_id = res[0].term_id
        return term_id
    
    def _insert_terms(self, terms_df: pd.DataFrame, source_id: int, control_id: int) -> None:
        '''
        Insert *multiple* terms and associated frequencies into the database

        :param terms_df: Object of class `pd.DataFrame` with fields: `term` and `frequency`
        :param source_id: Integer identifying the source record
        :param control_id: Integer identifying the control record
        '''
        terms_dict = terms_df.to_dict(orient='records')
        for record in terms_dict:
            self._insert_term(token=record['term'], 
                             frequency=record['frequency'], 
                             source_id=source_id, 
                             control_id=control_id)

    def insert_batch(self, batch_config: BatchConfig, batch_data: dict[pd.DataFrame]) -> int:
        '''
        Inserts a batch of terms (`terms_df`) into the database instance. Parameter `batch_config` is used
        to parametrise the batch run settings.

        :param terms_df: Object of class `pd.DataFrame` with fields: `term` and `frequency`
        :param batch_config: Object of class `BatchConfig`
        '''
        control_id, control_status = self._insert_control(batch_config.year, batch_config.month, batch_config.commentary)
        if control_status == 'Success':
            return control_id
        try:
            source_aliases = batch_data.keys()
            for source_alias in source_aliases:
                source_id = self._insert_source(source_alias)
                source_terms_df = batch_data.get(source_alias)
                self._insert_terms(terms_df=source_terms_df,
                                  control_id=control_id,
                                  source_id=source_id)
            self._update_control(control_id, 'Success', 'Production')
        # NB: generic `Exception` is not always a good practice but for the purposes of logging (below) it arguably makes sense
        except Exception as err:
            logging.error(err)
            self.db_session.rollback()
            self._update_control(control_id, 'Fatal', str(err))
        finally:
            self.db_session.flush()
            self.db_session.commit()
        return control_id
    
if __name__ == '__main__':
    pass