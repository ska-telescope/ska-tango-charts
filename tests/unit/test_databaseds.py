import os
import mock
import pytest
import tango


@pytest.fixture
def test_device_info():
    device_info = tango.DbDevInfo()
    device_info.name = "test/device/1"
    device_info._class = "TestDevice"
    device_info.server = "TestDevice/test"
    return device_info


@pytest.fixture
def tango_databaseds(test_device_info, mysql_cursor):
    db = tango.Database()
    db.add_server(test_device_info.server, test_device_info, with_dserver=True)
    yield db
    clean_up_database(mysql_cursor)


def clean_up_database(mysql_cursor):
    unrgister_device_query = "DELETE FROM device WHERE name='test/device/1';"
    unrgister_property_device_query = (
        "DELETE  FROM  property_device where device = 'test/device/1';"
    )
    unrgister_property_class_query = "DELETE  FROM  property_class where class='TestDevice';"
    unrgister_property_attribute_device_query = (
        "DELETE  FROM  property_attribute_device where device='test/device/1';"
    )

    device_info = [
        unrgister_device_query,
        unrgister_property_device_query,
        unrgister_property_class_query,
        unrgister_property_attribute_device_query,
    ]

    for query in device_info:
        mysql_cursor.execute(query)


def test_databaseds_connection():
    db = tango.Database()
    assert db is not None


@mock.patch.dict(os.environ, {"TANGO_HOST": "local:10123"}, clear=True)
def test_databaseds_connection_failure_when_tango_host_incorrect():
    with pytest.raises(tango.DevFailed) as error:
        db = tango.Database()
        assert error.args[1].desc == "Failed to connect to database on host local with port 10123"


def test_device_registration(tango_databaseds, test_device_info, mysql_cursor):
    mysql_cursor.execute("SELECT name,class,server FROM device WHERE name='test/device/1';")
    database_info = [info for info in mysql_cursor]
    assert ("test/device/1", "TestDevice", "TestDevice/test") in database_info


def test_device_property_registration(tango_databaseds, test_device_info, mysql_cursor):
    tango_databaseds.put_device_property(
        test_device_info.name, {"device_test_property": ["device_test_property_value"]}
    )

    mysql_cursor.execute("SELECT name,device FROM property_device where device='test/device/1'")
    database_info = [info for info in mysql_cursor]
    assert ("device_test_property", "test/device/1") in database_info


def test_class_property_registration(tango_databaseds, test_device_info, mysql_cursor):
    tango_databaseds.put_class_property(
        test_device_info._class, {"class_test_property": ["class_test_property_value"]}
    )

    mysql_cursor.execute("SELECT name,value FROM property_class where class='TestDevice'")
    database_info = [info for info in mysql_cursor]
    assert ("class_test_property", "class_test_property_value") in database_info


def test_device_attribute_property_registration(tango_databaseds, test_device_info, mysql_cursor):
    tango_databaseds.put_device_attribute_property(
        test_device_info.name,
        {"test_attribute": {"attribute_test_property": ["attribute_test_property_value"]}},
    )

    mysql_cursor.execute(
        "SELECT attribute,name,value FROM property_attribute_device where device='test/device/1'"
    )
    database_info = [info for info in mysql_cursor]
    assert (
        "test_attribute",
        "attribute_test_property",
        "attribute_test_property_value",
    ) in database_info


# Unhappy paths
