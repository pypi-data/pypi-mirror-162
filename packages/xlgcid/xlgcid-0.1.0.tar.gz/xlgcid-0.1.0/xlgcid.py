# -*- coding: utf-8 -*-
#
# Copyright (c) 2022~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from typing import *
import hashlib
import os

def get_gcid_digest(fp, fp_size: int):
    '''
    Calc GCID from `fp`.
    '''

    # modified from https://binux.blog/2012/03/hash_algorithm_of_xunlei/

    h = hashlib.sha1()

    piece_size = 0x40000
    while fp_size / piece_size > 0x200 and piece_size < 0x200000:
        piece_size = piece_size << 1

    buf = bytearray(piece_size)  # Reusable buffer to reduce allocations.
    buf_view = memoryview(buf)
    while read_size := fp.readinto(buf):
        fp_size -= read_size
        if fp_size < 0:
            raise ValueError('visit unexpected data.')
        h.update(hashlib.sha1(buf_view[:read_size]).digest())

    if fp_size != 0:
        raise ValueError('stream end too early.')

    return h.digest()

def get_file_gcid_digest(path: str):
    '''
    Calc GCID from `path`.
    '''
    with open(path, 'rb') as fp:
        return get_gcid_digest(fp, os.path.getsize(path))

__all__ = [
    'get_gcid_digest',
    'get_file_gcid_digest'
]
