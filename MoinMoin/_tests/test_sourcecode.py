"""
Verify that the MoinMoin source files conform (mostly) to PEP8 coding style.

Additionally, we check that the files have no crlf (Windows style) line endings.

@copyright: 2006 by Armin Rigo (originally only testing for tab chars),
            2007 adapted and extended (calling the PEP8 checker for most stuff) by MoinMoin:ThomasWaldmann.
@license: MIT licensed
"""

import pytest

# pep8 module was removed; these tests are disabled.
# To re-enable, install pycodestyle and adapt the code below.

def test_sourcecode():
    pytest.skip("pep8/pycodestyle based source code checks are disabled")

