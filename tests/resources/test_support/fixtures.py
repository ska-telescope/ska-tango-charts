import logging
import functools, os
from sys import exec_prefix
from collections import namedtuple

import pytest
from tango import DeviceProxy

LOGGER = logging.getLogger(__name__)

## pytest fixtures
ENV_VARS = [
    'HELM_RELEASE',
    'KUBE_NAMESPACE',
    'TANGO_HOST']
RunContext = namedtuple('RunContext', ENV_VARS)
@pytest.fixture(scope="session")
def run_context():
     # list of required environment vars
    values = list()
    
    for var in ENV_VARS:
        assert os.environ.get(var) # all ENV_VARS must have values set
        values.append(os.environ.get(var))
    return RunContext(*values)