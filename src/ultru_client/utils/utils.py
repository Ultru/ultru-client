import enum
import getpass
import json
import os
from pathlib import Path
import requests
import time
from urllib.parse import urljoin
import uuid

from .auth import authenticate
from .exceptions import NotAuthorizedError, UserUnknownError
from .globals import ULTRU_API_KEY, CLI_GLOBALS, _ULTR_JOB_STATUS, _ULTRU
from .base import BaseRequestsClass
from .engagements import Engagements
from .query import Query
from .jobs import get_job_results, job_status, submit_job
from .record_types import Types
from .scores import Scores


record_type_choices = Types.types.values()

score_choices = [
    "benign",
    "suspicious",
    "malicious",
    "malware"
]

def __authenticate():
    try:
        authenticate()
    except NotAuthorizedError:
        print(f"Invalid password")
    except UserUnknownError:
        print(f"Invalid username")

def init_ultru_client():
    if not os.path.exists(CLI_GLOBALS.ULTRU_CLI_CONFIG_DIR):
        os.mkdir(CLI_GLOBALS.ULTRU_CLI_CONFIG_DIR)

    if not os.path.exists(CLI_GLOBALS.RESULTS):
        os.mkdir(CLI_GLOBALS.RESULTS)

    if not os.path.exists(CLI_GLOBALS.SAVED_QUERY_FILE):
        with open(CLI_GLOBALS.SAVED_QUERY_FILE, 'w') as _file:
            json.dump(dict(), _file)

    if not os.path.exists(CLI_GLOBALS.JOBS):
        with open(CLI_GLOBALS.JOBS, 'w') as _file:
            json.dump(dict(), _file)

    if not os.path.exists(CLI_GLOBALS.CONFIG):
        with open(CLI_GLOBALS.CONFIG, 'w') as config_fp:
            json.dump({
                "username": "",
                "password": "",
                "store_password": False
            }, config_fp)


    _ULTRU.saved_queries = load_queries()
    _ULTRU.jobs = get_jobs()

    __authenticate()

def set_engagement(engagement):
    CLI_GLOBALS.ENGAGEMENT = engagement

def list_engagement():
    return CLI_GLOBALS.ENGAGEMENT

def load_queries(queryfile=None):
    if queryfile is None:
        queryfile = CLI_GLOBALS.SAVED_QUERY_FILE
    if os.path.exists(queryfile):
        with open(queryfile) as _file:
            data = json.load(_file)
        return data
    return dict()

def list_queries():
    return dict(_ULTRU.saved_queries)


def list_results():
    return os.listdir(CLI_GLOBALS.RESULTS)

def get_results():
    return os.listdir(CLI_GLOBALS.RESULTS)

def list_key():
    return {"url": ULTRU_API_KEY.url,
            "key": ULTRU_API_KEY.apikey}

def save_query(query_name, record_type, score, queryfile=None):
    if queryfile is None:
        queryfile = CLI_GLOBALS.SAVED_QUERY_FILE
    query = Query(record_type, score)
    current_queries = load_queries(queryfile)
    current_queries[query_name] = query.body
    with open(queryfile, 'w') as _file:
        json.dump(current_queries, _file)
    _ULTRU.saved_queries = current_queries

def get_query_names():
    return list(_ULTRU.saved_queries.keys())

def remove_queries(queries, queryfile=None):
    """
    queries - list of queries to remove from saved queries
    """
    if queryfile is None:
        queryfile = CLI_GLOBALS.SAVED_QUERY_FILE
    for q in queries:
        del _ULTRU.saved_queries[q]
    with open(queryfile, 'w') as _file:
        json.dump(_ULTRU.saved_queries, _file)


def execute_query(query, job_id):
    __authenticate()
    headers = {"Content-Type": "application/json", "Authorization": ULTRU_API_KEY.apikey}
    url = urljoin(ULTRU_API_KEY.url, 'query/score')
    response = requests.post(url, headers=headers, json=query)
    new_result_file = os.path.join(CLI_GLOBALS.RESULTS, job_id)
    try:
        results = response.json()
        with open(new_result_file, 'w') as _file:
            json.dump(results, _file)
    except Exception as e:
        print(e)
        print(response.text)
        results = response.text
        with open(new_result_file, 'w') as _file:
            _file.write(results)

    return new_result_file

def print_summary(result):
    print(json.dumps(summarize_results(result), indent=4))


def summarize_results(result):
    results_file = os.path.join(CLI_GLOBALS.RESULTS, result)
    with open(results_file) as _file:
        result = json.load(_file)
    itms = {}
    for x in result['Items']:
         for k,v in x.items():
             if isinstance(v, str):
                item_set = itms.setdefault(k, set())
                item_set.add(v)
    summary = {
        "Count": result['Count'],
        "Items": {k:list(v) for k,v in itms.items()}
    }
    return summary

def save_jobs():
    with open(CLI_GLOBALS.JOBS, 'w') as _file:
        json.dump(_ULTRU.jobs,_file, indent=4)

def submit_query(query_name, engagement=None):
    if engagement is None:
        engagement = CLI_GLOBALS.ENGAGEMENT
    if query_name in _ULTRU.saved_queries:
        query = _ULTRU.saved_queries[query_name]
        tmp = dict(**query)
        tmp['engagement_id'] = engagement
        submitted_time = int(time.time() * 1000)
        job_id = "{}_{}_{}".format(engagement, query_name, submitted_time)
        api_job_id = submit_job(engagement, tmp)
        if api_job_id is None:
            print(f"Invalid job id returned, not storing job")
            return
        _ULTRU.jobs[job_id] = {
            "query": query,
            "query_name": query_name,
            "status": _ULTR_JOB_STATUS.PENDING.name,
            "submitted": submitted_time,
            "results_file": None,
            "api_job_id": api_job_id,
        }
        save_jobs()
    else:
        pass

def remove_jobs(job_status, engagement=None):
    if engagement is None:
        engagement = CLI_GLOBALS.ENGAGEMENT
    tmp_jobs = dict(_ULTRU.jobs)
    for job_name, job_content in tmp_jobs.items():
        if job_content['status'] in job_status:
                del _ULTRU.jobs[job_name]
    save_jobs()

def list_jobs():
    return dict(_ULTRU.jobs)

def update_jobs(engagement=None):
    if engagement is None:
        engagement = CLI_GLOBALS.ENGAGEMENT
    active_ids = {k: v.get('api_job_id') for k, v in _ULTRU.jobs.items()
                  if v.get('status') != _ULTR_JOB_STATUS.FINISHED.name
                  and v.get('status') != _ULTR_JOB_STATUS.FAILED.name}
    for job_id, api_job_id in active_ids.items():
        backend_status = job_status(engagement, api_job_id)
        if backend_status == "new":
            _ULTRU.jobs[job_id]['status'] = _ULTR_JOB_STATUS.PENDING.name
        elif backend_status == "running":
            _ULTRU.jobs[job_id]['status'] = _ULTR_JOB_STATUS.STARTED.name
        elif backend_status == "done":
            _ULTRU.jobs[job_id]['status'] = _ULTR_JOB_STATUS.FINISHED.name
            _ULTRU.jobs[job_id]['results_file'] = store_results(engagement, job_id)
        elif backend_status == "failed":
            _ULTRU.jobs[job_id]['status'] = _ULTR_JOB_STATUS.FAILED.name
        else:
            print(f"Unknown status returned from API; {backend_status}")

    save_jobs()


def store_results(engagement_id: str, job_id: str):
    if not job_id in _ULTRU.jobs.keys():
        print(f"Job {job_id} not found")
        return
    api_job_id = _ULTRU.jobs[job_id].get('api_job_id')
    content = get_job_results(engagement_id, api_job_id)
    new_result_file = os.path.join(CLI_GLOBALS.RESULTS, job_id)
    try:
        with open(new_result_file, 'wb') as _file:
            _file.write(content)
    except Exception as e:
        print(e)
    return new_result_file


def pull_api_key():
    username = input('Username: ')
    password = getpass.getpass(prompt="Password: ")

    print(username)
    print(password)


    data = {}
    assert data, "No data found"
    return data


def get_jobs():
    if not os.path.exists(CLI_GLOBALS.JOBS):
        data = {}
    else:
        with open(CLI_GLOBALS.JOBS) as _file:
            data = json.load(_file)
    return data

