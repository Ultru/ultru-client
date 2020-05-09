import os
import pytest

# Global variables
from ultru_client.utils.globals import CLI_GLOBALS, ULTRU_API_KEY

# Ultru Config options
from ultru_client.utils.config import store_username, store_password, list_config, set_store_password

# Authenication to Ultru
from ultru_client.utils.auth import authenticate

# Exceptions
from ultru_client.utils.exceptions import NotAuthorizedError


def test_empty_config(func_config):
    config = list_config()
    assert config.get('username') == ''
    assert config.get('password') == ''
    assert config.get('store_password') == False

def test_store_auth(func_config):
    test_username = 'test_user'
    test_password = 'test_password'
    store_username(test_username)
    store_password(test_password)
    config = list_config()
    assert config.get('username') == test_username
    assert config.get('password') == test_password

@pytest.mark.skip(reason="authenticate function needs to skip cognito for test")
def test_valid_auth(func_config):
    del os.environ["TEST"]
    test_username = 'demo@ultru.io'
    test_password = 'D3mouser!'
    store_username(test_username)
    store_password(test_password)
    authenticate()
    assert ULTRU_API_KEY.apikey 
    assert ULTRU_API_KEY.url
    os.environ["TEST"] = 1

@pytest.mark.skip(reason="authenticate function needs to skip cognito for test")
def test_invalid_auth(func_config):
    del os.environ["TEST"]
    test_username = 'demo@ultru.io'
    test_password = 'badpassword'
    store_username(test_username)
    store_password(test_password)
    with pytest.raises(NotAuthorizedError):
        authenticate()
    os.environ["TEST"] = 1

