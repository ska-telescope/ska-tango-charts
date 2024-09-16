import logging
import pytest
from pytest_bdd import scenario, given, when, then, scenarios, parsers
import yaml
import mysql.connector
from mysql.connector import errorcode

pytest.namespace = ""

@given(parsers.parse("Tango env {values_file}"))
def getValuesFile(values_file):

    try:
        with open(values_file) as file:
            pytest.values_list = yaml.load(file, Loader=yaml.FullLoader)
    except Exception as e:
        pytest.raises(e)
        


@when(parsers.parse("I extract the DB config in the {device_name}"))
def getDBConfig(device_name):
    try:
        pytest.dbHost = 'ska-tango-base-' + pytest.values_list['tangodb']['component']
        pytest.dbName = pytest.values_list['tangodb']['db']['db']
        pytest.dbUser = pytest.values_list['tangodb']['db']['user']
        pytest.dbPassword = pytest.values_list['tangodb']['db']['password']
    except Exception as e:
        pytest.raises(e)
    

@then(parsers.parse("I check the tango database connection"))
def checkDB():
    try:
        cnx = mysql.connector.connect(
            user=pytest.dbUser,
            password=pytest.dbPassword,
            host=pytest.dbHost,
            database=pytest.dbName
        )

    except mysql.connector.Error as err:
            logging.error(err)
            pytest.raises(Exception("Database connection Error"))
    else:
        cnx.close()

scenarios('../features/tango-db.feature')
