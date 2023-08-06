# vim: set fileencoding=utf-8:


import logging
import json
import os

import appdirs


# --- constants ---

API_NAME = 'coronado' # lower case by design; used also as a namespace
CONFIGURATION_PATH = appdirs.user_config_dir(API_NAME)
CONFIGURATION_FILE_NAME = 'config.json'
CONFIGURATION_FILE_PATH = os.path.join(CONFIGURATION_PATH, CONFIGURATION_FILE_NAME)
DEFAULT_LOG_FILE_NAME = 'coronado.log'
LOG_PATH = appdirs.user_log_dir(API_NAME)
LOG_FILE_NAME = 'coronado.log'
LOG_FILE_PATH = os.path.join(LOG_PATH, LOG_FILE_NAME)


# +++ globals +++


_config = None


# --- functions ---

def _logInit(config, fileName = None):
    # fileName used only for unit tests
    os.makedirs(LOG_PATH, exist_ok = True)
    logLevel = getattr(logging, config.get('loglevel', 'INFO').upper(), logging.INFO)
    logFileName = fileName if fileName else LOG_FILE_PATH
    logging.basicConfig(filename = logFileName,
                        filemode = 'w',
                        format = '%(asctime)s %(name)s %(levelname)s %(message)s',
                        level = logLevel)


def loadConfig(testConfig: dict = None) -> dict:
    """
    Load the configuration from the system-dependent config path for the current
    user.  The configuration is stored in A JSON file at CONFIGURATION_FILE_PATH.

    Arguments
    ---------
        `testConfig`
    A dictionary, test configuration used for unit testing.  Ignore under normal
    use or contact the developers if needed.

    Return
    ------
    A dictionary of configuration parameters.
    """
    global _config

    if testConfig:
        _config = testConfig
    else:
        os.makedirs(CONFIGURATION_PATH, exist_ok = True)
        with open(CONFIGURATION_FILE_PATH, 'r') as inputStream:
            _config = json.load(inputStream)

    _logInit(_config)

    return _config


def emptyConfig() -> dict:
    """
    Configuration generator builds an empty configuration to fill in the details.

    **configuration**

    ```python
    {
        "clientID": "",
        "clientName": "",
        "loglevel": "INFO",
        "secret": "",
        "serviceURL": "", # API service URL
        "token": "",
        "tokenURL": ""
    }
    ```


    Return
    ------
    A dictionary of configuration parameters, all the values are empty.
    """
    return { "clientID": "",
             "clientName": "",
             "loglevel": "INFO",
             "secret": "",
             "serviceURL": "", # API service URL
             "token": "",
             "tokenURL": ""}

