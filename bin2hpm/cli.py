import argparse
import sys
import struct

from bin2hpm import hpm, __version__

def swap32(i):
    return struct.unpack("<I", struct.pack(">I", i))[0]

def main():
    parser = argparse.ArgumentParser(
        description='HPM.1 update file converter'
    )
    parser.add_argument('srcfile',
                        type=str,
                        help='Source file'
    )
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' + __version__
    )
    parser.add_argument('-o', '--output',
                        type=str,
                        help='output file (derived from input file if not set)'
    )
    parser.add_argument('-b', '--bitfile',
                        action='store_true',
                        help='bit file mode'
    )
    parser.add_argument('-v', '--file-version',
                        default='0.0',
                        type=lambda x: [int(v, 10) for v in x.split('.')],
                        help='file version information (format major.minor, e.g. 1.2)'
    )
    parser.add_argument('-a', '--auxillary',
                        type=lambda x: int(x, 16),
                        default='00000000',
                        help='additional metadata, hex format, 4 bytes'
    )
    parser.add_argument('-c', '--component',
                        type=int,
                        default=1,
                        help='HPM component ID (default 1)'
    )
    parser.add_argument('-d', '--device',
                        type=lambda x: int(x, 16),
                        default='0',
                        help='HPM device ID (hex, default 0)'
    )
    parser.add_argument('-m', '--manufacturer',
                        type=lambda x: int(x, 16),
                        default='000000',
                        help='IANA manufacturer ID (hex, 6 bytes max)'
    )
    parser.add_argument('-p', '--product',
                        type=lambda x: int(x, 16),
                        default='0000',
                        help='IANA product ID (hex, 4 bytes max)'
    )
    parser.add_argument('-r', '--compress',
                        action='store_true',
                        help='Enable RLE compression (requires DESY MMC)'
    )
    args = parser.parse_args()

    header = hpm.upg_img_hdr({
        'device_id': args.device,
        'manufacturer_id': args.manufacturer,
        'product_id': args.product,
        'time': 12345678,
        'components': 1 << args.component,
        'version_major': args.file_version[0],
        'version_minor': args.file_version[1],
        'version_aux':  swap32(args.auxillary)
    })
    sys.stdout.buffer.write(header)
