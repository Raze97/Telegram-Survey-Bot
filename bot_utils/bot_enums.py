from enum import Enum


class SurveyType(Enum):
    """
    Enum for the different survey types.
    """
    SUBSCRIBE = 1
    DAILY = 2
    END = 3


class EndUrlDistribution(Enum):
    """
    Enum for the different end distribution strategies.
    """
    NONE = 0
    DAY = 1
    TIME = 2
    MIXED = 3
    RANDOM = 4

