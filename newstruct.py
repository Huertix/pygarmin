#!/usr/bin/env python
"""
   newstruct

   Very quickly hacked layer over the struct module to handle
   null-terminated strings.

   In the format string, an "s" is interpreted as a null-terminated
   string, rather than a string of length 1.

   (c) 2000 James A. H. Skillen <J.A.H.Skillen@warwick.ac.uk>
   
"""

import string
_string = string
del string
import struct
error = struct.error
import re

START = re.compile("^[ ]*[@<>!]")
TOKEN = re.compile("[ ]*([0-9]*)([xcbBhHiIlLfdspP])")

def pack(fmt, *args):
    endian, tokens = _parse(fmt)
    fmt = [ endian ]
    args = list(args)
    for i in range(len(tokens)):
        if tokens[i][1] == "s" and tokens[i][0] == "":
            args[i] = args[i] + "\000"
            tokens[i][0] = str(len(args[i]))
        fmt.append(_string.join(tokens[i], ''))
    return apply(struct.pack, [ _string.join(fmt) ] + args)

def _parse(fmt):
    if START.match(fmt) is not None:
        endian = fmt[0]
        fmt = fmt[1:]
    else:
        endian = "@"
    tokens = []
    while fmt != "":
        m = TOKEN.match(fmt)
        if m is None:
            raise error("bad char in struct format")
        tokens.append(list(m.groups()))
        fmt = fmt[m.end():]
    return (endian, tokens)

def unpack(fmt, string):
    endian, tokens = _parse(fmt)
    unpacked = []
    buffer = [ endian ]
    for i in range(len(tokens)):
        if tokens[i][1] == "s" and tokens[i][0] == "":
            if len(buffer) > 1:
                buffer, string, unpacked = _flush(buffer, string, unpacked)
                buffer.append(endian)
            index = _string.find(string, "\000")
            unpacked.append(string[:index])
            string = string[index+1:]
        else:
            buffer.append(_string.join(tokens[i], ""))
    if len(buffer) > 1:
        buffer, string, unpacked = _flush(buffer, string, unpacked)
    return tuple(unpacked)

def _flush(buffer, string, unpacked):
    fmt = _string.join(buffer)
    size = struct.calcsize(fmt)

    unpacked = unpacked + list(struct.unpack(fmt, string[:size]))
    string = string[size:]
    del buffer[:]
    return (buffer, string, unpacked)

def calcsize(fmt):
    endian, tokens = _parse(fmt)
    for num, type in tokens:
        if type == "s" and num == "":
            return None  # FIXME hehe - we don't know the length...
    return struct.calcsize(fmt)