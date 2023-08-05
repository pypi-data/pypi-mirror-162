"""Initialization file for Olyn SDK for WSGI apps."""

from src.olyn.api import configure


def initialize_olyn(
        api_key: str,
        org_code: str,
        url: str = "https://sandbox.olyn.com"
):
    """Olyn API init method for WSGI Apps."""
    configure(api_key=api_key,
              org_code=org_code,
              url=url)
