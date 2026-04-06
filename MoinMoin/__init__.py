# -*- coding: utf-8 -*-
"""
MoinMoin - a wiki engine in Python

@copyright: 2000-2006 by Juergen Hermann <jh@web.de>,
            2002-2020 MoinMoin:ThomasWaldmann
@license: GNU GPL, see COPYING for details.
"""

import os, sys

# Make bundled packages in MoinMoin/support/ importable
_support_path = os.path.join(os.path.dirname(__file__), 'support')
if _support_path not in sys.path:
    sys.path.insert(0, _support_path)



