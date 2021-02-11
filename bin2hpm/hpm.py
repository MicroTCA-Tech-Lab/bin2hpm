from datetime import datetime
import sys

# name - default value - size

UPG_IMG_HEADER = (
    ( 'signature', int.from_bytes(b'PICMGFWU', 'little'), 8 ),
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

def zero_cksum(input):
    return int.to_bytes((0x100 - sum(input)) & 0xff, length=1, byteorder='little')

def upg_img_hdr(values):
    result = b''
    for name, default, size in UPG_IMG_HEADER:
        val = values[name] if name in values else default
        try:
            result += int.to_bytes(val, length=size, byteorder='little')
        except OverflowError:
            print(f'HPM header error: {name} value of {val} doesn\'t fit in {size} bytes', file=sys.stderr)
            sys.exit(-1)
    
    result += zero_cksum(result)
    return result
