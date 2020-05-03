import sys
from urllib.parse import urljoin
import requests
from ultru_query.base import BaseRequestsClass


class Engagements(BaseRequestsClass):
    def reset(self):
        self.data = []
        self.uri = ""
        self.body = {}

    def add(self, name):
        self.logger.info("Adding engagement %s" % name)
        self.uri = urljoin(self.base_url, "engagements/add/%s" % name)
        return self

    def remove(self, name):
        self.logger.info("Removing engagement %s" % name)
        self.uri = urljoin(self.base_url, "engagements/rm/%s" % name)
