from enum import Enum
from collections import namedtuple


# some named tuples here to improve readability
KeyScore = namedtuple('KeyScore', 'key score')
CompanyScore = namedtuple('CompanyScore', 'company score')
CandidateScore = namedtuple('CandidateScore', 'candidate key_score company_score')
PMatch = namedtuple('PMatch', 'probability match_case candidate1_score, candidate2_score')


# note, I put random key names ;-)
class MatchType(Enum):
    FALLBACK = 1
    KEYS_MATCH = 2
    COMPANY_MATCH = 3
    NON_MATCH = 4