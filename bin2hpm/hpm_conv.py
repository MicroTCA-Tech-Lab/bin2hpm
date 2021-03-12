from bin2hpm import hpm, rle
import sys

# supported arguments:
# device_id, manufacturer_id, product_id, components, version_major, version_minor, version_aux
def hpm_conv(img_data, compression_enable, **kwargs):
    # Build HPM upgrade image header
    result = hpm.upg_image_hdr(**kwargs)

    # Append HPM upgrade action (HPM prepare action)
    result += hpm.upg_action_hdr(**{
        'action_type': hpm.UpgradeActionType.Prepare,
        **kwargs
    })

    # Compress data if compression enabled
    if compression_enable:
        enc_data = rle.encode(img_data)
        print('Verifying compressed data...', end='')
        if rle.decode(enc_data) != img_data:
            print(f'RLE compression verify mismatch', file=sys.stderr)
            sys.exit(-1)
        print('OK\n')

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
