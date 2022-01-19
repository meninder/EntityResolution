from enum import Enum
from collections import namedtuple, OrderedDict


# some named tuples here to improve readability
KeyScore = namedtuple('KeyScore', 'key score')
CompanyScore = namedtuple('CompanyScore', 'company score')
CandidateScore = namedtuple('CandidateScore', 'candidate key_score company_score')
PMatch = namedtuple('PMatch', 'probability match_case candidate1_score, candidate2_score')


class MatchType(Enum):
    FALLBACK = 1
    KEYS_MATCH = 2
    COMPANY_MATCH = 3
    NON_MATCH = 4


def namedtuple_asdict(obj):
    '''
    This function converts a named tuple into a dictionary so that the output can be json'd.
    '''

    if hasattr(obj, "_asdict"): # detect namedtuple
        return OrderedDict(zip(obj._fields, (namedtuple_asdict(item) for item in obj)))
    elif isinstance(obj, str): # iterables - strings
        return obj
    elif hasattr(obj, "keys"): # iterables - mapping
        return OrderedDict(zip(obj.keys(), (namedtuple_asdict(item) for item in obj.values())))
    elif hasattr(obj, "__iter__"): # iterables - sequence
        return type(obj)((namedtuple_asdict(item) for item in obj))
    else: # non-iterable cannot contain namedtuples
        return obj