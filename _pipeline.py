import click
import os
import logging
import datetime

from dotenv import load_dotenv
from src.nuada import request_guardian_headlines, request_nyt_headlines, transform, BatchConfig, DatabaseConfig, DatabaseManager

# Load environment variables (if they exist)
load_dotenv()

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

TODAY = datetime.date.today()
FIRST = TODAY.replace(day=1)
LATEST_PERIOD = FIRST - datetime.timedelta(days=1)

def parse_credentials() -> dict:
    '''
    Helper function to extract relevant credentials from environment variables
    '''
    credentials = {'DB_PWD': os.environ.get('DB_PWD'), 
                   'SOURCE_KEY_NYT': os.environ.get('SOURCE_KEY_NYT'),
                   'SOURCE_KEY_GUARDIAN': os.environ.get('SOURCE_KEY_GUARDIAN')}

    if 'DB_PWD_FILE' in os.environ:
        with open(os.environ['DB_PWD_FILE'], 'r') as f:
            credentials['DB_PWD'] = f.read().strip()

    if 'SOURCE_KEY_NYT_FILE' in os.environ:
        with open(os.environ['SOURCE_KEY_NYT_FILE'], 'r') as f:
            credentials['SOURCE_KEY_NYT'] = f.read().strip()

    if 'SOURCE_KEY_GUARDIAN_FILE' in os.environ:
        with open(os.environ['SOURCE_KEY_GUARDIAN_FILE'], 'r') as f:
            credentials['SOURCE_KEY_GUARDIAN'] = f.read().strip()

    return credentials

@click.command()
@click.option('--year', default = LATEST_PERIOD.year)
@click.option('--month', default = LATEST_PERIOD.month)
def exec_pipeline(year: int, month: int) -> bool:
    '''
    Execute primary batch headline(s) ETL for this project.

    :param year: year of interest
    :param month: month of interest
    '''
    logging.info('Retrieving credentials (passwords & API keys)')
    secrets = parse_credentials()
    
    logging.info('Configuring execution context')
    batch_config = BatchConfig(year, month)
    db_config = DatabaseConfig(db_dialect=os.environ.get('DB_DIALECT', 'sqlite'),
                               db_api=os.environ.get('DB_API', 'pysqlite'),
                               db_user=os.environ.get('DB_USER', ''),
                               db_pwd=secrets['DB_PWD'],
                               db_host=os.environ.get('DB_HOST', ''),
                               db_port=os.environ.get('DB_PORT', ''),
                               db_name=os.environ.get('DB_NAME', ':memory:'))
    
    logging.info(f'Connecting to remote database session (config: {db_config})')
    db = DatabaseManager(db_config)
    
    logging.info(f'Requesting headline metadata from the "New York Times" and the "Guardian" (config: {batch_config})')
    headlines_nyt = request_nyt_headlines(year, month, secrets['SOURCE_KEY_NYT'])
    headlines_guardian = request_guardian_headlines(year, month, secrets['SOURCE_KEY_GUARDIAN'])
    
    logging.info(f'Transforming headlines into term-frequency matrices')
    terms_nyt = transform(headlines_nyt)
    terms_guardian = transform(headlines_guardian)
    batch_data = {'New York Times': terms_nyt,
                  'Guardian': terms_guardian}
    
    logging.info('Ingesting extracts from aforementioned media sources into database instance')
    db.insert_batch(batch_config, batch_data)
    
    return True

if __name__ == '__main__':
    exec_pipeline()