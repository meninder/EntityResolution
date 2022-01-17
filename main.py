import logging
import json
from matching_algo import calculate_probability_match


# cool - I never used a logger in lambda since printing goes directly to CloudWatch (lazy me!)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
logger.addHandler(streamHandler)


# should probably call the function in a more perspicous way, e..g. like the endpoint ;-)
def lambda_handler(event, context):
    """
    
    Some comments here, in whatever format you want

    """

    logger.info(f"Event Info: {event}")
    logger.info(f"Context Info: {context}")

    q = event['queryStringParameters']
    # maybe return a "request not valid" if somebody skips the params?
    # or, is there value anyway in running the algo without BOTH entities specified?
    e1 = q.get('e1', 'null1')
    e2 = q.get('e2', 'null2')

    logger.info(f"entity1: {e1}")
    logger.info(f"entity2: {e2}")
    logger.info(f'Checking if {e1} and {e2} match.')

    dct = calculate_probability_match(e1, e2)

    j = json.dumps(dct)
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

'''
def local_run():
    match, p_match = calculate_probability_match('bank of america', 'bofa')
    return match, p_match

local_run()
'''