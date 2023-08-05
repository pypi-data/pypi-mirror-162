Olyn Python SDK 
===============
[![pypi](https://img.shields.io/pypi/v/stripe.svg)](https://pypi.python.org/pypi/olyn)

The Olyn Python library provides convenient access to the Olyn API from applications written in the Python language. It includes a pre-defined set of classes for API resources that initialize themselves dynamically from API responses which makes it compatible with a wide range of versions of the Olyn API.

## Documentation
See Olyn API Docs for further information related to the overall usage of the API.

See Olyn API Reference for further clarification of each endpoint supported by Olyn API.

## Installation
You don't need this source code unless you want to modify the package. If you just want to use the package, just run:
```shell
pip install --upgrade olyn
```
Install from source with:
```shell
python setup.py install
```
### Requirements
Python 2.7+ or Python 3.4+ (PyPy supported)

## Usage
### Setup
The library needs to be configured with your account's api_key and org_code which is available in your Olyn Dashboard.
To set up the package you can either:
- Call the initialization_app method, this method is suited for WSGI applications.

```python
from src.olyn import initialize_olyn

initialize_olyn(api_key="<YOUR_API_KEY>", org_code="<YOUR_ORG_CODE>")
```
- Call each product class independently, suited for specific cases to be implemented in the flow of the current service.

```python
from src.olyn.api import Api

olyn_client = Api(api_key="<YOUR_API_KEY>", org_code="<YOUR_ORG_CODE>")
response = olyn_client.Assets.get("<olyn_asset_id>")
```
__Note___ By default the package point to `https://sandbox.olyn.com` you can pass the argument at initialization to point out to `https://api.olyn.com`. 
### Error Handling
Unsuccessful requests raise exceptions. The class of the exception will reflect the sort of error that occurred. Please see the Olyn API Reference for a description of the error classes you should handle, and for information on how to inspect these errors.
Olyn Python SDK will handle almost every single type of error the API can return, by raising an exception class with the information contained inside. you can handle these exceptions using try/except development.

````python
from src.olyn import initialize_olyn
from src.olyn.assets import Asset
from src.olyn.errors import NotFoundError

initialize_olyn(api_key="<YOUR_API_KEY>", org_code="<YOUR_ORG_CODE>")

try:
    Asset.get("<asset_id>")
except NotFoundError as err:
    print("ErrorType: ", err.error_type)
print("ErrorCode: ", err.error_code)

````
## Development and Issues
If something can be improved, there are any issues or things to improve or clarify, feel free to reach out opening an issue in this Repository.