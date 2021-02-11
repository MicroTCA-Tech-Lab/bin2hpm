import argparse
import os
import sys
import struct

from bin2hpm import hpm, rle, __version__

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
    parser.add_argument('-o', '--outfile',
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
    parser.add_argument('-s', '--description',
                        type=str,
                        help='Additional description string (max. 21 chars)'
    )
    args = parser.parse_args()

    components = 1 << args.component
    v_maj = args.file_version[0]
    v_min = args.file_version[1]
    v_aux = swap32(args.auxillary)

    header = hpm.upg_image_hdr({
        'device_id': args.device,
        'manufacturer_id': args.manufacturer,
        'product_id': args.product,
        'time': 12345678,
        'components': components,
        'version_major': v_maj,
        'version_minor': v_min,
        'version_aux': v_aux
    })

    prepare = hpm.upg_action_hdr(components, hpm.UpgradeActionType.Prepare)

    with open(args.srcfile, 'rb') as f:
        img_data = f.read()

    if args.compress:
        enc_data = rle.encode(img_data)
        vfy_data = rle.decode(enc_data)
        if vfy_data != img_data:
            print(f'RLE compression verify mismatch', file=sys.stderr)
            sys.exit(-1)

        img_comp_hdr = b'COMPRESSED\x00'
        img_comp_hdr += int.to_bytes(len(img_data), length=4, byteorder='big')
        img_data = img_comp_hdr + enc_data

    update = hpm.upg_action_img(
        components,
        v_maj,
        v_min,
        v_aux,
        args.description or os.path.basename(args.srcfile)[:20],
        img_data
    )

    outfile = args.outfile
    if not outfile:
        outfile = os.path.splitext(args.sourcefile)[0] + '.hpm'

    hpm_file = header + prepare + update
    hpm_file += hpm.upg_img_hash(hpm_file)

    with open(outfile, 'wb') as f:
        f.write(hpm_file)
