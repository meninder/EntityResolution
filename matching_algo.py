from typing import Dict
from dynamo_utils import get_all_keys, get_key_probability_and_name
from jellyfish import jaro_similarity
from string_cleaning_utils import clean_org
import logging
from data_utils import MatchType
from data_utils import ScoredKey, Ticker, Entity, PMatch


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
logger.addHandler(streamHandler)


def calculate_probability_ee(e1, e2):
    """
    Comment here etc.
    """
    p_ee = jaro_similarity(e1, e2)
    return p_ee


# not sure if name is correct, but just breaking down the other function
# now the actual function is more modular and can be easilty tested with unit tests etc
def score_candidates(candidates: list[str], keys: list) -> list[ScoredKey]:
    """
    Comment here etc.
    """
    # this is lazy, as I'm returning a list following the same candidate order
    # the best thing wuold be however to build a small class with source and target, and make explicit
    # the link between candidates and their score
    # here, I'm doing a first pass in making it modular
    return [ get_largest_candidate_key(c, keys) for c in candidates ]


def get_largest_candidate_key(candidate: str, keys: list) -> ScoredKey:
    """
    Comment here etc.
    """
    clean_candidate = clean_org(candidate) # not sure about this here, but for now it's ok
    scores = [(k, jaro_similarity(clean_candidate, k)) for k in keys]
    scores.sort(key=lambda x: x[1], reverse=True)

    return ScoredKey(scores[0], scores[1])


# same trick as above
def get_company_probabilities(candidates: list[str]) -> list[Ticker]:
    """
    Comment here etc.
    """
    return [get_candidate_company_probability(c) for c in candidates]


# we just need the names as input here
def get_candidate_company_probability(candidate: str):
    """
    Comment here etc.
    """
    ticker_probability = get_key_probability_and_name(candidate)

    return Ticker(ticker=ticker_probability[0], probability=ticker_probability[1])


# I would type all input in all function if not super painful
# it really improves code a lot
def calculate_probability_match(e1: str, e2: str, theta_ee: float = 0.75) -> PMatch:
    """
    
    Comments here, as in the main. Brief function description 
    and params description, for example following google style:

    https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html

    Note: I'm removing some logging to focus on logic, not because logging is bad

    """

    # theta_ee = 0.75 # commenting it for now, pass it from outside with a default, to make function testable
    # theta_l = 0.65  # is this used at all? Commenting it for now

    # this is a call to a db, so probably should check for error
    keys = get_all_keys()
    return  calculate_match_with_keys(e1, e2, keys, theta_ee)


# def isolate the function so we can run it locally
def calculate_match_with_keys(e1: str, e2: str, keys: list, theta_ee: float) -> PMatch:
    entities = [e1, e2]
    # get k1, k2 (candidate synomous with key)
    # probably terrible variable name
    candidates_best_scores = score_candidates(entities, keys)

    # if it's a perfect match (if I get it, hope I'm reading it right)
    if candidates_best_scores[0].key == candidates_best_scores[1].key:
        # return here and avoid one level of nesting
        return PMatch(
            probability=min(candidates_best_scores[0].score, candidates_best_scores[1].score),
            match_case=MatchType.PERFECT,
            source=Entity(scores=candidates_best_scores[0], ticker=None),
            target=Entity(scores=candidates_best_scores[1], ticker=None)
            )
    # if not, let's proceed with the other cases
    
    # get tickers corresponding to keys
    candidates = [candidates_best_scores[0].key, candidates_best_scores[1].key]
    ticker_probabilities = get_company_probabilities(candidates)
    # preparing entities for response
    source = Entity(scores=candidates_best_scores[0], ticker=ticker_probabilities[0])
    target = Entity(scores=candidates_best_scores[1], ticker=ticker_probabilities[1]) 
    prob = min(candidates_best_scores[0].score * ticker_probabilities[0].probability, candidates_best_scores[1].score * ticker_probabilities[1].probability)  
    # if tickers match (Case 3)  
    if ticker_probabilities[0].ticker == ticker_probabilities[1].ticker:
        # return here and avoid one level of nesting
        return PMatch(
            probability=prob,
            match_case=MatchType.TICKER,
            source=source,
            target=target
            )
    # if not, let's proceed with the other cases
    
    # override case: no match, but entities are very close to each other
    prob_ee = calculate_probability_ee(clean_org(e1), clean_org(e2))
    if prob_ee > theta_ee:
        # this is case 1 again
        return PMatch(
            probability=prob_ee,
            match_case=MatchType.MAYBE,
            source=source,
            target=target
            )

    # if nothing else matched, we return this
    return PMatch(
            probability=prob,
            match_case=MatchType.FOO,
            source=source,
            target=target
            )

    