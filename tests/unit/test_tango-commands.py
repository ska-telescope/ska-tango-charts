# coding=utf-8
"""features/tango-cpp.feature feature tests."""
import tango
import logging
import numpy as np
import pytest
from tango import Database, DeviceProxy, CmdArgType as ArgType

from pytest_bdd import given, scenario, then, when, parsers, scenarios

scenarios('../features/tango-commands.feature')

@pytest.fixture
@given(parsers.parse('a device called {device_name}'), target_fixture="device_proxy")
def device_proxy(run_context, device_name):
    """a device called sys/tg_test/1."""
    return tango.DeviceProxy(device_name)


@pytest.fixture
@when(parsers.cfparse("I call the command {command_name:String}({parameter:String?})", extra_types=dict(String=str)), target_fixture="call_command")
def call_command(device_proxy,command_name, parameter):
    """I call the command State()."""
    # logging.info("Called command: {} with parameter {} for device {}".format(command_name, parameter, device_proxy.info()))
    if parameter is None:
        return device_proxy.command_inout(command_name)
    else:
        command_info = device_proxy.command_query(command_name)
        # {0: tango._tango.CmdArgType.DevVoid,
        #  1: tango._tango.CmdArgType.DevBoolean,*
        #  2: tango._tango.CmdArgType.DevShort,*
        #  3: tango._tango.CmdArgType.DevLong,*
        #  4: tango._tango.CmdArgType.DevFloat,*
        #  5: tango._tango.CmdArgType.DevDouble,*
        #  6: tango._tango.CmdArgType.DevUShort,*
        #  7: tango._tango.CmdArgType.DevULong,*
        #  8: tango._tango.CmdArgType.DevString,*
        #  9: tango._tango.CmdArgType.DevVarCharArray,
        #  10: tango._tango.CmdArgType.DevVarShortArray,
        #  11: tango._tango.CmdArgType.DevVarLongArray,
        #  12: tango._tango.CmdArgType.DevVarFloatArray,
        #  13: tango._tango.CmdArgType.DevVarDoubleArray,
        #  14: tango._tango.CmdArgType.DevVarUShortArray,
        #  15: tango._tango.CmdArgType.DevVarULongArray,
        #  16: tango._tango.CmdArgType.DevVarStringArray,
        #  17: tango._tango.CmdArgType.DevVarLongStringArray,
        #  18: tango._tango.CmdArgType.DevVarDoubleStringArray,
        #  19: tango._tango.CmdArgType.DevState,
        #  20: tango._tango.CmdArgType.ConstDevString,
        #  21: tango._tango.CmdArgType.DevVarBooleanArray,
        #  22: tango._tango.CmdArgType.DevUChar,
        #  23: tango._tango.CmdArgType.DevLong64,*
        #  24: tango._tango.CmdArgType.DevULong64,*
        #  25: tango._tango.CmdArgType.DevVarLong64Array,
        #  26: tango._tango.CmdArgType.DevVarULong64Array,
        #  27: None,*  # DevInt has been removed in cppTango 9.5.0
        #  28: tango._tango.CmdArgType.DevEncoded, *****????????
        #  29: tango._tango.CmdArgType.DevEnum, *****????????
        #  30: tango._tango.CmdArgType.DevPipeBlob, *****????????
        #  31: tango._tango.CmdArgType.DevVarStateArray}
        if(command_info.in_type == ArgType.DevShort or
        command_info.in_type == ArgType.DevLong or
        command_info.in_type == ArgType.DevUShort or
        command_info.in_type == ArgType.DevULong or
        command_info.in_type == ArgType.DevLong64 or
        command_info.in_type == ArgType.DevULong64):
            return device_proxy.command_inout(command_name, int(parameter))
        if(command_info.in_type == ArgType.DevFloat or 
        command_info.in_type == ArgType.DevDouble):
            return device_proxy.command_inout(command_name, float(parameter))
        if(command_info.in_type == ArgType.DevBoolean):
            return device_proxy.command_inout(command_name, bool(parameter))

        return device_proxy.command_inout(command_name, parameter)


@then(parsers.parse('the attribute {attribute_name} is {expected_value}'))
def check_attribute(device_proxy, attribute_name, expected_value):
    """the attribute State is RUNNING."""
    attr = device_proxy.read_attribute(attribute_name)
    # logging.info("Attribute: {}".format(attr))
    if attr.data_format == tango._tango.AttrDataFormat.SCALAR:
        assert str(attr.value) == expected_value
    elif attr.data_format == tango._tango.AttrDataFormat.SPECTRUM:
        assert type(attr.value) == np.ndarray

@then(parsers.parse("the result is {expected_result}"))
def check_command(device_proxy, call_command, expected_result):
  assert str(call_command) == expected_result
