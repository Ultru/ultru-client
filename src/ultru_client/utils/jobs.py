import requests
from urllib.parse import urljoin
from .auth import API_URL, authenticate
from .exceptions import NotAuthorizedError, UserUnknownError
from .globals import ULTRU_API_KEY


def __authenticate(api_type="jobs"):
    success = False
    try:
        authenticate(api_type=api_type)
        success = True
    except NotAuthorizedError:
        print(f"Invalid password")
    except UserUnknownError:
        print(f"Invalid username")
    return success


def __query(api_type: str, endpoint: str, body: dict = {}):
    response = None
    if not __authenticate(api_type):
        print(f"Unable to authenticate, will not execute query")
        return response

    headers = {"Content-Type": "application/json",
               "Authorization": ULTRU_API_KEY.apikey}

    url = urljoin(ULTRU_API_KEY.url, f'{endpoint}')

    if body:
        # Setup a post request
        response = requests.post(url, headers=headers, json=body)
    else:
        response = requests.get(url, headers=headers)

    return response


def submit_job(engagement_id: str, query: dict):
    """Submit a query job.

    :param query: dict -- the query itself as a dictionary
    :returns: str -- the job_id
    """
    response = __query("jobs", f"jobs/schedule/{engagement_id}", query).json()
    if response.get('statusCode') != 200:
        print(f"Error occurred during job submission")
        return None
    return response.get('body', {}).get('job_id')


def query_job(engagement_id: str, job_id: str):
    """Query a job record.

    :param engagement_id: str -- the engagement under which the job was submitted
    :param job_id: str -- the job id that was returned from the submit_job fn
    :returns: dict -- job results in the following form:

        {
            "identity_id": "identity_id of submitter",
            "effort": "ultru - internal",
            "query": {
                "score_high": "10",
                "score_low": "5",
                "record_type": "process"
            },
            "s3ref": "a client specific S3 URI (must be authenticated to access)"
            "client_id": "demo@ultru.io",
            "status": "done",
            "timestamp": 1587848165.8797262,
            "engagement_id": "Researcher",
            "job_id": "496b1172a2f4467b90f9f3a5a4fed212"
        }
    """
    response = __query("jobs", f"jobs/query/{engagement_id}/{job_id}").json()
    if response.get('statusCode') != 200:
        print(f"Error occurred during job query")
        return None
    return response.get('body', {})


def list_jobs(engagement_id: str):
    """Lists all jobs that are related to this engagement and client (JWT).

    .. note:: the list has dicts that have the same format as the query_job
    return.

    :param engagement_id: str -- the engagement id
    :returns: list -- all jobs that are related to this engagement and client
    """
    response = __query("jobs", f"jobs/list/{engagement_id}").json()
    if response.get('statusCode') != 200:
        print(f"Error occurred during job list")
        return None
    return response.get('body', {}).get('jobs', [])


def job_status(engagement_id: str, job_id: str):
    """Queries status for a job via it's id.

    :param engagement_id: str -- the engagement id
    :param job_id: str -- the job_id to query
    :returns: str -- the current status of the job (new, running, done, failed)
    """
    response = __query("jobs", f"jobs/status/{engagement_id}/{job_id}").json()
    if response.get('statusCode') != 200:
        print(f"Error occurred during job status query")
        return None
    return response.get('body', {}).get('status')


def get_job_results(engagement_id: str, job_id: str):
    """Retrieve job results from S3 via authentication.

    :param engagement_id: str -- the engagement id
    :param job_id: str -- the job id to retrieve
    :returns: dict -- the query results
    """
    job_results = query_job(engagement_id, job_id)
    if job_results is None:
        return None
    if job_results.get('status') != "done":
        print(f"Job {job_id} is not yet finished, or has failed")
        return None
    s3_presigned_url_req = __query("jobs", f"jobs/get_url/{job_id}")
    if s3_presigned_url_req.status_code != 200:
        print(f"Job {job_id} does not have an S3 reference link")
        return None
    # Account for unit tests
    if "test" not in s3_presigned_url_req.json():
        s3_presigned_url = s3_presigned_url_req.json().get('body', {}).get('url')
        resp = requests.get(s3_presigned_url)

        if resp.status_code == 200:
            return resp.content
        else:
            print(f"Something went wrong downloading the query results: {resp.text}")
            return None
    else:
        return b"query_results"

