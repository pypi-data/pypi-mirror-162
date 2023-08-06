from .assets import *
from .image_sets import *
from . import analyzers
from . import fields
from . import makers
from . import static
from . import transforms
from . import validators

from manhattan.assets import Asset
from manhattan.assets.views.upload import upload_chains

__all__ = ['Assets']


class Assets:
    """
    The `Assets` class provides the initialization code for the package.
    """

    def __init__(self, app, root, backend, settings=None, secure_root=None):
        self._app = app

        # Configure the URL root for assets
        Asset._asset_root = root
        Asset._secure_asset_root = secure_root

        # Set up the asset manager
        self._app.asset_mgr = backend.AssetMgr(**(settings or {}))

        # Set up views
        self.setup_views()

    def setup_views(self):
        """
        Set up views for managing assets.
        """

        # Upload
        self._app.add_url_rule(
            '/upload-asset',
            endpoint='upload_asset',
            view_func=upload_chains.copy().flask_view(),
            methods=['POST']
        )
