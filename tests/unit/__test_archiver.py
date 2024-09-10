# coding=utf-8
"""features/archiver.feature feature tests."""

import tango
from tango import DevFailed, DeviceProxy
from time import sleep
import pytest
import logging
from pytest_bdd import given, scenario, then, when, parsers

pytest.device_proxies = []


@scenario('archiver.feature', 'Check archiving')
def test_archiver():
    """Test archiver."""


@given(parsers.parse('a Configuration Manager called {cm_device_name} and an Event Subscriber called {'
                     'es_device_name}'))
def device_proxy(run_context, cm_device_name, es_device_name):
    """a Configuration Manager called archiving/hdbpp/confmanager01 and
    an Event Subscriber called archiving/hdbpp/eventsubscriber01."""
    pytest.conf_manager_device = tango.DeviceProxy(cm_device_name)
    pytest.event_subscriber_device = tango.DeviceProxy(es_device_name)


@pytest.fixture
@when(parsers.parse("I request to archive the attribute {attribute_name}"))
def archive_attribute(device_proxy, attribute_name):
    """Attribute is set to sys/tg_test/1/double_scalar."""
    conf_manager_proxy = pytest.conf_manager_device

    evt_subscriber_device_proxy = pytest.event_subscriber_device

    conf_manager_proxy.set_timeout_millis(5000)
    evt_subscriber_device_proxy.set_timeout_millis(5000)
    conf_manager_proxy.write_attribute("SetAttributeName", attribute_name)
    conf_manager_proxy.write_attribute("SetArchiver", evt_subscriber_device_proxy.name())
    conf_manager_proxy.write_attribute("SetStrategy", "ALWAYS")
    conf_manager_proxy.write_attribute("SetPollingPeriod", 1000)
    conf_manager_proxy.write_attribute("SetPeriodEvent", 3000)

    try:
        conf_manager_proxy.command_inout("AttributeAdd")
    except DevFailed as df:
        if not str(df.args[0].reason) == 'Already archived':    
            logging.info("DevFailed exception: " + str(df.args[0].reason))

    evt_subscriber_device_proxy.Start()
    return attribute_name


@then(parsers.parse("after {time_interval} milliseconds the Archiving is Started"))
def check_archiving(device_proxy, archive_attribute):
    """The time interval is 1 second."""
    attribute = archive_attribute
    max_retries = 10
    sleep_time = 1
    for x in range(0, max_retries):
        try:
            # Check status of Attribute Archiving in Configuration Manager
            result_config_manager = pytest.conf_manager_device.command_inout("AttributeStatus", attribute)
            # Check status of Attribute Archiving in Event Subscriber
            result_evt_subscriber = pytest.event_subscriber_device.command_inout("AttributeStatus", attribute)
            assert "Archiving          : Started" in result_config_manager
            assert "Archiving          : Started" in result_evt_subscriber
        except DevFailed as df:
            if x == (max_retries - 1):
                raise df
            logging.info(
                "DevFailed exception: " + str(df.args[0].reason) + ". Sleeping for " + str(sleep_time) + "ss")
            sleep(sleep_time)
