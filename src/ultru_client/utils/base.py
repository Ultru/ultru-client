import json
import logging
import os
import sys
from urllib.parse import urljoin
import requests
from .record_types import Types

class BaseRequestsClass:
    def __init__(self, api_key, session=None):
        self.setup_logger()

        if not isinstance(api_key, dict):
            self.logger.error('Expecting a dictionary formatted API KEY')
            raise AttributeError(f"api_key is improperly formatted")

        if api_key.get('apikey') is None:
            self.logger.error('Invalid api key passed')
            raise AttributeError(f"api_key cannot be None")

        if session is None:
            self.session = requests.Session()
        else:
            self.session = session

        self.data = []
        self.body = {}
        self.headers = {"Content-Type": "application/json", "Authorization": api_key.get('apikey')}
        self.base_url = api_key.get('url')
        self.api_key = api_key

        if self.base_url is None:
            self.logger.error('Invalid api key passed')
            raise AttributeError('URL not in api key')

        self.set_uri('/')
        self.reset()

    def setup_logger(self):
        self.logger = logging.getLogger(__name__)# {{{}}}
        loglevel = os.environ.get('LOGLVL', logging.INFO)
        logfile = os.environ.get("LOGFILE", "ultru.log")

        fh = logging.FileHandler(logfile)
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
        fm = logging.Formatter(FORMAT)
        fh.setFormatter(fm)
        ch.setFormatter(fm)

        logging.basicConfig(handlers=[fh, ch], level=int(loglevel) * 10)

    def set_uri(self, path):
        if self.base_url.startswith("http"):
            self.uri = urljoin(self.base_url, path)
        elif self.base_url.startswith("mock"):
            self.uri = self.base_url + path
        else:
            raise AttributeError("Invalid base url (expect http or https)")
        self.logger.debug(f"Set URI: {self.uri}")

    def execute(self):
        def do_the_execute():
            self.logger.debug(f"uri: {self.uri}; body: {self.body}; data: {self.data}")
            if self.body:
                resp = self.session.post(self.uri, headers=self.headers, data=json.dumps(self.body))
            else:
                resp = self.session.get(self.uri, headers=self.headers)
            outer_status_code = resp.status_code
            if outer_status_code == 200:
                body = resp.json()
                inner_status_code = body.get('statusCode')
                if inner_status_code == 200:
                    self.handle_json(body)
                else:
                    self.handle_error(body)
            else:
                self.logger.error(f"Server responded: {resp.status_code}")
                if resp.status_code == 403:
                    self.logger.error(f"Forbidden error 403; check your Ultru API key is valid, otherwise notify the developer for an invalid GET/POST or URL")
                else:
                    try:
                        self.handle_error(resp.json())
                    except Exception as exc:
                        self.logger.error(exc)

        if not self.uri:
            self.logger.error("Require by_* function before running execute")
        if not "engagement" in self.body:
            self.logger.error("Require set_engagement function before running execute")

        if "retrieve_all_types" in self.__dict__.keys():
            if self.retrieve_all_types:
                for _type in Types.types.values():
                    self.body["record_type"] = _type
                    do_the_execute()
                return self

        do_the_execute()

        return self

    def reset(self):
        """Override me for reset functionality"""
        pass

    def set_engagement(self, engagement):
        self.body['engagement'] = engagement
        return self
