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

import argparse
import os
import sys
import struct

from bin2hpm import hpm_conv, bitfile, __version__


def swap32(i):
    return struct.unpack("<I", struct.pack(">I", i))[0]


def main():
    parser = argparse.ArgumentParser(
        description='HPM.1 update file converter'
    )
    parser.add_argument('infile',
                        type=str,
                        help='Input file'
                        )
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' + __version__
                        )
    parser.add_argument('-o', '--outfile',
                        type=str,
                        help='output file (derived from input file if not set)'
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
    parser.add_argument('-q', '--quiet',
                        action='store_true',
                        help='Quiet mode'
                        )

    force_fmt = parser.add_mutually_exclusive_group(required=False)
    force_fmt.add_argument('-b', '--bitfile',
                           action='store_true',
                           help='Force bitfile mode'
                           )
    force_fmt.add_argument('-n', '--binfile',
                           action='store_true',
                           help='Force binfile mode'
                           )

    args = parser.parse_args()

    # Determine bit file mode
    if args.bitfile:
        bitmode = True
    elif args.binfile:
        bitmode = False
    else:
        bitmode = os.path.splitext(args.infile)[1].lower() == '.bit'

    # Set up arguments for HPM generator
    components = 1 << args.component
    v_maj = args.file_version[0]
    v_min = args.file_version[1]
    v_aux = swap32(args.auxillary)

    # Check input file existence
    if not os.path.isfile(args.infile):
        print(f'Input file {args.infile} not found', file=sys.stderr)
        sys.exit(-1)

    if not args.quiet:
        # Print general information
        print(f'bin2hpm v{__version__} (C) 2021 DESY\n')
        print(
            f'Input file {args.infile}, length {os.path.getsize(args.infile)} bytes\n')
        print(
            f'IANA Manuf., Product 0x{args.manufacturer:06x}, 0x{args.product:04x}')
        print(f'Component {args.component}, Device {args.device}')
        print(f'FW version {v_maj}.{v_min:02d} / 0x{args.auxillary:08x}\n')

    # Determine outfile name
    outfile = args.outfile
    if not outfile:
        outfile = os.path.splitext(args.infile)[0] + '.hpm'

    # Read input file
    with open(args.infile, 'rb') as f:
        img_data = f.read()

    # Parse bitfile if bitmode enabled
    if bitmode:
        img_data = bitfile.parse_bitfile(img_data, args.quiet)

    # Do the actual conversion
    result = hpm_conv.hpm_conv(
        img_data,
        args.compress,
        quiet_mode=args.quiet,
        device_id=args.device,
        manufacturer_id=args.manufacturer,
        product_id=args.product,
        components=components,
        version_major=v_maj,
        version_minor=v_min,
        version_aux=v_aux,
        desc_str=args.description or os.path.basename(args.infile)[:20]
    )
    # Write HPM file
    with open(outfile, 'wb') as f:
        f.write(result)

    if not args.quiet:
        print(f'Output file {outfile}, length {len(result)} bytes')
