"""
Generic gallery chain.

: `gallery_field`
    The field against the document that stores the gallery of assets (required).

: `projection`
    The projection used when requesting the document from the database (defaults
    to None which means the detault projection for the frame class will be
    used).

    NOTE: The `gallery_field` must be one of the projected fields otherwise the
    gallery will always appear to be empty.

: `remove_assets`
    If True then assets associated with the document will be removed when they
    are removed from the gallery.

: `validators`
    A list of validators (see manhattan.assets.validators) that will be used to
    validate assets within to the gallery (defaults to None, as in no
    validation).

"""

import json

import flask
from manhattan.assets import Asset
from manhattan.assets.fields import AssetField
from manhattan.assets.transforms.base import BaseTransform
from manhattan.chains import Chain, ChainMgr
from manhattan.forms import BaseForm, validators
from manhattan.nav import Nav, NavItem
from werkzeug.datastructures import MultiDict

from manhattan.manage.views import (
    factories as manage_factories,
    utils as manage_utils
)

__all__ = ['gallery_chains']


# Define the chains
gallery_chains = ChainMgr()

# GET
gallery_chains['get'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'get_assets_from_document',
    'decorate',
    'render_template'
    ])

# POST
gallery_chains['post'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'get_assets_from_form',
    'validate',
    [
        [
            'store_assets',
            'redirect'
        ],
        [
            'decorate',
            'render_template'
        ]
    ]
])


# Define the links
gallery_chains.set_link(
    manage_factories.config(
        gallery_field=None,
        gallery_render_kw=None,
        gallery_validators=None,
        remove_assets=False
    )
)
gallery_chains.set_link(manage_factories.authenticate())
gallery_chains.set_link(manage_factories.get_document())
gallery_chains.set_link(manage_factories.render_template('gallery.html'))
gallery_chains.set_link(manage_factories.redirect('view', include_id=True))

@gallery_chains.link
def decorate(state):
    """
    Add decor information to the state (see `utils.base_decor` for further
    details on what information the `decor` dictionary consists of).

    This link adds a `decor` key to the state.
    """
    document = state[state.manage_config.var_name]
    state.decor = manage_utils.base_decor(
        state.manage_config,
        state.view_type,
        document
    )

    # Title
    state.decor['title'] = state.manage_config.titleize(document)

    # Breadcrumbs
    if Nav.exists(state.manage_config.get_endpoint('list')):
        state.decor['breadcrumbs'].add(
            manage_utils.create_breadcrumb(state.manage_config, 'list')
        )

    if Nav.exists(state.manage_config.get_endpoint('view')):
        state.decor['breadcrumbs'].add(
            manage_utils.create_breadcrumb(
                state.manage_config,
                'view',
                document
            )
        )
    state.decor['breadcrumbs'].add(NavItem('Gallery'))

@gallery_chains.link
def get_assets_from_document(state):
    """
    Get the asset information for the gallery from the document (GET).

    This link adds `assets` to the state which contains the list of assets to
    be stored against the gallery field, and `assets_json_type` which is a
    used in the template to provide the frontend JS with a serialzied version
    of the assets.
    """

    assert state.gallery_field, 'No gallery field defined'

    # Get assets currently stored against the document
    state.assets = []
    document = state[state.manage_config.var_name]

    for asset in (document.get(state.gallery_field) or []):

        if not isinstance(asset, Asset):
            asset = Asset(asset)
            for k, v in asset.variations.items():
                asset.variations[k] = Asset(v)

        state.assets.append(asset)

    state.assets_json_type = [a.to_json_type_for_field() for a in state.assets]

@gallery_chains.link
def get_assets_from_form(state):
    """
    Get the asset information for the gallery from the form (POST).

    This link adds `assets` to the state which contains the list of assets to
    be stored against the gallery field, and `assets_json_type` which is a
    used in the template to provide the frontend JS with a serialzied version
    of the assets.
    """

    assert state.gallery_field, 'No gallery field defined'

    # Build a map of existing assets stored against the document
    existing_assets = {}
    document = state[state.manage_config.var_name]

    for asset in (document.get(state.gallery_field) or []):

        if not isinstance(asset, Asset):
            asset = Asset(asset)

        existing_assets[asset.key] = asset

    # Store a dictionary of assets with modified base transforms (e.g
    # they've been cropped or rotated and need their variations
    # regenerated).
    state.base_transforms_modified = {}

    # Get assets submitted in the form
    state.assets = []

    for asset_data in json.loads(flask.request.form.get(state.gallery_field)):

        if asset_data.get('temporary', False):

            # Fetch the asset from the temporary asset cache to ensure we get
            # an unmodified version (we can't trust the submitted version).
            asset = flask.current_app.asset_mgr\
                    .get_temporary_by_key(asset_data['key'])

        elif asset_data['key'] in existing_assets:

            # Fetch the existing asset from the document
            asset = existing_assets[asset_data['key']]

            # Flag if the base transforms for an existing asset have changed
            # (e.g it was cropped or rotated).
            if (
                json.dumps(asset.base_transforms, sort_keys=True) \
                != json.dumps(asset_data['base_transforms'], sort_keys=True)
            ):
                state.base_transforms_modified[asset_data['key']] = True

        # Update the asset's base transforms, meta and preview URI based on
        # the submitted values.
        asset.base_transforms = asset_data['base_transforms']
        asset.user_meta = asset_data['user_meta']
        asset.preview_uri = asset_data.get('preview_uri', None)

        state.assets.append(asset)

    state.assets_json_type = [a.to_json_type_for_field() for a in state.assets]

@gallery_chains.link
def validate(state):
    """
    Validate the gallery of assets.

    If there's an error against one or more of the assets in the gallery then
    this link will add `asset_errors` to the state. This is dictionary if
    errors with the asset `key` property as the key and the error message as
    the value.
    """

    if not state.gallery_validators:

        # No validators for gallery assets, nothing to do
        return True

    class AssetForm(BaseForm):

        asset = AssetField(
            'Asset',
            validators=[validators.Required(), *state.gallery_validators]
        )

    # Validate the submitted assets
    all_assets_valid = True

    for asset in state.assets:

        form_data = MultiDict({'asset': json.dumps(asset.to_json_type())})
        form = AssetForm(form_data, asset=None if asset.temporary else asset)

        if not form.validate():
            errors = ' '.join(form.errors['asset'])
            flask.flash(f'{asset.filename}: {errors}')
            all_assets_valid = False

    return all_assets_valid

@gallery_chains.link
def store_assets(state):
    """
    Store changes to the assets for the document. This includes converting
    temporary assets to permanent assets and generating variations for assets
    with modified base transforms (e.g that have been cropped or rotated).
    """

    # Build a list of assets to make permanent (persist), to generate new
    # variations for (transform) and to remove.
    assets_to_persist = []
    assets_to_transform = []
    assets_to_remove = []

    for asset in state.assets:

        if asset.temporary:
            assets_to_persist.append(asset)

            if not asset.base_transforms:
                continue

        else:

            if asset.key not in state.base_transforms_modified:
                continue

        # Build the transform instructions required to regenerate variations
        # for the asset.

        # Get variations defined for the gallery field against the manage
        # config.
        variations = state.manage_config.asset_variations.get(
            state.gallery_field,
            {}
        )

        if asset.variations:

            # Check for local transforms against the asset which are added to
            # and may override variations defined for the gallery field.
            for variation_name, variation_asset in asset.variations.items():

                if not isinstance(variation_asset, Asset):
                    variation_asset = Asset(variation_asset)

                variations[variation_name] = [
                    BaseTransform.from_json_type(t)
                    for t in variation_asset.local_transforms
                ]

        # Ensure the system set '--draft--' variation is never updated
        variations.pop('--draft--', None)

        if variations:

            # Add the tranform information for the asset (the asset,
            # variations and base transforms).
            assets_to_transform.append((
                asset,
                variations,
                [
                    BaseTransform.from_json_type(t)
                    for t in asset.base_transforms
                ]
            ))

    # Determine which assets need to be removed
    document = state[state.manage_config.var_name]
    assets_table = {a.key for a in state.assets}

    for asset in (document.get(state.gallery_field) or []):

        if not isinstance(asset, Asset):
            asset = Asset(asset)

        if asset.key not in assets_table:
            assets_to_remove.append(asset)

    # Store assets permanently
    asset_mgr = flask.current_app.asset_mgr
    asset_mgr.persist_many(assets_to_persist)

    # Generate variations
    asset_mgr.generate_variations_for_many(
        [a[0] for a in assets_to_transform],
        {a[0].key: a[1] for a in assets_to_transform},
        {a[0].key: a[2] for a in assets_to_transform}
    )

    # Update the document
    if hasattr(document, 'logged_update'):
        document.logged_update(
            state.manage_user,
            {state.gallery_field: [a.to_json_type() for a in state.assets]},
            state.gallery_field
        )

    else:
        setattr(document, state.gallery_field, state.assets)
        document.update(state.gallery_field)

    if state.remove_assets:

        # Remove assets
        asset_mgr.remove_many(assets_to_remove)

    flask.flash('{document} updated.'.format(document=document))
