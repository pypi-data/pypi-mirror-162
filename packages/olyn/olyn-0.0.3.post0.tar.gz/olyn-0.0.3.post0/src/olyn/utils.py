"""Logic to manipulate post request from Olyn-API."""
from typing import Union


class Utils:
    """Utils to handle and assert statements post Olyn-API request."""

    @classmethod
    # Replace module by Serialized Olyn modules(Asset, Data, Registry, etc ...)
    def is_data_key_from_developer(
            cls,
            module: dict,
            org_code: list[str]  # List of orgs to cross_check.
    ) -> bool:
        """Return True if module is created by one organization within list."""
        if 'createdBy' not in module:
            raise KeyError
        if module['createdBy'] in org_code:
            return True
        else:
            return False

    @classmethod
    # Replace module by Serialized Olyn modules(Asset, Data, Registry, etc ...)
    def get_data_key_in_asset_modules(
            cls,
            modules: list[dict],
            key: str,  # List of orgs to cross_check.
            org_code: Union[list[str], None] = None
    ) -> list:
        """Return module if exists in list  & validated org_code."""
        checked_modules: list = []
        for module in modules:
            if 'createdBy' not in module:
                raise KeyError
            if module['key'] == key:
                checked_modules.append(module)
        if org_code is None:
            return checked_modules
        validated_modules: list = []
        for module in checked_modules:
            if module['createdBy'] in org_code:
                validated_modules.append(module)
        return validated_modules
