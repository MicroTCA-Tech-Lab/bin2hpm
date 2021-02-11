"""
SPDX-License-Identifier: BSD-3-Clause
Copyright (c) 2021 Deutsches Elektronen-Synchrotron DESY.
See LICENSE.txt for license details.
"""

import sys

def bs_read_n(inp, n):
    result, inp = \
        int.from_bytes(inp[0:n], byteorder='big'), inp[n:]
    return result, inp

def bs_read_u8(inp):
    return bs_read_n(inp, 1)

def bs_read_u16(inp):
    return bs_read_n(inp, 2)

def bs_read_u32(inp):
    return bs_read_n(inp, 4)

def bs_read_str(inp):
    n, inp = bs_read_u16(inp)
    val, inp = inp[:n], inp[n:]
    return val, inp

def check_info(inp, section_expected, title):
    section_name, inp = bs_read_u8(inp)
    if section_name != ord(section_expected):
        raise ValueError(f'Bitstream section {section_expected} missing')

    section_info, inp = bs_read_str(inp)
    section_info = section_info.decode('utf-8')
    print(f'{title}: {section_info}')
    return inp

def parse_bitfile(inp):
    print('Parsing bitfile...')
    prologue, inp = bs_read_str(inp)
    one, inp = bs_read_u16(inp)
    if len(prologue) != 9 or one != 1:
        raise ValueError('Bitstream header invalid')

    inp = check_info(inp, 'a', ' Design info')
    inp = check_info(inp, 'b', '   Part name')
    inp = check_info(inp, 'c', '   File date')
    inp = check_info(inp, 'd', '        time')

    section_e, inp = bs_read_u8(inp)
    if section_e != ord('e'):
        raise ValueError('Bitstream section e missing')

    payload_size, inp = bs_read_u32(inp)
    print(f'  Image size: 0x{payload_size:08x} ({int(payload_size/1024)}KiB)\n')

    return inp[:payload_size]
