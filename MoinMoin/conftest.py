# -*- coding: utf-8 -*-
"""
MoinMoin Testing Framework
--------------------------

All test modules must be named test_modulename to be included in the
test suite. If you are testing a package, name the test module
test_package_module.

Tests that need the current request, for example to create a page
instance, can refer to self.request. It is injected into all test case
classes by the framework.

Tests that require a certain configuration, like section_numbers = 1, must
use a Config class to define the required configuration within the test class.

@copyright: 2005 MoinMoin:NirSoffer,
            2007 MoinMoin:AlexanderSchremmer,
            2008 MoinMoin:ThomasWaldmann
@license: GNU GPL, see COPYING for details.
"""

import atexit
import sys
from pathlib import Path

import pytest

rootdir = Path(__file__).parent
moindir = rootdir.parent
sys.path.insert(0, str(moindir))

from MoinMoin.web.request import TestRequest, Client
from MoinMoin.wsgiapp import Application, init
from MoinMoin._tests import maketestwiki, wikiconfig

coverage_modules = set()

try:
    """
    This code adds support for coverage.py (see
    http://nedbatchelder.com/code/modules/coverage.html).
    It prints a coverage report for the modules specified in all
    module globals (of the test modules) named "coverage_modules".
    """

    import coverage

    def report_coverage():
        coverage.stop()
        module_list = [sys.modules[mod] for mod in coverage_modules]
        module_list.sort()
        coverage.report(module_list)

    def pytest_addoption(parser):
        parser.addoption('--coverage', action='store_true', default=False,
                         help='Output information about code coverage (slow!)')

    def pytest_configure(config):
        if config.getoption('--coverage'):
            atexit.register(report_coverage)
            coverage.erase()
            coverage.start()

except ImportError:
    coverage = None


def init_test_request(given_config=None, static_state=[False]):
    if not static_state[0]:
        maketestwiki.run(True)
        static_state[0] = True
    request = TestRequest()
    request.given_config = given_config
    request = init(request)
    return request


def pytest_collection_modifyitems(session, config, items):
    """Collect coverage_modules from test modules."""
    if coverage is not None:
        for item in items:
            mod = item.module if hasattr(item, 'module') else None
            if mod is not None:
                coverage_modules.update(getattr(mod, 'coverage_modules', []))


def pytest_runtest_setup(item):
    """Inject request and client into test classes, mimicking old behavior."""
    cls = item.cls
    if cls is not None and not hasattr(cls, '_moin_setup_done'):
        if hasattr(cls, 'Config'):
            cls.request = init_test_request(given_config=cls.Config)
            cls.client = Client(Application(cls.Config))
        else:
            cls.request = init_test_request(given_config=wikiconfig.Config)
            cls.client = Client(Application(wikiconfig.Config))
        cls._moin_setup_done = True
