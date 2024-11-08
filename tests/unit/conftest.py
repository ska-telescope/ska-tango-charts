import os
import logging
import pytest
import yaml
import mysql.connector

from tango import DeviceProxy
from collections import namedtuple

## shared fixtures
from resources.test_support.fixtures import run_context

"""
Taken from https://gitlab.com/ska-telescope/skampi/-/blob/21e00f36a5fa797ad816ec8c40954f6a3a70b040/post-deployment/tests/conftest.py

RunContext is a metadata object to access values from the environment, 
i.e. data that is injected in by the Makefile. Useful if tests need to 
be aware of the k8s context they are running in, such as the HELM_RELEASE.

This will allow tests to resolve hostnames and other dynamic properties.

Example:

def test_something(run_context):
    HOSTNAME = 'some-pod-{}'.format(run_context.HELM_RELEASE)

"""

FILE_PATH = os.path.abspath("tests/tango_values.yaml")


@pytest.fixture
def get_values_file():
    values_list = None
    try:
        with open(FILE_PATH) as file:
            values_list = yaml.load(file, Loader=yaml.FullLoader)
    except Exception as e:
        pytest.raises(e)
    return values_list


@pytest.fixture
def get_db_config(get_values_file):
    mysql_config = dict()
    try:
        operator = os.getenv("SKA_TANGO_OPERATOR", "true")
        if operator.lower() in ["true"]:
            mysql_config["host"] = "databaseds-tangodb-tango-databaseds"
        else:
            mysql_config["host"] = "ska-tango-base-" + get_values_file["tangodb"]["component"]
        mysql_config["database"] = get_values_file["tangodb"]["db"]["db"]
        mysql_config["user"] = get_values_file["tangodb"]["db"]["user"]
        mysql_config["password"] = get_values_file["tangodb"]["db"]["password"]
    except Exception as e:
        pytest.raises(e)
    return mysql_config


@pytest.fixture
def mysql_cursor(get_db_config):
    mysql_cnx = None
    try:
        mysql_cnx = mysql.connector.connect(**get_db_config)
    except mysql.connector.Error as err:
        logging.error(err)
        pytest.raises(Exception("Database connection Error"))

    cursor = mysql_cnx.cursor()
    yield cursor
    cursor.close()
    mysql_cnx.close()
