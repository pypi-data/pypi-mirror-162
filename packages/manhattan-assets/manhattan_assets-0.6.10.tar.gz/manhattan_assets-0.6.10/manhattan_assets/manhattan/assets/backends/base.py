"""
Classes for implementing a backend for asset management.
"""

import json

from manhattan.assets import Asset

__all__ = ['BaseAssetMgr']


# Classes

class BaseAssetMgr:
    """
    Assets are managed via an asset manager class which must provide the API
    defined by the `BaseAssetMgr` class.
    """

    # A table of functions that convert analyzers to a format understood by
    # the backend service.
    _analyzer_converters = None

    # A table of functions that convert transforms to a format understood by
    # the backend service.
    _transform_converters = None

    def __init__(self, cache, expire_after=3600):
        # The cache used to store references to temporary assets, must support
        # `get` and `set` methods, `set` must support an `timeout` argument
        # when the data will expire.
        #
        # `werkzeug.contrib.cache` provides a number of suitable classes for
        # creating caches (e.g `SimpleCache` and `MemcachedCache`).
        self._cache = cache

        # The amount of time before temporary assets expire
        self._expire_after = expire_after

    def analyze(self, asset, analyzers):
        """Analyze the asset"""
        raise NotImplementedError()

    def analyze_many(self, assets, analyzers):
        """Analyze the given list of asseta"""
        for asset in assets:
            self.generate_variations(asset, analyzers[asset.key])

    def clear_cache(self, asset):
        """Clear the given asset from the cache"""
        self._cache.delete(self.get_cache_key(asset.key))

    def clone(self, asset, name=None, secure=None):
        """Returning a temporary asset cloned from the specified asset"""
        secure = asset.secure if secure is None else secure

        # Retrieve the asset we're cloning
        file = self.retrieve(asset)

        # Store the file as a new temporary asset (cloning it)
        cloned = self.store_temporary(
            (file, asset.filename),
            name=name,
            secure=secure
        )

        return cloned

    def generate_variations(self, asset, variations, base_transforms=None):
        """Generate variations for the asset"""
        raise NotImplementedError()

    def generate_variations_for_many(
        self,
        assets,
        variations,
        base_transforms=None
    ):
        """Generate variations for the given assets"""
        base_transforms = base_transforms or {}

        for asset in assets:
            self.generate_variations(
                asset,
                variations[asset.key],
                base_transforms.get(asset.key, None)
            )

    def get_temporary_by_key(self, key):
        """Get a temporary asset by it's key"""
        asset_json = self._cache.get(self.get_cache_key(key))
        if asset_json:
            asset = Asset(json.loads(asset_json))
            for name, variation in asset.variations.items():
                asset.variations[name] = Asset(variation)
            return asset

    def persist_many(self, assets):
        """Set the given list of assets as permenant"""
        for asset in assets:
            self.store(asset)

    def remove(self, asset):
        """Remove the specified asset"""
        raise NotImplementedError()

    def remove_many(self, assets):
        """Remove the given list of assets"""
        for asset in assets:
            self.remove(asset)

    def retrieve(self, asset):
        """Retrieve the asset"""
        raise NotImplementedError()

    def store_temporary(self, file, name=None, secure=False):
        """Store an asset temporarily"""
        raise NotImplementedError()

    def store(self, file_or_asset, name=None, secure=False):
        """
        Store an asset.

        NOTE: The `name` argument is ignored if an asset is provided, to rename
        an existing asset you must clone the asset with a new name and then
        store the resulting temporary asset.

        NOTE: The `secure` argument is ignored if an asset is provided.
        """
        raise NotImplementedError()

    def update_cache(self, asset):
        """Update the given asset in the cache"""
        if asset.temporary:
            self._cache.set(
                self.get_cache_key(asset.key),
                json.dumps(asset.to_json_type()),
                self._expire_after
            )

    # Class methods

    @classmethod
    def get_cache_key(cls, asset_key):
        return f'temporary_assets:{asset_key}'

    @classmethod
    def convert_analyzers(cls, analyzers):
        """
        Convert a stack of analyzers to a format understood by the backend
        service.
        """

        backend_analyzers = []
        for analyzer in analyzers:
            converter = cls._analyzer_converters.get(analyzer.id)
            if not converter:
                converter = cls._analyzer_converters.get('__custom__')
            backend_analyzers.append(converter(analyzer))

        return backend_analyzers

    @classmethod
    def convert_transforms(cls, transforms):
        """
        Convert a stack of transforms to a format understood by the backend
        service.
        """

        backend_transforms = []
        for transform in transforms:
            converter = cls._transform_converters.get(transform.id)
            if not converter:
                converter = cls._transform_converters.get('__custom__')
            backend_transforms.append(converter(transform))

        return backend_transforms
