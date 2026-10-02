# -*- coding: utf-8 -*-
"""
    MoinMoin - tests of the refresh action's input validation

    @license: GNU GPL, see COPYING for details.
"""
import pytest

from MoinMoin.action import valid_refresh_key


@pytest.mark.parametrize("key", ['text_html', 'pagelinks', 'text_html.v2', 'a-b'])
def test_valid_key(key):
    assert valid_refresh_key(key)


@pytest.mark.parametrize("key", ['', '.', '..', '.hidden', 'a/b', 'a\\b', '../x',
                                 '/abs', 'C:x', 'a\x00b', 'a\n'])
def test_invalid_key(key):
    assert not valid_refresh_key(key)
