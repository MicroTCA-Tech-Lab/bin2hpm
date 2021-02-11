"""
SPDX-License-Identifier: BSD-3-Clause
Copyright (c) 2021 Deutsches Elektronen-Synchrotron DESY.
See LICENSE.txt for license details.
"""

from array import array

RLE_MAX_BLKSIZE=128

def encode(data):
    def check_block(data):
        n = 1
        while len(data) > n and data[n] == data[0] and n < RLE_MAX_BLKSIZE:
            n += 1
        return n, data[0]

    print('Performing RLE compression ...')
    orig_len = len(data)

    result = array('B')
    while len(data):
        tmp = array('B')
        while len(data) and len(tmp) < RLE_MAX_BLKSIZE:
            n, val = check_block(data)
            if n > 2:
                data = data[n:]
                break
            elif n == 2:
                n = 1
            data = data[n:]
            tmp.append(val)
        if len(tmp):
            result.append(len(tmp) - 1)
            result.extend(tmp)
        if n < 2:
            continue
        result.append((n - 2) | 0x80)
        result.append(val)
    
    comp_len = len(result)
    comp_ratio = 100 * comp_len / orig_len

    print(f'Compressed size {comp_len} bytes, ratio {comp_ratio:.1f}%')
    return bytes(result)

def decode(data):
    def to_byte(b):
        return b.to_bytes(1, 'little')

    result = b''
    while (len(data)):
        if data[0] & 0x80:
            result += to_byte(data[1]) * ((data[0] & 0x7f) + 2)
            data = data[2:]
        else:
            l = data[0] + 1
            result += data[1:l+1]
            data = data[l+1:]
    return result
