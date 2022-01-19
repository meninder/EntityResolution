from dynamo_utils import get_all_keys, get_key_probability_and_name
from jellyfish import jaro_similarity
from string_cleaning_utils import clean_org
import logging
from data_utils import MatchType
from data_utils import KeyScore, CompanyScore, CandidateScore, PMatch

BLN_LOCAL_RUN = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
logger.addHandler(streamHandler)


def get_candidate_string_similarity_score(candidate1: str, candidate2: str) -> float:
    """
    Calculate similarity between candidate1 and 2.
    Fall back matching logic relies on this similarity value (Case 1)
    """

    return jaro_similarity(candidate1, candidate2)


def get_candidate_key_score(candidate: str, keys: list) -> KeyScore:
    '''
    for each key, calculate similarity w candidate
    '''

    candidate_clean = clean_org(candidate)
    scores = [(k, jaro_similarity(candidate_clean, k)) for k in keys]
    scores.sort(key=lambda x: x[1], reverse=True)
    highest_score = scores[0]
    return KeyScore(key=highest_score[0], score=highest_score[1])


def get_candidate_company_score(key: str) -> CompanyScore:
    '''
    Given a key, retrieve the value from Dynamo (non-local)
    The value is converted to a CompanyScore type in the function
    To debug, a local value is generated.
    '''
    if BLN_LOCAL_RUN:
        return CompanyScore(company='facebook', score=0.1)
    else:
        return get_key_probability_and_name(key)


def get_candidate_score(candidate: str, keys: list) -> CandidateScore:
    '''
    for a "candidate", finds "key" and "company", with corresponding scores.
    '''

    key_score = get_candidate_key_score(candidate, keys)
    company_score = get_candidate_company_score(key_score[0])

    return CandidateScore(candidate=candidate, key_score=key_score, company_score=company_score)


def calculate_probability_match(candidate1_score: CandidateScore,
                                candidate2_score: CandidateScore,
                                theta: float = 0.75) -> PMatch:

    '''
    Takes the keys and companies for each candidate and then calculates the probability of a match.
    There are four cases:
    Case 1: Fallback method.  If candidate strings are close (>theta similarity) and all other matching checks fail.
    Case 2: Keys match.  (c1=facebook, c2=fanebook will map to the same key; so don't need to look at company)
    Case 3: Keys don't match, Companies do (c1=facebook, c2=meta platforms will have diff keys but map to meta platforms)
    Case 4: Keys and company doesn't match.  Check if strings themselves are very close (Case 1) otherwise call No Match.
    '''

    # find match case and final probability
    if candidate1_score[1][0] == candidate2_score[1][0]:
        final_probability = min(candidate1_score[1][1], candidate2_score[1][1])  # using key scores
        match_case = MatchType.KEYS_MATCH.value
        logger.info(f'Case 2: Keys match with probability {final_probability}')
    else:
        final_probability = min(candidate1_score[1][1] * candidate1_score[2][1],
                                candidate2_score[1][1] * candidate1_score[2][1])
        if candidate1_score[2][0] == candidate2_score[2][0]:  # using company, which match
            match_case = MatchType.COMPANY_MATCH.value
            logger.info(f'Case 3: Keys do not match, but tickers match with probability {final_probability}')
        else:  # keys, company do not match, check candidate-candidate match
            candidate_similarity_score = get_candidate_string_similarity_score(candidate1_score[0], candidate2_score[0])
            if candidate_similarity_score > theta:  # override mismatch
                match_case = MatchType.FALLBACK.value
                final_probability = candidate_similarity_score
                logger.info(f'Case 1: Direct entity comparison overrider with probability {final_probability}')
            else:  # no match
                match_case = MatchType.NON_MATCH.value
                logger.info(f'Case 4: No Match with probability is {final_probability}')

    return PMatch(probability=final_probability,
                  match_case=match_case,
                  candidate1_score=candidate1_score,
                  candidate2_score=candidate2_score)


def get_pmatch(candidate1: str, candidate2: str, keys: list, theta: float=0.75) -> PMatch:
    '''
    Input the two candidates, get their key & company and resp scores, then calculate matching probability
    '''

    candidate1_score = get_candidate_score(candidate=candidate1, keys=keys)
    logger.info(f'{candidate1_score[0]} is mapped to key {candidate1_score[1][0]} with probability {candidate1_score[1][1]}')
    logger.info(f'{candidate1_score[0]} is mapped to company {candidate1_score[2][0]} with probability {candidate1_score[2][1]}')

    candidate2_score = get_candidate_score(candidate=candidate2, keys=keys)
    logger.info(f'{candidate2_score[0]} is mapped to key {candidate2_score[1][0]} with probability {candidate2_score[1][1]}')
    logger.info(f'{candidate2_score[0]} is mapped to company {candidate2_score[2][0]} with probability {candidate2_score[2][1]}')

    pmatch = calculate_probability_match(candidate1_score, candidate2_score, theta)
    logger.info(f'Ouput PMatch: {pmatch}')

    return pmatch


def testing_function():
    candidate1, candidate2 = 'facebook', 'fanebook' # Case 2
    candidate1, candidate2 = 'facebook', 'bool'  # Case 3 (Local)
    candidate1, candidate2 = 'facebook', 'bool'  # Case 4 (Non-Local)

    if BLN_LOCAL_RUN:
        lst_keys = ['faceboooook', 'face', 'book', 'test_case']
    else:
        lst_keys = get_all_keys()

    pmatch = get_pmatch(candidate1, candidate2, lst_keys, theta=0.75)

    return pmatch


def example_pmatch():
    '''
    Example PMatch data for debugging purposes
    '''
    key1_score = KeyScore(key='bank', score=1.0)
    company1_score = CompanyScore(company='Bank of America', score=0.7555555555555555)
    key2_score = KeyScore(key='bofa', score=1.0)
    company2_score = CompanyScore(company='Bank of America', score=0.7555555555555555)

    pm = PMatch(probability=0.7555555555555555,
                match_case=3,
                candidate1_score=CandidateScore(candidate='bank',
                                                key_score=key1_score,
                                                company_score=company1_score),
                candidate2_score=CandidateScore(candidate='bofa',
                                                key_score=key2_score,
                                                company_score=company2_score)
                )
    return pm
