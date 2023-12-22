import logging
import urllib.parse
import boto3
import json

from botocore.exceptions import ClientError
from dotenv import load_dotenv
load_dotenv()

log = logging.getLogger()
log.setLevel('INFO')

def get_s3_metadata(event):
    """
    Helper function to retrieve the `bucket` and `key` properties of the `event` parameter.

    :param event: Payload object of key-value pairs; these are parameters which can be dynamically passed to the underlying handler function

    ** Note **

    The logic of this function is informed by the structure of the `event` object issued by S3. An illustration is shown below:

    {
      "Records": [
        ...,
        "s3": {
            ...
            "bucket": {
                "name": "BUCKET_NAME",
                ...
            },
            "object": {
                "key": "OBJECT_KEY", 
                ...
            }
        }
        }
    ]
    }
    """
    s3 = event['Records'][0]['s3']

    bucket = s3['bucket']['name']
    key = urllib.parse.unquote_plus(s3['object']['key'], encoding='utf-8') # NB: this raw URL contains special characters which need to be converted (e.g. %2F for /)
    
    s3_metadata = {'bucket': bucket, 'key': key}
    return s3_metadata

def extract_article_data(response) -> dict:
    """
    Ingests a response from `s3_client.get_object()` and deserialises this response into a Python dictionary object.

    :param response: Raw response from call to `s3_client.get_object()` (see `lambda_handler()` presented below)
    """
    body = response['Body'].read().decode('utf-8')
    decoded = json.loads(body)
    article_data = decoded['response']['docs']
    return article_data

def filter_article_data(article_data: dict) -> dict:
    pass

def lambda_handler(event, context):
    """
    Handler for AWS lambda integration.

    :param event: Payload object of key-value pairs; these are parameters which can be dynamically passed to the underlying handler function
    :param context: Object containing information on the context of invocation (e.g. which other service 'triggered' the function and so forth)
    """
    s3_metadata = get_s3_metadata(event)
    s3_client = boto3.client('s3')
    try:
        log.info(f'Retrieving latest dataset (key: {s3_metadata["key"]}) uploaded to: {s3_metadata["bucket"]}')
        response = s3_client.get_object(Bucket=s3_metadata['bucket'], Key=s3_metadata['key'])
        # Logic to upload code to an RDS instance
    except ClientError as e:
        log.error(e)
        raise e
    return True

if __name__ == '__main__':
    
    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket='nuada-archives', Key='2023_11_nyt_archive_search.json')
    article_data = extract_article_data(response)
    print(article_data[0])