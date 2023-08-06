"""
Generic upload asset chain.

NOTE: The generic upload chain is designed to handle a single file upload,
multiple file uploads client side should result in multiple calls to the upload
chain.
"""

import os

import flask
from manhattan.assets.transforms.images import Fit, Output
from manhattan.assets.backends import exceptions
from manhattan.chains import Chain, ChainMgr

from manhattan.manage.views import factories
from manhattan.manage.views import utils
from manhattan.manage.utils import get_config

__all__ = ['upload_chains']


# Define the chains
upload_chains = ChainMgr()

# POST
upload_chains['post'] = Chain([
    'config',
    'authenticate',
    'store_temporary_asset',
    'render_json'
])


# Define the links
upload_chains.set_link(factories.config())
upload_chains.set_link(factories.authenticate())

@upload_chains.link
def store_temporary_asset(state):
    """
    Store the file uploaded as a temporary asset.

    The client request is expected to include a file under the parameter name of
    `file`.

    If the file is successfully stored this links adds an `asset` key to the
    state containing the `Asset` instance representing the uploaded file.

    IMPORTANT: Validation of the asset itself is the responsibility of the view
    that is storing the associated parent document, not the upload chain. The
    upload chain merely validates that a file was provided and could be stored.
    """

    # Check a file was provided
    if 'file' not in flask.request.files \
            or not flask.request.files['file'].filename:
        return utils.json_fail('No file sent')

    # Apply the whitelist to
    file = flask.request.files['file']

    if state.ext_whitelist is None:
        state.ext_whitelist = [
            '.7z',
            '.csv',
            '.doc',
            '.docx',
            '.eml',
            '.gif',
            '.jpeg',
            '.jpg',
            '.key',
            '.keynote',
            '.md',
            '.mp3',
            '.msg',
            '.odf',
            '.ods',
            '.odt',
            '.ogg',
            '.pages',
            '.pdf',
            '.png',
            '.ppt',
            '.pptx',
            '.rar',
            '.rtf',
            '.svg',
            '.tif',
            '.tiff',
            '.txt',
            '.webp',
            '.xls',
            '.xlsm',
            '.xlsx',
            '.zip'
        ]

    if len(state.ext_whitelist):

        filename, ext = os.path.splitext(file.filename)

        if ext.lower() not in state.ext_whitelist:
            return utils.json_fail('Not a supported file type.')

    # Attempt to store the file
    asset_mgr = flask.current_app.asset_mgr
    asset_name = state.asset_name

    if callable(asset_name):
        asset_name = asset_name(file.filename)

    try:

        state.asset = asset_mgr.store_temporary(
            (file.filename, file),
            name=asset_name,
            secure=flask.request.values.get('secure') == 'secure'
        )

    except exceptions.StoreError as e:
        return utils.json_fail(str(e))

    # Check to see if an image file type has been requested and if so validate
    # the asset backend recognized it as an image.
    file_type = flask.request.values.get('file_type')
    if file_type == 'image':
        if state.asset.type != file_type:
            return utils.json_fail('Not a supported: ' + file_type)

    # Attempt to get the config manager associated with the upload
    blueprint_name = flask.request.values.get('blueprint', None)
    blueprint_config = None
    if blueprint_name:
        blueprint_config = get_config(flask.current_app, blueprint_name)

    # Look up any analyzers and variations (transforms) associated with the
    # uploaded file.
    field_name = flask.request.values.get('field_name', None)

    analyzers = {}
    variations = {}

    if blueprint_config and field_name:
        analyzers = blueprint_config.asset_analyzers.get(field_name, {})
        variations = blueprint_config.asset_variations.get(field_name, {})

        # Image sets may request that only one specific variations is
        # generated (e.g non-base versions only generate their respective
        # variation).
        version = flask.request.values.get('version')
        if version and version in variations:
            variations = {version: variations[version]}

    # We perform any analysis and transformation of assets eagerly (e.g when
    # they are temporary). Whilst variations may need to be regenerated for an
    # asset before storing it permanently (if it has base transforms) for the
    # majority of cases eager generation distributes the work load better.

    if analyzers:

        # Perform analysis
        try:
            asset_mgr.analyze(state.asset, analyzers)

        except exceptions.StoreError as e:
            return utils.json_fail(str(e))

    in_page_upload = flask.request.values.get('in_page') == 'in_page'
    if variations or in_page_upload:

        if state.asset.type == 'image':

            # Add system variations for the image (required for the thumbnail
            # preview and draft that appears in the image editor).

            # Thumbnail
            if variations:
                variations['--thumb--'] = flask.current_app.config.get(
                    'ASSET_THUMB_VARIATION',
                    [
                        Fit(480),
                        Output('jpg', 75)
                    ]
                )

            # Draft
            variations['--draft--'] = flask.current_app.config.get(
                'ASSET_DRAFT_VARIATION',
                [
                    Fit(1200),
                    Output('jpg', 50)
                ]
            )

        # Perform transforms
        try:
            asset_mgr.generate_variations(state.asset, variations)

        except exceptions.StoreError as e:
            return utils.json_fail(str(e))

        if '--thumb--' in variations:

            # Store the thumbnail transforms so the variation can be
            # regenerated outside of this view (draft variations are not
            # regenerated as a rule).
            state.asset.variations['--thumb--'].local_transforms = [
                t.to_json_type() for t in variations['--thumb--']
            ]

    # Store a temporary copy of the temporary asset
    asset_mgr.update_cache(state.asset)

@upload_chains.link
def render_json(state):
    """
    Return a successful response with the uploaded `asset` included in the
    payload.
    """
    return utils.json_success({'asset': state.asset.to_json_type_for_field()})
