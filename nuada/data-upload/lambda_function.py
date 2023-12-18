import requests
import os
import boto3
import logging

from botocore.exceptions import ClientError
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)

def request_nyt_archive_search(year: int, month: int, key: str) -> str:
    """
    Request results of the New York Times 'Archive Search' API (NYT API) via the internet.

    :param year: Year of interest
    :param month: Month of interest
    :param key: API key applicable to the NYT API
    """
    if not key:
        raise ValueError('Input variable `key` must be specified')
    url = f'https://api.nytimes.com/svc/archive/v1/{str(year)}/{str(month)}.json?api-key={key}'
    try:
        res = requests.get(url)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return None
    return res.json()

def upload_file(file_name: str, bucket: str, object_name=None):
    """
    Upload a file to an S3 bucket.

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def lambda_handler(event, context):
    """
    Handler for AWS lambda integration.
    """
    log.info('Configuring input parameters')
    s3_bucket = 'nuada'
    time = datetime.now()
    nyt_latest_year = time.year
    nyt_latest_month = time.month - 1
    nyt_key = os.environ.get('SOURCE_KEY_NYT')
    nyt_file_name = f'{nyt_latest_year}_{nyt_latest_month}_nyt_archive_search.json'

    log.info(f'Extracting latest media archive (as at: 01/{nyt_latest_month}/{nyt_latest_year}) from the New York Times API')
    articles = request_nyt_archive_search(year=nyt_latest_year, month=nyt_latest_month, key=nyt_key)

    log.info(f'Uploading latest archive (filename: {nyt_file_name}) to S3 bucket: {s3_bucket}')
    response = upload_file(file_name=nyt_file_name, bucket=s3_bucket, object_name=articles)
    
    return response

if __name__ == '__main__':
    pass
