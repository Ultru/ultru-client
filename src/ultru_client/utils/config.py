import json
import os
from .globals import CLI_GLOBALS

def __maybe_init_config():
    if not os.path.exists(CLI_GLOBALS.ULTRU_CLI_CONFIG_DIR):
        os.mkdir(CLI_GLOBALS.ULTRU_CLI_CONFIG_DIR)
    if not os.path.exists(CLI_GLOBALS.CONFIG):
        with open(CLI_GLOBALS.CONFIG, 'w') as config_fp:
            json.dump({
                "username": "",
                "password": "",
                "store_password": False
            }, config_fp)

def __store_config(field, value):
    __maybe_init_config()
    with open(CLI_GLOBALS.CONFIG, 'r') as config_fp:
        config = json.load(config_fp)
    config[field] = value
    with open(CLI_GLOBALS.CONFIG, 'w') as config_fp:
        json.dump(config, config_fp)

def get_config_value(field):
    __maybe_init_config()
    with open(CLI_GLOBALS.CONFIG, 'r') as config_fp:
        config = json.load(config_fp)
    return config.get(field)

def list_config():
    __maybe_init_config()
    with open(CLI_GLOBALS.CONFIG, 'r') as config_fp:
        config = json.load(config_fp)
    return config

def put_config_value(field, value):
   __store_config(field, value)

def store_username(username):
    __store_config('username', username)

def store_password(password):
    __store_config('password', password)

def set_store_password(boolean):
    __store_config('store_password', boolean)

