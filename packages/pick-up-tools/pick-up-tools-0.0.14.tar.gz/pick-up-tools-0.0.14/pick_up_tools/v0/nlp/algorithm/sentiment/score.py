from .by_dict.preidict import predict as sentiment_by_dict
from .by_dict.jiojionlp.predict import predict as sentiment_by_dict_2

from .by_bayes.jiagunlp import predict as sentiment_by_bayes
from .by_bayes.snow import predict as sentiment_by_bayes_2

from .by_robert_pre_train import predict as sentiment_by_robert_pre_train, \
    enable as ro_enable

import numpy as np

WEIGHT = [3, 1, 2]
PROCESS = [
    sentiment_by_dict,
    sentiment_by_bayes,
    sentiment_by_robert_pre_train
]
if not ro_enable:
    WEIGHT, PROCESS = WEIGHT[:2], PROCESS[:2]


def sentiment_score(text):
    weight = np.array(WEIGHT)
    _score = np.array([p(text) for p in PROCESS])
    score = (_score * weight).sum() / weight.sum()
    return score
