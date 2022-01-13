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

from bin2hpm import hpm, rle
import sys

# supported arguments:
# device_id, manufacturer_id, product_id, components, version_major, version_minor, version_aux


def hpm_conv(img_data, compression_enable, quiet_mode=False, **kwargs):
    # Build HPM upgrade image header
    result = hpm.upg_image_hdr(**kwargs)

    # Append HPM upgrade action (HPM prepare action)
    result += hpm.upg_action_hdr(**{
        'action_type': hpm.UpgradeActionType.Prepare,
        **kwargs
    })

    # Compress data if compression enabled
    if compression_enable:
        enc_data = rle.encode(img_data, quiet_mode)
        if not quiet_mode:
            print('Verifying compressed data...')
        if rle.decode(enc_data) != img_data:
            print(f'RLE compression verify mismatch', file=sys.stderr)
            sys.exit(-1)
        if not quiet_mode:
            print('RLE compression verify OK\n')

        img_comp_hdr = b'COMPRESSED\x00'
        img_comp_hdr += int.to_bytes(len(img_data), length=4, byteorder='big')
        img_data = img_comp_hdr + enc_data

    # Append HPM upgrade action image
    result += hpm.upg_action_img(
        img_data,
        **kwargs
    )

    # Append MD5 hash
    result += hpm.upg_img_hash(result)
    return result
