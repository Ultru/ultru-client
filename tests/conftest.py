import pytest
import os
from tempfile import TemporaryDirectory
from pathlib import Path
from ultru_client.utils.globals import CLI_GLOBALS, ULTRU_API_KEY, _ULTRU
from ultru_client.utils.record_types import Types
from ultru_client.utils.scores import Scores
import shutil

JOBS_EP = "https://ebtzy3p8ci.execute-api.us-east-2.amazonaws.com"
COGNITO = "https://cognito-idp.us-east-2.amazonaws.com/us-east-2_vF8cq6bRE/.well-known/jwks.json"
S3_EP = "https://ultru-query-artifacts.s3.us-east-2.amazonaws.com"
MOCK_JOB = {
    "identity_id": "identity_id of submitter",
    "effort": "ultru - internal",
    "query": {
        "score_high": "10",
        "score_low": "5",
        "record_type": "process"
    },
    "s3ref": "cognito/queries/identity_id/496b1172a2f4467b90f9f3a5a4fed212.json",
    "client_id": "demo@ultru.io",
    "status": "done",
    "timestamp": 1587848165.8797262,
    "engagement_id": "Researcher",
    "job_id": "496b1172a2f4467b90f9f3a5a4fed212"
}


@pytest.fixture(scope='function')
def func_config(request):
    __temporarydir = TemporaryDirectory()
    CLI_GLOBALS.ULTRU_CLI_CONFIG_DIR = __temporarydir.name

    def fin():
        ULTRU_API_KEY.url = None
        ULTRU_API_KEY.apikey = None
        CLI_GLOBALS.COGNITO = None
        CLI_GLOBALS.ENGAGEMENT = 'Researcher'
        __temporarydir.cleanup()

    request.addfinalizer(fin)


@pytest.fixture(scope='module')
def module_config(request):
    __temporarydir = TemporaryDirectory()
    CLI_GLOBALS.ULTRU_CLI_CONFIG_DIR = __temporarydir.name

    def fin():
        ULTRU_API_KEY.url = None
        ULTRU_API_KEY.apikey = None
        CLI_GLOBALS.COGNITO = None
        CLI_GLOBALS.ENGAGEMENT = 'Researcher'
        __temporarydir.cleanup()

    request.addfinalizer(fin)


@pytest.fixture()
def queries():
    types = list(Types.types.values())
    scores = list(Scores.scores.keys())
    base = 'test'
    queries = list()
    for y in types:
        for z in scores:
            queries.append(('{}_{}_{}'.format(base, y, z), y, z))
    return queries


@pytest.fixture(scope='module')
def results(request):
    results_path = Path(__file__).resolve().parent.joinpath('resources').joinpath('results')
    os.rmdir(CLI_GLOBALS.RESULTS)
    shutil.copytree(results_path, CLI_GLOBALS.RESULTS)


@pytest.fixture(scope="session")
def jobs_ep():
    return JOBS_EP


@pytest.fixture(scope="session")
def s3_ep():
    return S3_EP


@pytest.fixture(scope="session")
def cognito():
    return COGNITO


@pytest.fixture(scope="session")
def mock_job():
    return MOCK_JOB


@pytest.fixture(scope="session")
def jobs_base_response(mock_job):
    return {
        "statusCode": 200,
        "body": mock_job
    }


@pytest.fixture(scope="session")
def api_key():
    mypath = Path(__file__).parent
    with open(mypath.joinpath('resources', 'ultru.key')) as fp:
        API_KEY = fp.read()

    return API_KEY

