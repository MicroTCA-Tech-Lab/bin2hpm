###########################################################################
#      ____  _____________  __    __  __ _           _____ ___   _        #
#     / __ \/ ____/ ___/\ \/ /   |  \/  (_)__ _ _ __|_   _/ __| /_\  (R)  #
#    / / / / __/  \__ \  \  /    | |\/| | / _| '_/ _ \| || (__ / _ \      #
#   / /_/ / /___ ___/ /  / /     |_|  |_|_\__|_| \___/|_| \___/_/ \_\     #
#  /_____/_____//____/  /_/      T  E  C  H  N  O  L  O  G  Y   L A B     #
#                                                                         #
#          Copyright 2021 Deutsches Elektronen-Synchrotron DESY.          #
#                  SPDX-License-Identifier: BSD-3-Clause                  #
#                                                                         #
###########################################################################

from tqdm import tqdm

RLE_MAX_BLKSIZE = 128


def to_byte(b):
    return bytes([b])


def encode(data, quiet_mode=False):
    def check_block(data, k):
        n = 1
        while (len(data) - k) > n and data[k+n] == data[k] and n < RLE_MAX_BLKSIZE:
            n += 1
        return n, data[k]

    if not quiet_mode:
        print('Performing RLE compression ...')
    orig_len = len(data)

    result = b''
    with tqdm(total=orig_len, unit='B', unit_scale=True, leave=False) as pbar:
        k = 0
        last_k = k
        while k < len(data):
            tmp = b''
            while k < len(data) and len(tmp) < RLE_MAX_BLKSIZE:
                n, val = check_block(data, k)
                if n > 2:
                    k += n
                    break
                elif n == 2:
                    n = 1
                k += n
                tmp += to_byte(val)
            pbar.update(k - last_k)
            last_k = k

            if len(tmp):
                result += to_byte(len(tmp) - 1)
                result += tmp
            if n < 2:
                continue
            result += to_byte((n - 2) | 0x80)
            result += to_byte(val)

    comp_len = len(result)
    comp_ratio = 100 * comp_len / orig_len

    if not quiet_mode:
        print(f'Compressed size {comp_len} bytes, ratio {comp_ratio:.1f}%')
    return result


def decode(data):
    result = b''
    with tqdm(total=len(data), unit='B', unit_scale=True, leave=False) as pbar:
        k = 0
        last_k = k
        while k < len(data):
            if data[k] & 0x80:
                result += to_byte(data[k+1]) * ((data[k] & 0x7f) + 2)
                k += 2
            else:
                l = data[k] + 1
                result += data[k+1:k+l+1]
                k += l+1
            pbar.update(k - last_k)
            last_k = k

    return result
