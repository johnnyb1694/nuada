import logging
import os
import click
import datetime

from dotenv import load_dotenv
from src.nuada import DBC, init_db, ingest, preprocess, request_nyt_archive_search

# Load environment variables (if they exist)
load_dotenv()

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Extract current timestamp (for pipelining purposes below!)
TODAY = datetime.date.today()
FIRST = TODAY.replace(day=1)
LATEST_PERIOD = FIRST - datetime.timedelta(days=1)

@click.command()
@click.option('--year', default = LATEST_PERIOD.year)
@click.option('--month', default = LATEST_PERIOD.month)
def exec_pipeline(year: int, month: int):

    logging.info('Initialising environment variables')
    nyt_key = os.environ.get('SOURCE_KEY_NYT')
    db_config = DBC(db_dialect=os.environ.get('DB_DIALECT', 'sqlite'),
                    db_api=os.environ.get('DB_API', 'pysqlite'),
                    db_user=os.environ.get('DB_USER', ''),
                    db_pwd=os.environ.get('DB_PWD', ''),
                    db_host=os.environ.get('DB_HOST', ''),
                    db_port=os.environ.get('DB_PORT', ''),
                    db_name=os.environ.get('DB_NAME', ':memory:'))
    logging.info('Requesting data from New York Times "Archive Search" API')
    response_json = request_nyt_archive_search(year=str(year), month=str(month), key=nyt_key)

    logging.info('Constructing term-frequency dataframe for specified period of interest')
    term_frequency_df = preprocess(response_json)
    
    logging.info('Uploading term-frequency dataframe into database service')
    Session = init_db(db_config)
    with Session() as db_session:
       ingest(db_session, term_frequency_df)

    return True

if __name__ == '__main__':
    exec_pipeline()