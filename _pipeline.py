import logging
import os
import click
import datetime

from dotenv import load_dotenv
from src.nuada.pipeline import DBC, init_db, ingest, preprocess, request_nyt_archive_search

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

def parse_credentials() -> dict:
    """
    Helper function to extract relevant credentials from environment variables
    """
    credentials = {'DB_PWD': os.environ.get('DB_PWD'), 'SOURCE_KEY_NYT': os.environ.get('SOURCE_KEY_NYT')}

    if 'DB_PWD_FILE' in os.environ:
        with open(os.environ['DB_PWD_FILE'], 'r') as f:
            credentials['DB_PWD'] = f.read().strip()

    if 'SOURCE_KEY_NYT_FILE' in os.environ:
        with open(os.environ['SOURCE_KEY_NYT_FILE'], 'r') as f:
            credentials['SOURCE_KEY_NYT'] = f.read().strip()

    return credentials

@click.command()
@click.option('--year', default = LATEST_PERIOD.year)
@click.option('--month', default = LATEST_PERIOD.month)
def exec_pipeline(year: int, month: int) -> bool:
    """
    Execute the 'main' data pipeline; funnels headline term frequencies into a remote database instance specified with environment variables

    :param year: year of interest
    :param month: month of interest
    """
    logging.info('Initialising environment variables')
    secrets = parse_credentials()
    nyt_key = secrets['SOURCE_KEY_NYT']
    db_config = DBC(db_dialect=os.environ.get('DB_DIALECT', 'sqlite'),
                    db_api=os.environ.get('DB_API', 'pysqlite'),
                    db_user=os.environ.get('DB_USER', ''),
                    db_pwd=secrets['DB_PWD'],
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
       control = ingest(db_session, term_frequency_df)
       logging.info(f'Ingestion processed with status: {control}')

    return True

if __name__ == '__main__':
    exec_pipeline()