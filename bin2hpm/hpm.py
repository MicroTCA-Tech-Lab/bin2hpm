"""
SPDX-License-Identifier: BSD-3-Clause
Copyright (c) 2021 Deutsches Elektronen-Synchrotron DESY.
See LICENSE.txt for license details.
"""

from datetime import datetime
import sys
from enum import Enum
import hashlib 
  
class UpgradeActionType(Enum):
    Backup = 0
    Prepare = 1
    Upload = 2

# name - default value - size

UPG_IMG_HEADER = (
    ( 'signature', 'PICMGFWU', 8 ),
    ( 'format_version', 0, 1 ),
    ( 'device_id', 0, 1 ),
    ( 'manufacturer_id', 0, 3),
    ( 'product_id', 0, 2 ),
    ( 'time', int(datetime.now().timestamp()), 4 ),
    ( 'img_caps', 0, 1 ),
    ( 'components', 0, 1 ),
    ( 'selftest_to', 0, 1 ),
    ( 'rollback_to', 0, 1 ),
    ( 'inaccess_to', 2, 1 ),
    ( 'earliest_compat_rev', 0, 2 ),
    ( 'version_major', 0, 1 ),
    ( 'version_minor', 0, 1 ),
    ( 'version_aux', 0, 4 ),
    ( 'oem_data_len', 0, 2 ),
)

UPG_ACTION_HEADER = (
    ( 'action_type', 0, 1 ),
    ( 'components', 0, 1 ),
)

UPG_ACTION_IMG_INFO = (
    ( 'version_major', 0, 1 ),
    ( 'version_minor', 0, 1 ),
    ( 'version_aux', 0, 4 ),
    ( 'desc_str', '', 21 ),
    ( 'img_length', 0, 4 ),
)

def fixed_str(s, n):
    s = s[:n]
    s += '\x00' * (n - len(s))
    return s.encode('utf-8')

def zero_cksum(input):
    return int.to_bytes((0x100 - sum(input)) & 0xff, length=1, byteorder='little')

def to_bcd(value):
    return int(str(value), 16)

def encode_generic(table, values):
    result = b''
    for name, default, size in table:
        val = values[name] if name in values else default
        try:
            if isinstance(val, str):
                result += fixed_str(val, size)
            elif isinstance(val, bytes):
                result += val[:size]
            else:
                if name == 'version_minor':
                    val = to_bcd(val)
                elif isinstance(val, Enum):
                    val = val.value
                result += int.to_bytes(val, length=size, byteorder='little')
                
        except OverflowError:
            print(f'{name} value of {val} doesn\'t fit in {size} bytes', file=sys.stderr)
            sys.exit(-1)
        except TypeError:
            print(f'Couldn\'t encode {name} value of {val}', file=sys.stderr)
            sys.exit(-1)
    return result

def upg_image_hdr(**kwargs):
    result = encode_generic(UPG_IMG_HEADER, kwargs)
    result += zero_cksum(result)
    return result

def upg_action_hdr(**kwargs):
    result = encode_generic(UPG_ACTION_HEADER, kwargs)
    result += zero_cksum(result)
    return result

def upg_action_img(img_data, **kwargs):
    result = upg_action_hdr(**{
        'action_type': UpgradeActionType.Upload,
        **kwargs
    })
    result += encode_generic(UPG_ACTION_IMG_INFO, {
        'img_length': len(img_data),
        **kwargs
    })
    result += img_data
    return result

def upg_img_hash(hpm_img):
    return hashlib.md5(hpm_img).digest()
