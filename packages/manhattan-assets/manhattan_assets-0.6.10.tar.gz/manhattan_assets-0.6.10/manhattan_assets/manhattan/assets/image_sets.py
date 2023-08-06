
from mongoframes import SubFrame

from .assets import Asset

__all__ = ['ImageSet']


class ImageSet(SubFrame):
    """
    `ImageSets` are used specificially to implement <picture> tags in HTML.
    ImageSets provide (typically) multiple version of an image to be displayed for
    different media queries. Each image may be either a seperate transform
    (crop/rotate) of a base image (asset) or can be a unique image (asset).

    Usage (building a picture element in a template):

        <picture class="article__image">
            {% for srcset, media in image_set.sources(
                l='(min-width: 960px)',
                m='(min-width: 720px)'
            ) %}
                {{ source|safe }}
            {% endif %}

            <img
                src="{{ image_set.url('s', 'm', 'l') }}"
                alt="{{ image_set.alt }}"
            >
        </picture>

    """

    _fields = {
        # A table of images that represent the image set, if a key for an
        # image is not present in the table then we reference the base image.
        'images',

        # A table of transforms (crop/rotate) each image within the image set,
        # if a key for an image is not present in the table then we reference
        # the transform for the base image, and if no base image transforms are
        # present then the base image us used.
        'base_transforms',

        # The verion of the image within the `images` table that represents
        # the base image. The first image uploaded for an image set is
        # generally considered the base image, other images in the image set
        # will often be different crops of the base image.
        'base_version',

        # An alt tag for the image represented by the image set
        'alt'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # A map of preview URIs for the assets set when assets are been
        # modified client-side. This value is never stored in the database and
        # is used to allow a preview to persist between multiple form
        # submissions.
        self.preview_uris = None

    @property
    def base_image(self):
        return self.images.get(self.base_version)

    @property
    def versions(self):
        versions = []
        for image in self.images.values():
            for version in image.variations.keys():
                versions.append(version)
        return list(set(versions))

    def variation(self, version):
        """Return the image for the given version"""
        image = self.images.get(version, self.base_image)
        if version in image.variations:
            return image.variations[version]

    def sources(self, **versions):
        """
        Return a list of srcset URLs and media queries for the given versions.

        Usage:

            versions = {
                l='(min-width: 960px)',
                m='(min-width: 720px)'
            }

            for url, media in image_set.sources(versions):
                ...
        """
        sources = []

        base_image = self.base_image
        for version, media in versions.items():
            image = self.images.get(version, base_image)

            if version in image.variations:
                sources.append((image.variations[version].url, media))

        return sources

    def to_json_type_for_field(self):
        document_dict = self._json_safe_for_field(self._document)
        self._remove_keys(document_dict, self._private_fields)

        if self.preview_uris:
            document_dict['preview_uris'] = self.preview_uris

        return document_dict

    def url(self, version):
        """Return the URL for the given version"""
        variation = self.variation(version)
        if variation:
            return variation.url

    @classmethod
    def _json_safe_for_field(cls, value):
        """Return a JSON safe value"""

        if isinstance(value, Asset):
            return value.to_json_type_for_field()

        # Lists
        elif isinstance(value, (list, tuple)):
            return [cls._json_safe_for_field(v) for v in value]

        # Dictionaries
        elif isinstance(value, dict):
            return {
                k: cls._json_safe_for_field(v)
                for k, v in value.items()
            }

        return cls._json_safe(value)

    @classmethod
    def default_projection(cls):
        """
        Short-cut for defining a simple projection, usage:

            projection = {
                'image_set': ImageSet.default_projection()
            }

        """
        projection = {
            '$sub': cls,
            'images': {
                '$sub.': Asset,
                'variations': {'$sub.': Asset}
            }
        }
        return projection
