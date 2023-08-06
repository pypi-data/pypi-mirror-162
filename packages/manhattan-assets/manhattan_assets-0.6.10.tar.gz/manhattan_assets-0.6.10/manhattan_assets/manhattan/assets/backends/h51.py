"""
Asset backend for Hangar51.
"""

from datetime import datetime, timedelta
import json

import h51
from h51.exceptions import H51Exception
from h51 import resources
from manhattan.assets import transforms
from manhattan.assets import transforms
from manhattan.assets import Asset
from manhattan.assets.backends.base import BaseAssetMgr
from manhattan.assets.backends.exceptions import RetrieveError, StoreError
from manhattan.assets.transforms.base import BaseTransform

__all__ = ['AssetMgr']


# Transforms

def _output_transform(t):

    image_formats = {
        'gif': 'GIF',
        'jpg': 'JPEG',
        'png': 'PNG',
        'webp': 'WebP'
    }

    settings = {'image_format': image_formats.get(t.settings['format'])}

    if t.settings.get('lossless') is not None:
        settings['lossless'] = t.settings.get('lossless')

    if t.settings.get('quality') is not None:
        settings['quality'] = t.settings.get('quality')

    return ['output', settings]


# Backend

class AssetMgr(BaseAssetMgr):
    """
    Asset manager using the h51 (Hangar51) service API.
    """

    # Analyzer converters
    _analyzer_converters = {
        '__custom__': lambda a: [a.id.split('.')[-1], a.settings]
    }

    # Transform converters
    _transform_converters = {
        'image.crop': lambda t: ['crop', t.settings],
        'image.fit': lambda t: ['fit', t.settings],
        'image.output': _output_transform,
        'image.rotate': lambda t: [
            'rotate',
            {'degrees': t.settings['angle']}
        ],
        '__custom__': lambda t: [t.id.split('.')[-1], t.settings]
    }

    def __init__(self, api_key, api_base_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Build the lcient keyword arguments
        client_kwargs = {}

        if api_base_url:
            client_kwargs['api_base_url'] = api_base_url

        # Set up an client for the Hangar51 API
        self._client = h51.Client(api_key, **client_kwargs)

    def analyze(self, asset, analyzers):
        """Analyze the asset"""

        # Analyze the asset
        try:
            r = self._client(
                'post',
                f'assets/{asset.key}/analyze',
                data={
                    'analyzers': json.dumps(self.convert_analyzers(analyzers))
                }
            )

        except H51Exception as e:
            raise StoreError(str(e))

        # Update the asset's meta data
        asset.core_meta = r['meta']

        # Update any instance of the asset in the cache (e.g if the asset is
        # temporary).
        self.update_cache(asset)

    def analyze_many(self, assets, analyzers):
        """Analyze the given list of asseta"""

        if not assets:
            return

        # Build a lookup table for the assets
        asset_table = {a.key: a for a in assets}

        try:
            response = self._client(
                'post',
                f'assets/analyze',
                data={
                    'analyzers': json.dumps({
                        k: self.convert_analyzers(v)
                        for k, v in analyzers.items()
                    }),
                    'local': True,
                    'uids': [a.key for a in assets],
                }
            )

            # Store the analysis against the assets
            for r in response['results']:

                asset = asset_table[r['uid']]

                # Update the asset's meta data
                asset.core_meta = r['meta']

                # Update any instance of the asset in the cache (e.g if the
                # asset is temporary).
                self.update_cache(asset)

        except H51Exception as e:
            raise StoreError(str(e))

    def generate_variations(
        self,
        asset,
        variations,
        base_transforms=None
    ):
        """Generate variations for the asset"""

        base_transforms = base_transforms or []

        # Build the manifest of variations to generate
        manifest = {}
        for name, local_transforms in variations.items():

            # Auto-orient by default
            manifest[name] = [['auto_orient', {}]]

            # Convert the transforms to h51 format
            manifest[name] += self.convert_transforms(
                base_transforms + local_transforms
            )

        try:

            r = self._client(
                'put',
                f'assets/{asset.key}/variations',
                data={'variations': json.dumps(manifest)}
            )

            # Store the variations against the asset
            for name in variations:
                variation = r['variations'].get(name)
                if variation:
                    asset_variation = Asset(
                        base=False,
                        key=f'{asset.key}.{name}',
                        filename=variation['store_key'],
                        type=asset.type,
                        core_meta=variation['meta'],
                        local_transforms=[
                            BaseTransform.to_json_type(t)
                            for t in variations[name]
                        ],
                        secure=asset.secure
                    )
                    asset.variations[name] = asset_variation

        except H51Exception as e:
            raise StoreError(str(e))

        # Update the base transforms for the asset
        asset.base_transforms = [
            BaseTransform.to_json_type(t)
            for t in base_transforms
        ]

        # Update any instance of the asset in the cache (e.g if the asset is
        # temporary).
        self.update_cache(asset)

    def generate_variations_for_many(
        self,
        assets,
        variations,
        base_transforms=None
    ):
        """Generate variations for the given assets"""
        if not assets:
            return

        base_transforms = base_transforms or {}

        # Build a lookup table for the assets
        asset_table = {a.key: a for a in assets}

        # Build the manifest for each of the assets
        manifests = {}
        for asset in assets:
            manifests[asset.key] = {}

            for name, local_transforms in variations[asset.key].items():

                # Auto-orient by default
                manifests[asset.key][name] = [['auto_orient', {}]]

                # Convert the transforms to h51 format
                manifests[asset.key][name] += self.convert_transforms(
                    base_transforms.get(asset.key, []) + local_transforms
                )

        try:

            # Generate variations
            response = self._client(
                'put',
                f'assets/transform',
                data={
                    'local': True,
                    'uids': [a.key for a in assets],
                    'variations': json.dumps(manifests)
                }
            )

            # Store the variations against the assets
            for r in response['results']:

                asset = asset_table[r['uid']]

                for name in variations[asset.key]:
                    variation = r['variations'].get(name)
                    if variation:
                        asset_variation = Asset(
                            base=False,
                            key=f'{asset.key}.{name}',
                            filename=variation['store_key'],
                            type=asset.type,
                            core_meta=variation['meta'],
                            local_transforms=[
                                BaseTransform.to_json_type(t)
                                for t in variations[asset.key][name]
                            ],
                            secure=asset.secure
                        )
                        asset.variations[name] = asset_variation

                # Update the base transforms for the asset
                asset.base_transforms = [
                    BaseTransform.to_json_type(t)
                    for t in base_transforms.get(asset.key, [])
                ]

                # Update any instance of the asset in the cache (e.g if the
                # asset is temporary).
                self.update_cache(asset)

        except H51Exception as e:
            raise StoreError(str(e))

    def persist_many(self, assets):
        """Set the given list of assets as permenant"""

        if not assets:
            return None

        try:
            # Flag that the given assets should be stored permanently
            resources.Asset.persist_many(
                self._client,
                [a.key for a in assets]
            )
        except H51Exception as e:
            raise StoreError(str(e))

        for asset in assets:

            # Flag the asset as no longer temporary
            asset.temporary = False

            # Clear any reference to the temporary asset
            self.clear_cache(asset)

    def remove(self, asset):
        """Remove the specified asset"""
        try:
            resources.Asset.expire_many(
                self._client,
                [asset.key],
                0
            )
        except H51Exception as e:
            raise StoreError(str(e))

    def remove_many(self, assets):
        """Remove the given list of asset"""
        if not assets:
            return None

        try:
            resources.Asset.expire_many(
                self._client,
                [a.key for a in assets],
                0
            )
        except H51Exception as e:
            raise StoreError(str(e))

    def retrieve(self, asset):
        """Retrieve the asset (the file)"""
        try:
            data = self._client(
                'get',
                f'assets/{asset.key}/download',
                download=True
            )

        except H51Exception as e:
            raise RetrieveError(str(e))

        return data

    def store_temporary(self, file, name=None, secure=False):
        """Store an asset temporarily"""

        # Store the file
        try:
            h51_asset = resources.Asset.create(
                self._client,
                file,
                name=name,
                expire=self._expire_after,
                secure=secure
            )

        except H51Exception as e:
            raise StoreError(str(e))

        # Create an asset representing the file
        asset = Asset(
            base=True,
            key=h51_asset.uid,
            filename=h51_asset.store_key,
            type=h51_asset.type,
            core_meta=h51_asset.meta,
            secure=h51_asset.secure,
            temporary=True
        )

        # Store the asset as a temporary asset
        self.update_cache(asset)

        return asset

    def store(self, file_or_asset, name=None, secure=False):
        """
        Store an asset.

        NOTE: The `name` argument is ignored if an asset is provided, to rename
        an existing asset you must clone the asset with a new name and then
        store the resulting temporary asset.

        NOTE: The `secure` argument is ignored if an asset is provided.
        """

        asset = None

        if isinstance(file_or_asset, Asset):
            asset = file_or_asset
            asset.temporary = False

            # Persist the asset
            try:
                r = self._client(
                    'post',
                    f'assets/{asset.key}/persist'
                )

            except H51Exception as e:
                raise StoreError(str(e))

            # Clear any reference to the temporary asset
            self.clear_cache(asset)

        else:
            # Store the file
            try:
                h51_asset = resources.Asset.create(
                    self._client,
                    file_or_asset,
                    name=name,
                    secure=secure
                )

            except H51Exception as e:
                raise StoreError(str(e))

            # Create an asset representing the file
            asset = Asset(
                base=True,
                key=h51_asset.uid,
                filename=h51_asset.store_key,
                type=h51_asset.type,
                core_meta=h51_asset.meta,
                secure=h51_asset.secure
            )

        return asset
