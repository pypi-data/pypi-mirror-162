import json

import flask
from manhattan.forms import fields
from wtforms import widgets

from manhattan.assets.image_sets import ImageSet
from manhattan.assets.validators import AssetType

__all__ = [
    'AssetField',
    'ImageField',
    'ImageSetField'
]


class AssetField(fields.Field):
    """
    A field that supports a file being uploaded.
    """

    widget = widgets.HiddenInput()

    def __init__(self, label=None, validators=None, render_kw=None, **kwargs):

        # Ensure the field is flagged as an asset field
        if not render_kw:
            render_kw = {}

        render_kw['data-mh-file-field'] = True

        # Flag indicating if the asset's base transforms have changed (which
        # would indicate that the asset's variations need to be regenerated).
        self.base_transform_modified = False

        super().__init__(label, validators, render_kw=render_kw, **kwargs)

    def __call__(self, **kwargs):

        if flask.has_request_context() \
                and 'data-mh-file-field--blueprint' not in kwargs:

            # Add the current blueprint to the field arguments
            kwargs['data-mh-file-field--blueprint'] = flask.request.blueprint

        return super().__call__(**kwargs)

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        elif self.data is not None:
            return json.dumps(self.data.to_json_type_for_field())
        return ''

    def process_data(self, value):
        """Process the the fields initial or default value"""
        self.data = value

    def process_formdata(self, values):
        """Process a value(s) submitted to the form"""
        if not values or not values[0]:
            self.data = None
            return

        # Convert the serialized asset JSON to an asset
        asset_data = json.loads(values[0])
        key = asset_data['key']
        base_transforms = asset_data.get('base_transforms')
        user_meta = asset_data.get('user_meta')

        if self.data and self.data.key == key:
            # Asset was original set as a value for the field
            asset = self.data

        else:
            # Attempt to retrieve asset from the temporary cache
            asset = flask.current_app.asset_mgr.get_temporary_by_key(key)

        if not asset:
            self.data = None
            return

        # Set any user defined meta data against the asset
        asset.user_meta = user_meta

        # For the base transforms we perform a comparison to flag that they
        # have been modified and therefore we need to regenerate existing
        # assets.
        old_transforms = json.dumps(asset.base_transforms)
        new_transforms = json.dumps(base_transforms)
        self.base_transform_modified = old_transforms != new_transforms

        asset.base_transforms = base_transforms

        # Cater for a preview URI provided client-side (required to provide
        # a preview after the field validates but the form fails to).
        if asset_data.get('preview_uri'):
            asset.preview_uri = asset_data['preview_uri']

        self.data = asset


class ImageField(AssetField):
    """
    A field that supports an image being uploaded.
    """

    def __init__(self,
        label=None,
        validators=None,
        render_kw=None,
        crop_aspect_ratio=None,
        fix_crop_aspect_ratio=False,
        **kwargs
    ):

        if not validators:
            validators = []

        # Require the asset be an image
        validators.append(AssetType('image'))

        if not render_kw:
            render_kw = {}

        # Flag the file type for the fields as an image
        render_kw['data-mh-file-field--file-type'] = 'image'

        # Set the label for the field (it not already set)
        render_kw['data-mh-file-field--label'] = render_kw.pop(
            'data-mh-file-field--label',
            'Upload an image...'
        )

        # Add crop settings to the render keywords
        if crop_aspect_ratio != None:
           render_kw['data-mh-file-field--crop-aspect-ratio'] \
                = crop_aspect_ratio

        if fix_crop_aspect_ratio:
            render_kw['data-mh-file-field--fix-crop-aspect-ratio'] = True

        # Default to accepting only images
        if 'data-mh-file-field--accept' not in render_kw:
            render_kw['data-mh-file-field--accept'] = 'image/*'

        super().__init__(label, validators, render_kw=render_kw, **kwargs)


class ImageSetField(fields.Field):
    """
    A field that supports a set of images being uploaded.

    Usage:

        class MyForm(BaseForm):

            my_image = ImageSetField(
                'My image',
                versions=[
                    ('l', 'Desktop', 2.0), # First is set as the base version
                    ('m', 'Tablet', 1.5),
                    ('s', 'Mobile', 1.0)
                ],
                validators=[validators.Required()]
            )

    Note: Each version is given as a tuple of the form:

    - version name
    - version label
    - crop aspect ratio for the version (optional)

    """

    widget = widgets.HiddenInput()

    def __init__(self,
        label=None,
        versions=None,
        fix_crop_aspect_ratio=False,
        validators=None,
        render_kw=None,
        **kwargs
    ):

        assert versions, 'You must give at least one version for an image set.'

        version_length = len(versions[0])
        assert version_length in [2, 3], (
            '`versions` argument must me given as '
            '(name, label) or (name, label, crop_ratio).'
        )
        for version in versions:
            assert len(version) == version_length, (
                'Each item in the `versions` argument must be the same '
                'length.'
            )

        assert not fix_crop_aspect_ratio or version_length == 3, (
            '`fix_crop_aspect_ratio` can not be true unless crop ratios have '
            'been given for each version.'
        )

        if not render_kw:
            render_kw = {}

        # Store the versions the image set supports
        self.versions = versions

        # Set the versions for the field
        render_kw['data-mh-image-set--versions'] = ','.join([
            v[0] for v in versions
        ])

        # Set the labels for each version in the image set
        render_kw['data-mh-image-set--version-labels'] = ','.join([
            v[1] for v in versions
        ])

        # Set the crop ratio for each version in the image set
        if version_length == 3:
            render_kw['data-mh-image-set--crop-aspect-ratios'] = ','.join([
                str(v[2]) for v in versions
            ])

        if fix_crop_aspect_ratio:
            render_kw['data-mh-image-set--fix-crop-aspect-ratio'] = True

        # Default to accepting only images
        if 'data-mh-image-set--accept' not in render_kw:
            render_kw['data-mh-image-set--accept'] = 'image/*'

        # Ensure the field is flagged as an image set field
        render_kw['data-mh-image-set'] = True

        # A set of keys indicating which of the image set's base transforms
        # have changed (which would indicate that the associated asset
        # variations need to be regenerated).
        self.modified_base_transforms = set([])

        super().__init__(label, validators, render_kw=render_kw, **kwargs)

    def __call__(self, **kwargs):

        if flask.has_request_context() \
                and 'data-mh-image-set--blueprint' not in kwargs:

            # Add the current blueprint to the field arguments
            kwargs['data-mh-image-set--blueprint'] \
                    = flask.request.blueprint

        return super().__call__(**kwargs)

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        elif self.data is not None:
            return json.dumps(self.data.to_json_type_for_field())
        return ''

    def process_data(self, value):
        """Process the the fields initial or default value"""
        self.data = value

    def process_formdata(self, values):
        """Process a value(s) submitted to the form"""
        if not values or not values[0]:
            self.data = None
            return

        # Convert the serialized JSON to an image set
        image_set_data = json.loads(values[0])
        images = image_set_data.get('images', {})
        base_transforms = image_set_data.get('base_transforms', {})
        base_version = image_set_data.get('base_version', self.versions[0][0])
        alt = image_set_data.get('alt', '')

        # Build a list of valid versions
        valid_versions = [v[0] for v in self.versions]

        # Check the base version is one of the valid versions
        if base_version not in valid_versions:
            self.data = None
            return

        # Check that all base transforms are valid
        for version, transforms in base_transforms.items():
            if version not in valid_versions:
                self.data = None
                return

        # (Re)build the image set instance ensuring data is trusted
        image_set = ImageSet(
            images={},
            base_transforms=base_transforms,
            base_version=base_version,
            alt=alt
        )

        for version in valid_versions:

            # Convert the assets within the image set to `Asset` instances
            image_data = image_set_data['images'].get(version)

            if image_data:
                image = None
                key = image_data.get('key')

                if (
                    self.data
                    and version in self.data.images
                    and self.data.images[version].key == key
                ):
                    # Asset initial set against value for the field
                    image = self.data.images[version]

                else:
                    # Attempt to retrieve asset from the temporary cache
                    image = flask\
                            .current_app.asset_mgr.get_temporary_by_key(key)

                if image and image.type == 'image':
                    image_set.images[version] = image

            # Cater for a preview URIs provided client-side (required to
            # provide a preview after the field validates but the form fails
            # to).
            if image_set_data.get('preview_uris'):
                image_set.preview_uris = image_set_data['preview_uris']

            # Determine if the user has changed the base transform for the
            # version.
            old_transforms = None
            new_transforms = base_transforms.get(version)

            if self.data:
                old_transforms = self.data.base_transforms.get(version)

            if json.dumps(old_transforms) != json.dumps(new_transforms):
                self.modified_base_transforms.add(version)

        # Set the data for the field
        self.data = None
        if image_set.base_image:
            self.data = image_set

