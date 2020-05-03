from collections import defaultdict
import os
import json
import pathlib
from urllib.parse import urljoin
from moto import mock_cognitoidentity
import requests
import requests_mock
from ultru_client.utils.config import list_config, put_config_value, store_username, store_password
from ultru_client.utils.globals import CLI_GLOBALS, ULTRU_API_KEY, _ULTRU, _ULTR_JOB_STATUS
from ultru_client.utils.utils import (
    init_ultru_client,
    load_queries,
    save_query,
    list_queries,
    submit_query,
    update_jobs,
    get_jobs,
    record_type_choices,
    score_choices,
    get_query_names,
    remove_queries,
    list_jobs,
    list_results,
    pull_api_key,
    list_key,
    set_engagement,
    list_engagement,
    get_results,
    print_summary,
    summarize_results,
    save_jobs
)

os.environ['TEST'] = "1"


def test_verify_ultru_init(module_config):
    store_username('testuser')
    store_password('testpassword')
    init_ultru_client()
    assert os.path.exists(CLI_GLOBALS.ULTRU_CLI_CONFIG_DIR)
    assert os.path.exists(CLI_GLOBALS.RESULTS)
    assert os.path.exists(CLI_GLOBALS.SAVED_QUERY_FILE)
    assert os.path.exists(CLI_GLOBALS.JOBS)
    assert os.path.exists(CLI_GLOBALS.CONFIG)

def test_list_key(module_config):
    _key = list_key()
    assert _key['url'] is None
    assert _key['key'] is None

def test_create_queries(module_config, queries):
    assert len(list_queries()) == 0
    for query in queries:
        save_query(*query)
    assert len(list_queries()) == len(queries)

def test_remove_queries(module_config):
    queries = get_query_names()
    assert len(queries) == len(list_queries())

    remove_queries(queries)

    queries = get_query_names()
    assert len(queries) == len(list_queries())
    assert len(list_queries()) == 0
    assert len(load_queries()) == 0

def test_load_queries(module_config):
    querys = {"new1": {"record_type": "process", "score_low": 0, "score_high": 5}, "new2": {"record_type": "file", "score_low": 9, "score_high": 10}}
    with open(CLI_GLOBALS.SAVED_QUERY_FILE, 'w') as _file:
        json.dump(querys, _file)
    assert len(load_queries()) == 2

def test_set_engagement(module_config):
    test_engagement = 'Researcher'
    set_engagement(test_engagement)
    assert list_engagement() == test_engagement

def test_get_results(results):
    assert get_results() == ['Researcher_new1_1586620316517']


def test_result_summary(results):
    _expected_results = {
        "Count": 7,
    }


    _result = get_results()[0]
    summary = summarize_results(_result)
    assert summary['Count'] == 7
    assert len(summary['Items']) == 22


@mock_cognitoidentity
def test_submit_query(jobs_ep, cognito, api_key, jobs_base_response):
    api_endpoint = urljoin(jobs_ep, "/dev/api/jobs/schedule/Researcher")
    query = {
        "record_type": "process"
    }
    _ULTRU.saved_queries["test_query"] = query
    with requests_mock.Mocker() as mock:
        mock.post(api_endpoint, status_code=200, json=jobs_base_response)
        mock.get(cognito, status_code=200, json=api_key)
        submit_query("test_query")
        test_job = [x for x in _ULTRU.jobs.values()
                    if x.get("api_job_id") ==
                    "496b1172a2f4467b90f9f3a5a4fed212"][0]
        assert test_job["query"] == query
        assert test_job["query_name"] == "test_query"
        assert test_job["status"] == "PENDING"
        assert test_job["api_job_id"] == "496b1172a2f4467b90f9f3a5a4fed212"


@mock_cognitoidentity
def test_update_jobs(jobs_ep, s3_ep, jobs_base_response, cognito, api_key):
    status_endpoint = urljoin(jobs_ep, "/dev/api/jobs/status/Researcher/496b1172a2f4467b90f9f3a5a4fed212")
    query_endpoint = urljoin(jobs_ep, "dev/api/jobs/query/Researcher/496b1172a2f4467b90f9f3a5a4fed212")
    s3_endpoint = urljoin(s3_ep, "/cognito/queries/identity_id/496b1172a2f4467b90f9f3a5a4fed212.json")
    with requests_mock.Mocker() as mock:
        mock.get(status_endpoint, status_code=200, json=jobs_base_response)
        mock.get(query_endpoint, status_code=200, json=jobs_base_response)
        mock.get(s3_endpoint, status_code=200,
                 content=bytes(bytearray(json.dumps({"query_results": []}),
                                         "utf-8")))
        mock.get(cognito, status_code=200, json=api_key)
        update_jobs()
        test_job = [x for x in _ULTRU.jobs.values()
                    if x.get("api_job_id") ==
                    "496b1172a2f4467b90f9f3a5a4fed212"][0]
        assert test_job.get('status') == "FINISHED"
        job_id = "Researcher_test_query_"
        expected = pathlib.Path(CLI_GLOBALS.RESULTS).joinpath(job_id).resolve()
        assert test_job.get('results_file').startswith(str(expected))


def test_save_jobs(module_config):
    _ULTRU.jobs = defaultdict()
    _ULTRU.jobs["test_job_id"] = {
        "query": {"engagement":"Researcher", "record_type": "process", "score_low": 0, "score_high": 5},
        "query_name": "new1",
        "status": _ULTR_JOB_STATUS.FINISHED.name,
        "submited": 0,
        "results_file": "nada"
    }
    save_jobs()

    jobs = get_jobs()
    assert len(jobs) == 1
    assert 'test_job_id' in jobs
    assert jobs['test_job_id'] == {
        "query": {"engagement":"Researcher", "record_type": "process", "score_low": 0, "score_high": 5},
        "query_name": "new1",
        "status": _ULTR_JOB_STATUS.FINISHED.name,
        "submited": 0,
        "results_file": "nada"
    }