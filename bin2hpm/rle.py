"""
SPDX-License-Identifier: BSD-3-Clause
Copyright (c) 2021 Deutsches Elektronen-Synchrotron DESY.
See LICENSE.txt for license details.
"""

RLE_MAX_BLKSIZE=128

def to_byte(b):
    return bytes([b])

def encode(data):
    def check_block(data):
        n = 1
        while len(data) > n and data[n] == data[0] and n < RLE_MAX_BLKSIZE:
            n += 1
        return n, data[0]

    print('Performing RLE compression ...')
    orig_len = len(data)

    result = b''
    while len(data):
        tmp = b''
        while len(data) and len(tmp) < RLE_MAX_BLKSIZE:
            n, val = check_block(data)
            if n > 2:
                data = data[n:]
                break
            elif n == 2:
                n = 1
            data = data[n:]
            tmp += to_byte(val)
        if len(tmp):
            result += to_byte(len(tmp) - 1)
            result += tmp
        if n < 2:
            continue
        result += to_byte((n - 2) | 0x80)
        result += to_byte(val)
    
    comp_len = len(result)
    comp_ratio = 100 * comp_len / orig_len

    print(f'Compressed size {comp_len} bytes, ratio {comp_ratio:.1f}%')
    return result

def decode(data):
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
