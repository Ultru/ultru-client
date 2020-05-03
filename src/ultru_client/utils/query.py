import json
import sys
import requests
from urllib.parse import urljoin

from .record_types import Types
from .scores import Scores
import logging



class Query(object):

    def __init__(self, record_type=None, score=None, **kwargs):
#        self.logger = logging.getLogger()
        self.__body = {}
        if record_type is not None:
            self.by_type(Types.from_type(record_type.upper()))
        if score is not None:
            self.by_score(Scores.from_score(score.upper()))

    @property
    def body(self):
        return self.__body

    def by_type(self, type_):
        assert isinstance(type_, Types)
        self.__body["record_type"] = type_.value
        return self

    def by_score(self, score):
        assert isinstance(score, Scores)
        self.__body["score_low"] = score.low
        self.__body["score_high"] = score.high
        return self

    def set_count(self, counter):
        self.__body['counter'] = counter
        return self

    def count_only(self):
        self._count_only = True
        self.__body['select'] = "count"
        return self

