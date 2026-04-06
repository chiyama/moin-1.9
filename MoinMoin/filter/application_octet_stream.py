# -*- coding: iso-8859-1 -*-
"""
    MoinMoin - binary file Filter

    Processes any binary file and extracts ASCII content from it.

    We ignore any file with a file extension on the blacklist, because
    we either can't handle it or it usually has no indexable content.

    Due to speed reasons, we only read the first maxread bytes from a file.

    For reducing the amount of trash, we only return words with
    length >= minwordlen.

    Depends on: nothing (pure python)

    @copyright: 2006 MoinMoin:ThomasWaldmann
    @license: GNU GPL, see COPYING for details.
"""

maxread = 10000
minwordlen = 4

blacklist = ('.iso', '.nrg', # CD/DVD images
             '.zip', '.rar', '.lzh', '.lha',
             '.tar', '.gz', '.tgz', '.bz2', '.tb2', '.z',
             '.exe', '.com', '.dll', '.cab', '.msi', '.bin', # windows
             '.rpm', '.deb', # linux
             '.hqx', '.dmg', '.sit', # mac
             '.jar', '.class', # java
            )

import os, string

# Build a translation table that replaces all non-alphanumeric characters with spaces.
# In Python 3, string.maketrans was removed; use str.maketrans and bytes.maketrans instead.
_alnum = (string.ascii_letters + string.digits).encode('ascii')
_allbytes = bytes(range(256))
_non_alnum = bytes(b for b in _allbytes if b not in _alnum)
trans_nontext = bytes.maketrans(_non_alnum, b' ' * len(_non_alnum))

def execute(indexobj, filename):
    fileext = os.path.splitext(filename)[1]
    if fileext.lower() in blacklist:
        return u''
    f = open(filename, "rb")
    data = f.read(maxread)
    f.close()
    data = data.translate(trans_nontext) # replace non-ascii by blanks
    data = data.split() # removes lots of blanks
    data = [s for s in data if len(s) >= minwordlen] # throw away too short stuff
    data = b' '.join(data)
    return data.decode('ascii')

