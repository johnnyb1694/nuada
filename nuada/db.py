import os

from dataclasses import dataclass
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Control, Article, Source

@dataclass
class DBC:
    """
    Short for 'Database Configuration'
    """
    dialect: str = os.environ.get('DB_DIALECT') # 'sqlite'
    api: str = os.environ.get('DB_API')# 'pysqlite'
    user: str | None = os.environ.get('DB_USER')
    pwd: str | None = os.environ.get('DB_PWD')
    host: str | None = os.environ.get('DB_HOST')
    port: str | None = os.environ.get('DB_PORT')
    name: str = os.environ.get('DB_NAME') # ':memory:'

def initialise(db_config: DBC, echo: bool = False) -> Session:
    """
    Initialises the database for this application and returns a function which can be used to construct sessions with the same configuration.

    :param db_config: object of class `DBC`
    :param echo: optional boolean that allows you to control whether database operations are echoed to the console or not
    """
    url = f'''{db_config.dialect}
              +
              {db_config.api}
              ://
              {db_config.user}
              :
              {db_config.pwd}
              @
              {db_config.host}
              :
              {db_config.port}
              /
              {db_config.name}'''
    
    engine = create_engine(url, echo=echo)
    Base.metadata.create_all(engine)
    return sessionmaker(engine)


