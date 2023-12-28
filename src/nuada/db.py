from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
from models import Base

def _init_engine(db_dialect: str = 'sqlite', 
                 db_api: str = 'pysqlite', 
                 db_user: str = '',
                 db_pwd: str = '',
                 db_host: str = '',
                 db_port: str = '', 
                 db_name: str = ':memory:',
                 echo: bool = True):
    """
    Initialise a database 'session' for operating on the remote database. This abstraction essentially encapsulates a pool of database connections.

    This function will initialise the schema for this database if it has not been created in the target database already.
    """
    # Configure database parameters
    db_config = {
        'drivername': f'{db_dialect}+{db_api}',
        'username': f'{db_user}',
        'password': f'{db_pwd}',
        'host': f'{db_host}',
        'database': f'{db_name}'
    }

    if db_port:
        db_config['port'] = f'{db_port}'

    # Initialise connection pool ('engine')
    engine = create_engine(url=URL.create(**db_config), echo=echo)
    Base.metadata.create_all(engine)
    
    # Establish session factory (which encapsulates a connection pool to the specified remote database URL)
    Session = sessionmaker(engine)
    return Session

if __name__ == '__main__':
    pass