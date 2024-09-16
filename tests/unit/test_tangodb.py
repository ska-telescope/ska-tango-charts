def test_tango_database_is_present(mysql_cursor):
    mysql_cursor.execute("SHOW DATABASES")

    database_names = [database_name[0] for database_name in mysql_cursor]
    assert "tango" in database_names


def test_tango_database_tables(mysql_cursor):
    mysql_cursor.execute("SHOW TABLES")

    expected_tables = (
        "access_address",
        "access_device",
        "attribute_alias",
        "attribute_class",
        "class_attribute_history_id",
        "class_history_id",
        "class_pipe_history_id",
        "device",
        "device_attribute_history_id",
        "device_history_id",
        "device_pipe_history_id",
        "event",
        "object_history_id",
        "property",
        "property_attribute_class",
        "property_attribute_class_hist",
        "property_attribute_device",
        "property_attribute_device_hist",
        "property_class",
        "property_class_hist",
        "property_device",
        "property_device_hist",
        "property_hist",
        "property_pipe_class",
        "property_pipe_class_hist",
        "property_pipe_device",
        "property_pipe_device_hist",
        "server",
    )
    actual_tables = [table_name[0] for table_name in mysql_cursor]
    assert actual_tables == list(expected_tables)


def test_databaseds_device_is_registered_in_the_database(mysql_cursor):
    mysql_cursor.execute("SELECT name FROM device")

    actual_devices = [device_name[0] for device_name in mysql_cursor]
    assert "sys/database/2" in actual_devices
