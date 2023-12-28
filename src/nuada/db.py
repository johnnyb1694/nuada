from sqlalchemy import create_engine, URL
from models import Base

def _init_engine(db_dialect: str = 'sqlite', 
                 db_api: str = 'pysqlite', 
                 db_user: str = '',
                 db_pwd: str = '',
                 db_host: str = '',
                 db_port: str = '', 
                 db_name: str = ':memory:',
                 echo: bool = True):
    '''
    Initialise the 'engine' for operating on the remote database. This abstraction essentially encapsulates a pool of database connections.

    It is wrapped around a further abstraction - the `Session` object - when interacting with the database via the SQLAlchemy ORM. This function
    will initialise the schema for this database if it has not been created in the target database already.
    '''

    db_config = {
        'drivername': f'{db_dialect}+{db_api}',
        'username': f'{db_user}',
        'password': f'{db_pwd}',
        'host': f'{db_host}',
        'database': f'{db_name}'
    }

    if db_port:
        db_config['port'] = f'{db_port}'

    engine = create_engine(url=URL.create(**db_config), echo=echo)
    Base.metadata.create_all(engine)

    return engine

if __name__ == '__main__':

    engine = _init_engine()