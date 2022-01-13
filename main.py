import logging
from string_cleaning_utils import clean_org
from matching_algo import calculate_probability_match

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
logger.addHandler(streamHandler)


def lambda_handler(event, context):

    logging.info(f"Event Info: {event}")
    logging.info(f"Context Info: {context}")

    q = event['queryStringParameters']
    e1 = q.get('entity1', 'entity1')
    e2 = q.get('entity2', 'entity2')

    logging.info(f"entity1: {e1}")
    logging.info(f"entity2: {e2}")
    logger.info(f'Checking if {e1} and {e2} match.')

    e1_clean = clean_org(e1)
    e2_clean = clean_org(e2)
    match, p_match = calculate_probability_match(e1_clean, e2_clean)
