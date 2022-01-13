import boto3
import logging
from botocore.exceptions import ClientError

import os
os.environ['AWS_PROFILE']='mike'
assert os.getenv('AWS_PROFILE') == 'mike'


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
logger.addHandler(streamHandler)

def start_table_session():
    session = boto3.Session()
    credentials = session.get_credentials()
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=credentials.access_key,
        aws_secret_access_key=credentials.secret_key,
        region_name='us-east-1'
        )
    table = dynamodb.Table('Sp500EntityResolution')

    return table


def write_dct(dct):

    table = start_table_session()
    logger.info('Retrieved Dynamo table')
    logger.info(f'Writing {len(dct)} items')
    for key, indexer in dct.items():
        d = {
            "candidates": key,
            "name": indexer.name,
            "probability": str(indexer.p)
            }
        try:
            if len(key.strip())==None:
                response = table.put_item(Item=d)
        except ClientError as e:
            logger.warning(f'Failed to put key {key} with indexer value {indexer}.')
    logger.info('Finished writing to table')


def get_key_probability_and_name(key):
    table = start_table_session()
    response = table.get_item(Key={'candidates': key})
    response = response.get('Item', {})
    probability = float(response.get('probability', 0.0))
    name = response.get('name', 'None')
    return name, probability


def get_all_keys():
    table = start_table_session()
    response = table.scan(AttributesToGet=['candidates'])
    response = response.get('Items', [])
    keys = [d['candidates'] for d in response]

    return keys