import requests
import os
import boto3
import json
import logging

from contextlib import contextmanager
from botocore.exceptions import ClientError
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

log = logging.getLogger()
log.setLevel('INFO')

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
        log.error(e)
        return False
    return res.json()

@contextmanager
def staging_data(file_name: str, data: dict, base_path: str = '/tmp'):
    """
    Stages response data in a JSON format (e.g. articles retrieved in a dictionary format) on the local `/tmp` drive. Operates in a context-driven fashion.

    :param file_name: Desired file name (including base path, if necessary)
    :param data: Dataset
    """
    staging_path = os.path.join(base_path, file_name)
    try:
        json_string = json.dumps(data)
        with open(staging_path, 'w') as file:
            file.write(json_string)
        yield
    except IOError as e:
        log.error(e)
        return False
    finally:
        # NB: there is a small chance that, due to IO errors, the path does not exist (hence this clause)
        if os.path.exists(staging_path):
            os.remove(staging_path)
    return True

def upload_file(file_name: str, bucket: str, object_name: str | None = None, base_path: str = '/tmp'):
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
    file_path = os.path.join(base_path, file_name)
    try:
        s3_client.upload_file(file_path, bucket, object_name)
    except ClientError as e:
        log.error(e)
        return False
    return True

def lambda_handler(event, context):
    """
    Handler for AWS lambda integration.

    :param event: Payload of key-value pairs; these are parameters which can be dynamically passed to the underlying handler function
    """
    log.info('Configuring environment parameters')
    s3_bucket = 'nuada-archives'
    time = datetime.now()
    nyt_latest_year = time.year
    nyt_latest_month = time.month - 1
    nyt_key = os.environ.get('SOURCE_KEY_NYT')
    nyt_file_name = f'{nyt_latest_year}_{nyt_latest_month}_nyt_archive_search.json'

    log.info(f'Extracting latest media archive (as at: 01/{nyt_latest_month + 1}/{nyt_latest_year}) from the New York Times API')
    articles = request_nyt_archive_search(year=nyt_latest_year, month=nyt_latest_month, key=nyt_key)

    log.info(f'Uploading latest archive (filename: {nyt_file_name}) to S3 bucket: "{s3_bucket}"')
    response = False
    with staging_data(nyt_file_name, articles):
        response = upload_file(file_name=nyt_file_name, bucket=s3_bucket)
    
    return response

if __name__ == '__main__':
    pass
