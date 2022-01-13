from dynamo_utils import get_all_keys, get_key_probability_and_name
from jellyfish import jaro_similarity

import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
logger.addHandler(streamHandler)


def calculate_probability_ee(e1, e2):
    p_ee = jaro_similarity(e1, e2)
    return p_ee


def get_largest_candidate_key(e1, e2, keys):
    scores_e1 = [(k, jaro_similarity(e1, k)) for k in keys]
    scores_e1.sort(key=lambda x: x[1], reverse=True)
    key_score_tuple_e1 = scores_e1[0]

    scores_e2 = [(k, jaro_similarity(e2, k)) for k in keys]
    scores_e2.sort(key=lambda x: x[1], reverse=True)
    key_score_tuple_e2 = scores_e2[0]

    return key_score_tuple_e1, key_score_tuple_e2


def get_candidate_company_probability(key_score_tuple_e1, key_score_tuple_e2):
    key1, prob_ec1 = key_score_tuple_e1
    key2, prob_ec2 = key_score_tuple_e2

    ticker_probability_tuple1 = get_key_probability_and_name(key1)
    ticker_probability_tuple2 = get_key_probability_and_name(key2)

    return ticker_probability_tuple1, ticker_probability_tuple2


def calculate_probability_match(e1, e2):

    theta_ee = 0.75
    theta_l = 0.65

    logger.info('Getting full candidate list from Dynamo')
    keys = get_all_keys()
    logger.info(f'There are {len(keys)} keys')

    # get k1, k2 (candidate synomous with key)
    key_score_tuple_e1, key_score_tuple_e2 = get_largest_candidate_key(e1, e2, keys)
    logger.info(f'{e1} is mapped to key {key_score_tuple_e1[0]} with probability {key_score_tuple_e1[1]}')
    logger.info(f'{e2} is mapped to key {key_score_tuple_e2[0]} with probability {key_score_tuple_e2[1]}')

    if key_score_tuple_e1[0] == key_score_tuple_e2[0]:
        # matching key case (Case 2)
        final_probability = min(key_score_tuple_e1[1], key_score_tuple_e2[1])
        match = 2
        logger.info(f'Case 2: Keys match with probability {final_probability}')
    else:
        # get tickers corresponding to keys
        ticker_probability_tuple1, ticker_probability_tuple2 = get_candidate_company_probability(key_score_tuple_e1,
                                                                                                 key_score_tuple_e2)
        logger.info(
            f'Key {key_score_tuple_e1[0]}' + \
            f' is mapped to {ticker_probability_tuple1[0]}' + \
            f' with probability {ticker_probability_tuple1[1]}')
        logger.info(
            f'Key {key_score_tuple_e2[0]}' + \
            f' is mapped to {ticker_probability_tuple2[0]}' + \
            f' with probability {ticker_probability_tuple2[1]}')
        final_probability = min(key_score_tuple_e1[1] * ticker_probability_tuple2[1],
                  key_score_tuple_e2[1] * ticker_probability_tuple2[1])

        if ticker_probability_tuple1[0]==ticker_probability_tuple2[0]:
            # tickers match (Case 3)
            match = 3
            logger.info(f'Case 3: Keys do not match, but tickers match with probability {final_probability}')
        else:
            # tickers don't match (Case 4)
            match = 4
            logger.info(f'Case 4: Keys and tickers do not match with probability {final_probability}')

    if match == 4:
        # override case: no match, but entities are very close to each other
        prob_ee = calculate_probability_ee(e1, e2)
        if prob_ee > theta_ee:
            match = 1
            final_probability = prob_ee
            logger.info(f'Case 1: Direct entity comparison overrider with probability {final_probability}')

    if match==4:
        logger.info(f'*****No Match: Case {match} with probability is {final_probability}')
    else:
        logger.info(f'*****Match: Case {match} with probability is {final_probability}')

    return match, final_probability
