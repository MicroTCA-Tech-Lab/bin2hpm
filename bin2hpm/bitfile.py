"""
SPDX-License-Identifier: BSD-3-Clause
Copyright (c) 2021 Deutsches Elektronen-Synchrotron DESY.
See LICENSE.txt for license details.
"""

import sys

class BitfileReader():
    def __init__(self, input):
        self.inp = input
    
    def read_n(self, n):
        val, self.inp = self.inp[:n], self.inp[n:]
        return val

    def read_int(self, n):
        result, self.inp = \
            int.from_bytes(self.inp[0:n], byteorder='big'), self.inp[n:]
        return result

    def read_u8(self):
        return self.read_int(1)

    def read_u16(self):
        return self.read_int(2)

    def read_u32(self):
        return self.read_int(4)

    def read_str(self):
        n = self.read_u16()
        return self.read_n(n)

def check_info(bs, section_expected, title):
    section_name = bs.read_u8()
    if section_name != ord(section_expected):
        raise ValueError(f'Bitstream section {section_expected} missing')

    section_info = bs.read_str()
    section_info = section_info.decode('utf-8')
    print(f'{title}: {section_info}')

def parse_bitfile(inp):
    print('Parsing bitfile...')
    bs = BitfileReader(inp)
    prologue = bs.read_str()
    one = bs.read_u16()
    if len(prologue) != 9 or one != 1:
        raise ValueError('Bitstream header invalid')

    check_info(bs, 'a', ' Design info')
    check_info(bs, 'b', '   Part name')
    check_info(bs, 'c', '   File date')
    check_info(bs, 'd', '        time')

    section_e = bs.read_u8()
    if section_e != ord('e'):
        raise ValueError('Bitstream section e missing')

    payload_size = bs.read_u32()
    print(f'  Image size: 0x{payload_size:08x} ({int(payload_size/1024)}KiB)\n')

    return bs.read_n(payload_size)
