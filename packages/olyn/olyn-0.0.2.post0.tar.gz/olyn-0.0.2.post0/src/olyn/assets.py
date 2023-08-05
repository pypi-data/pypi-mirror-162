"""Utils to use Olyn api assets route."""

from src.olyn.api import default as default_api
from src.olyn.errors import EndpointNotImplementedError


class Asset:
    """Asset class to bridge to Olyn-API."""

    @classmethod
    def get(cls, asset_id):
        """Get olyn asset by id."""
        response = default_api().get(f'v1/assets/{asset_id}')
        return response.json

    @classmethod
    def get_all_by_owner(cls, user_id, page: int = 1, page_size: int = 250):
        """Get Owner assets."""
        response = default_api().get(
            f"v1/assets/keys/data/olynWalletUuid?"
            f"page={page}&pageSize={page_size}"
        )

        return response.json

    @classmethod
    def search_units(cls, owner, query, page: int = 1, page_size: int = 20):
        """Search through assets."""
        payload = {
            'query': query,
            'owner': owner
        }
        response = default_api().post(
            f'v1/unit-cards/search?page={page}&pageSize={page_size}',
            payload
        )
        return response.json

    @classmethod
    def add_or_update_data_on_asset(
            cls,
            asset_id: str,
            payload: list[dict]
    ):
        """Add or Update data modules to a specific asset."""
        response = default_api().put(
            url=f'v1/assets/{asset_id}/keys/data',
            body={
                'assetData': payload
            }
        )
        return response.json

    @classmethod
    def transfer_asset(
            cls,
            asset_id: str,
            current_owner: str,
            new_owner: str,
            current_chain: str,
            new_chain: str
    ):
        """Change the status of an asset."""
        raise EndpointNotImplementedError()

    @classmethod
    def change_asset_status(
            cls,
            asset_id: str,
            status: str,
            public_key: str,
            chain: str
    ):
        """Change the status of an asset."""
        raise EndpointNotImplementedError()
