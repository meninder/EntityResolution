from enum import Enum
from collections import namedtuple


# some named tuples here to improve readability
ScoredKey = namedtuple('ScoredKey', 'key score')
Ticker = namedtuple('Ticker', 'ticker probability')
Entity = namedtuple('Entity', 'scores ticker')
PMatch = namedtuple('PMatch', 'probability match_case source target')


# note, I put random key names ;-)
class MatchType(Enum):
    MAYBE = 1
    PERFECT = 2
    TICKER = 3
    FOO = 4