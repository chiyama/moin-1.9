#########################################################
# md5crypt.py
#
# 0423.2000 by michal wallace http://www.sabren.com/
# based on perl's Crypt::PasswdMD5 by Luis Munoz (lem@cantv.net)
# based on /usr/src/libcrypt/crypt.c from FreeBSD 2.2.5-RELEASE
#
# MANY THANKS TO
#
#  Carey Evans - http://home.clear.net.nz/pages/c.evans/
#  Dennis Marti - http://users.starpower.net/marti1/
#
#  For the patches that got this thing working!
#
#########################################################
"""md5crypt.py - Provides interoperable MD5-based crypt() function

SYNOPSIS

        import md5crypt.py

        cryptedpassword = md5crypt.md5crypt(password, salt);

DESCRIPTION

unix_md5_crypt() provides a crypt()-compatible interface to the
rather new MD5-based crypt() function found in modern operating systems.
It's based on the implementation found on FreeBSD 2.2.[56]-RELEASE and
contains the following license in it:

 "THE BEER-WARE LICENSE" (Revision 42):
 <phk@login.dknet.dk> wrote this file.  As long as you retain this notice you
 can do whatever you want with this stuff. If we meet some day, and you think
 this stuff is worth it, you can buy me a beer in return.   Poul-Henning Kamp

apache_md5_crypt() provides a function compatible with Apache's
.htpasswd files. This was contributed by Bryan Hart <bryan@eai.com>.

"""

import hashlib

MAGIC = b'$1$'
ITOA64 = b"./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def _to_bytes(s):
    """Convert string to bytes if needed."""
    if isinstance(s, str):
        return s.encode('utf-8')
    return s


def to64(v, n):
    ret = b''
    while (n - 1 >= 0):
        n = n - 1
        ret = ret + bytes([ITOA64[v & 0x3f]])
        v = v >> 6
    return ret


def apache_md5_crypt(pw, salt):
    # change the Magic string to match the one used by Apache
    return unix_md5_crypt(pw, salt, b'$apr1$')


def unix_md5_crypt(pw, salt, magic=None):
    pw = _to_bytes(pw)
    salt = _to_bytes(salt)

    if magic is None:
        magic = MAGIC

    # Take care of the magic string if present
    if salt[:len(magic)] == magic:
        salt = salt[len(magic):]

    # salt can have up to 8 characters:
    salt = salt.split(b'$', 1)[0]
    salt = salt[:8]

    ctx = pw + magic + salt

    md5 = hashlib.md5()
    md5.update(pw + salt + pw)
    final = md5.digest()

    for pl in range(len(pw), 0, -16):
        if pl > 16:
            ctx = ctx + final[:16]
        else:
            ctx = ctx + final[:pl]

    # Now the 'weird' xform (??)

    i = len(pw)
    while i:
        if i & 1:
            ctx = ctx + b'\x00'
        else:
            ctx = ctx + pw[0:1]
        i = i >> 1

    md5 = hashlib.md5()
    md5.update(ctx)
    final = md5.digest()

    # The following is supposed to make
    # things run slower.

    for i in range(1000):
        ctx1 = b''
        if i & 1:
            ctx1 = ctx1 + pw
        else:
            ctx1 = ctx1 + final[:16]

        if i % 3:
            ctx1 = ctx1 + salt

        if i % 7:
            ctx1 = ctx1 + pw

        if i & 1:
            ctx1 = ctx1 + final[:16]
        else:
            ctx1 = ctx1 + pw

        md5 = hashlib.md5()
        md5.update(ctx1)
        final = md5.digest()

    # Final xform

    passwd = b''

    passwd = passwd + to64((final[0] << 16)
                           |(final[6] << 8)
                           |(final[12]), 4)

    passwd = passwd + to64((final[1] << 16)
                           |(final[7] << 8)
                           |(final[13]), 4)

    passwd = passwd + to64((final[2] << 16)
                           |(final[8] << 8)
                           |(final[14]), 4)

    passwd = passwd + to64((final[3] << 16)
                           |(final[9] << 8)
                           |(final[15]), 4)

    passwd = passwd + to64((final[4] << 16)
                           |(final[10] << 8)
                           |(final[5]), 4)

    passwd = passwd + to64(final[11], 2)

    return (magic + salt + b'$' + passwd).decode('ascii')


## assign a wrapper function:
md5crypt = unix_md5_crypt

if __name__ == "__main__":
    print(unix_md5_crypt("cat", "hat"))
