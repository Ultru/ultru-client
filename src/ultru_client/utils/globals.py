import enum
import os
from pathlib import Path


class ULTRU_API_KEY:
    apikey = None
    url = None


class baseConfig:
    def __init__(self):
        self.ULTRU_CLI_CONFIG_DIR = os.path.join(Path.home(), ".ultru")
        self.__engagement = 'Researcher'
        self.__cognito = None

    @property
    def SAVED_QUERY_FILE(self):
        return os.path.join(self.ULTRU_CLI_CONFIG_DIR, 'saved_queries')

    @property
    def KEY_FILE(self):
        return os.path.join(self.ULTRU_CLI_CONFIG_DIR, 'ultru.key')

    @property
    def RESULTS(self):
        return os.path.join(self.ULTRU_CLI_CONFIG_DIR, 'results')

    @property
    def JOBS(self):
        return os.path.join(self.ULTRU_CLI_CONFIG_DIR, 'jobs')

    @property
    def CONFIG(self):
        return os.path.join(self.ULTRU_CLI_CONFIG_DIR, 'config')

    @property
    def ENGAGEMENT(self):
        return self.__engagement

    @ENGAGEMENT.setter
    def ENGAGEMENT(self, value):
        self.__engagement = value

    @property
    def COGNITO(self):
        return self.__cognito

    @COGNITO.setter
    def COGNITO(self, value):
        self.__cognito = value

CLI_GLOBALS = baseConfig()

class _ULTR_JOB_STATUS(enum.Enum):
    PENDING = 0
    STARTED = 1
    FINISHED = 2
    FAILED = 3

class _ULTRU:
    saved_queries = dict()
    jobs = dict()
    running_queries = dict()


