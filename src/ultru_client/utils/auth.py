from getpass import getpass
from os import environ
import boto3
from warrant import Cognito
from .config import get_config_value, put_config_value
from .exceptions import NotAuthorizedError, UserUnknownError
from .globals import CLI_GLOBALS, ULTRU_API_KEY

USER_POOL_ID = "us-east-2_vF8cq6bRE"
CLIENT_ID = "2qr12uvr74uc683vp0ekg98u80"
API_URL = {
    "legacy": "https://t24s740ln5.execute-api.us-east-2.amazonaws.com/dev/api/",
    "jobs": "https://ebtzy3p8ci.execute-api.us-east-2.amazonaws.com/dev/api/",
    "s3": "https://ultru-query-artifacts.s3.us-east-2.amazonaws.com/",
}

def __hint():
    print("Authenticate using your ultru.io credentials...")

def __do_authenticate(username):
    client = boto3.client('cognito-idp')
    password = __get_password()
    try:
        CLI_GLOBALS.COGNITO.authenticate(password)
    except client.exceptions.NotAuthorizedException as exc:
        raise NotAuthorizedError("", f"Invalid password for user {username}")
    except ValueError as exc:
        raise UserUnknownError("", f"User {username} is unknown or account does not exist")

def __get_password():
    if get_config_value('password') == '':
        password = getpass(f"Password: ")
        if get_config_value('store_password'):
            put_config_value('password', password)
    else:
        password = get_config_value('password')
    return password

def __get_username():
    username = get_config_value('username')
    if username == '':
        __hint()
        username = input("Email: ")
        put_config_value('username', username)
    return username

def authenticate(api_type="legacy"):
    """Authenticate to Ultru API and store api key.

    .. note:: will account for multiple API types that can be set using the
    api_type parameter
    """
    # Store the API URL based on request
    ULTRU_API_KEY.url = API_URL[api_type]

    # We are currently unable to sufficiently mock cognito with moto or
    # localstack (need to look further into this)
    if environ.get('TEST'):
        return

    # Static
    username = __get_username()
    if CLI_GLOBALS.COGNITO is None:
        CLI_GLOBALS.COGNITO = Cognito(USER_POOL_ID, CLIENT_ID, username=username)
        __do_authenticate(username)
    else:
        try:
            CLI_GLOBALS.COGNITO.check_token()
        except AttributeError:
            # In the case that we never authenticated properly:
            __do_authenticate(username)

    if CLI_GLOBALS.COGNITO is None:
        raise SystemError('Ultru authentication failed')

    ULTRU_API_KEY.apikey = CLI_GLOBALS.COGNITO.id_token

