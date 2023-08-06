from flask import current_app
from .assets import Asset
from .image_sets import ImageSet

__all__ = [
    'min_file_projection',
    'min_image_projection',
    'min_image_set_projection'
]


def min_file_projection(field, extra=None):
    """Return a projection that will select minimal file info"""
    projection = {}
    projection[field] = {
        '$sub': Asset,
        'key': True,
        **(extra or {})
    }
    projection['.'.join([field, 'filename'])] = True
    projection['.'.join([field, 'core_meta', 'filename'])] = True
    projection['.'.join([field, 'core_meta', 'length'])] = True

    return projection

def min_image_projection(field, variations, extra=None):
    """Return a projection that will only select minimal image info"""
    projection = {}

    sub_projection = {'$sub.': Asset}
    for variation in variations:
        variation_path = variation
        sub_projection['.'.join([variation_path, 'filename'])] = True
        core_meta_path = '.'.join([variation_path, 'core_meta'])
        sub_projection['.'.join([core_meta_path, 'image', 'size'])] = True
        sub_projection['.'.join([core_meta_path, '__manhattan_fake__'])] = True
        user_meta_path = '.'.join([variation_path, 'user_meta'])
        sub_projection[user_meta_path] = True

    projection[field] = {
        '$sub': Asset,
        'key': True,
        'variations': sub_projection,
        **(extra or {})
    }
    projection['.'.join([field, 'filename'])] = True
    projection['.'.join([field, 'core_meta', 'image', 'size'])] = True
    projection['.'.join([field, 'user_meta'])] = True

    return projection

def min_image_set_projection(field, versions, extra=None):
    """Return a projection that will only select minimal image set info"""
    projection = {}
    projection[field] = {
        '$sub': ImageSet,
        'alt': True,
        'base_version': True
    }

    for version in versions:
        projection.update(
            min_image_projection(
                '.'.join([field, 'images', version]),
                versions,
                extra
            )
        )

    return projection
