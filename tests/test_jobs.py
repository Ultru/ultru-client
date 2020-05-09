from collections import defaultdict
from os import environ
import pathlib
from urllib.parse import urljoin
from moto import mock_cognitoidentity, mock_s3
import requests
import requests_mock
from ultru_client.utils.jobs import get_job_results, job_status, list_jobs
from ultru_client.utils.jobs import query_job, submit_job

environ['TEST'] = "1"

@mock_cognitoidentity
def test_submit_job(jobs_ep, cognito, api_key, jobs_base_response):
    api_endpoint = urljoin(jobs_ep, "/dev/api/jobs/schedule/Researcher")
    query = {
        "record_type": "process"
    }
    with requests_mock.Mocker() as mock:
        mock.post(api_endpoint, status_code=200, json=jobs_base_response)
        mock.get(cognito, status_code=200, json=api_key)
        assert submit_job("Researcher", query) == "496b1172a2f4467b90f9f3a5a4fed212"


@mock_cognitoidentity
def test_query_job(jobs_ep, mock_job, cognito, api_key, jobs_base_response):
    api_endpoint = urljoin(jobs_ep, "/dev/api/jobs/query/Researcher/496b1172a2f4467b90f9f3a5a4fed212")
    with requests_mock.Mocker() as mock:
        mock.get(api_endpoint, status_code=200, json=jobs_base_response)
        mock.get(cognito, status_code=200, json=api_key)
        assert query_job("Researcher", "496b1172a2f4467b90f9f3a5a4fed212") == mock_job

@mock_cognitoidentity
def test_list_job(jobs_ep, mock_job, cognito, api_key):
    api_endpoint = urljoin(jobs_ep, "/dev/api/jobs/list/Researcher")
    json_resp = defaultdict(dict)
    json_resp['statusCode'] = 200
    json_resp['body']['jobs'] = [mock_job]
    with requests_mock.Mocker() as mock:
        mock.get(api_endpoint, status_code=200, json=json_resp)
        mock.get(cognito, status_code=200, json=api_key)
        resp = list_jobs("Researcher")
        assert resp[0].get('job_id') == "496b1172a2f4467b90f9f3a5a4fed212"


@mock_cognitoidentity
def test_job_status(jobs_ep, jobs_base_response, api_key, cognito):
    status_endpoint = urljoin(jobs_ep, "/dev/api/jobs/status/Researcher/496b1172a2f4467b90f9f3a5a4fed212")
    with requests_mock.Mocker() as mock:
        mock.get(status_endpoint, status_code=200, json=jobs_base_response)
        mock.get(cognito, status_code=200, json=api_key)
        assert job_status("Researcher", "496b1172a2f4467b90f9f3a5a4fed212") == "done"


@mock_cognitoidentity
@mock_s3
def test_get_job_results(jobs_ep, s3_ep, jobs_base_response, api_key, cognito):
    api_endpoint = urljoin(jobs_ep, "/dev/api/jobs/query/Researcher/496b1172a2f4467b90f9f3a5a4fed212")
    s3_endpoint = urljoin(s3_ep, "/cognito/queries/identity_id/496b1172a2f4467b90f9f3a5a4fed212.json")
    get_url_endpoint = urljoin(jobs_ep, "/dev/api/jobs/get_url/496b1172a2f4467b90f9f3a5a4fed212")
    with requests_mock.Mocker() as mock:
        mock.get(api_endpoint, status_code=200, json=jobs_base_response)
        mock.get(s3_endpoint, status_code=200, content=b"query_results")
        mock.get(get_url_endpoint, status_code=200, json={"test": {}})
        mock.get(cognito, status_code=200, json=api_key)
        assert get_job_results("Researcher", "496b1172a2f4467b90f9f3a5a4fed212") == b"query_results"

