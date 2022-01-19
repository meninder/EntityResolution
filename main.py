import logging
import json
from matching_algo import get_all_keys, get_pmatch
from data_utils import namedtuple_asdict

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
logger.addHandler(streamHandler)


def lambda_api_endpoint(event, context):
    """

    This function takes in 2 query parameters called "e1" and "e2"
    Return meta data based on the algo that describes the match.

    """

    logger.info(f"Event Info: {event}")
    logger.info(f"Context Info: {context}")

    q = event['queryStringParameters']
    e1 = q.get('e1', 'null1')
    e2 = q.get('e2', 'null2')

    logger.info(f"entity1: {e1}")
    logger.info(f"entity2: {e2}")
    logger.info(f'Checking if {e1} and {e2} match.')

    if (e1 == 'null1') or (len(e1) == 0) or (e2 == 'null2') or (len(e2) == 0):
       j = json.dumps({})
    else:
        logger.info('Getting full candidate list from Dynamo')
        keys = get_all_keys()
        logger.info(f'There are {len(keys)} keys')

        pmatch = get_pmatch(e1, e2, keys)
        j = json.dumps(namedtuple_asdict(pmatch))

        logger.info(f'json from calculation: {j}')

    return {
        'statusCode': 200,
        'headers': {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Headers" : "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
    },
        'body': j
        }


def local_run():
    get_pmatch(candidate1 = 'facebook',
               candidate2 = 'fanebook',
               keys=['faceboooook', 'face', 'book', 'test_case'],
               theta=0.75)

#local_run()
