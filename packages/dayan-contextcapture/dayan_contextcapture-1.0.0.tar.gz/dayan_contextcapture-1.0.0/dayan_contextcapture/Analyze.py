import os
import exifread
from PIL import Image


def check_photogroup(path):
    """Get the info of photo

    Args:
        path (str): photo local path

    Returns:
        list
    """
    if not os.path.isdir(path):
        print(" %s is not a path to a photo group!" % path)
        return

    photo_nums = len([ph for ph in os.listdir(path) if ph.endswith(('jpg', 'jpeg', 'JPG', 'JPEG'))])
    photo_info = []

    for filename in os.listdir(path):
        if filename.endswith(('jpg', 'jpeg', 'JPG', 'JPEG')):
            file_name_path = os.path.join(path, filename)
            photo_info = get_image_exif(file_name_path, photo_info)
            if photo_info is not []:
                photo_info[0]['pic_count'] = photo_nums
                break
    return photo_info


def get_image_exif(path, photo_info):
    """Get photo exif info.

    Args:
        path (str): local photo path.
        photo_info (list): photo info .
    Returns:
        photo_info (list).
    """
    with open(path, 'rb') as f:
        tags = exifread.process_file(f)
        if tags:
            photo_info.append({
                'focal_length': eval(tags['EXIF FocalLength'].printable) if 'EXIF ExifImageLength' in tags else '',
                'camera_producter': tags['Image Make'].printable if 'Image Make' in tags else '',
                'camera_model': tags['Image Model'].printable if 'Image Model' in tags else '',
                'pic_width': tags['EXIF ExifImageWidth'].printable if 'EXIF ExifImageWidth' in tags else '',
                'pic_height': tags['EXIF ExifImageLength'].printable if 'EXIF ExifImageLength' in tags else ''
            })
        else:
            img = Image.open(f)
            photo_info.append({
                'focal_length': '',
                'camera_producter': '',
                'camera_model': '',
                'pic_width': img.width,
                'pic_height': img.height
            })
    return photo_info



