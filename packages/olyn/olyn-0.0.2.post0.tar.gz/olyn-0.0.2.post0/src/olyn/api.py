"""Olyn API class handler."""

import json
import os

import urllib3

from src.olyn.errors import ApiError, RequestValidationError, \
    ForbiddenError, UnauthorizedError, NotFoundError, MethodNotAllowedError, \
    ConflictError


class Response:
    def __init__(self, response):
        self.json = json.loads(response.data.decode('utf-8'))
        self.status = response.status


class Api:
    def __init__(self, api_key, org_code, url='https://sandbox.olyn.com'):
        self.client = urllib3.PoolManager()
        self.api_key = api_key
        self.org_code = org_code
        self.default_headers = {'x-api-key': self.api_key or '',
                                'x-org-code': self.org_code or '',
                                'Content-Type': 'application/json'}
        self.api_url = url

    def get(self, url, headers={}):
        response = Response(self.client.request('GET',
                                                f'{self.api_url}/{url}',
                                                headers={
                                                    **self.default_headers,
                                                    **headers
                                                }
                                                ))
        self.__handle_errors__(response)
        return response

    def post(self, url, body, headers={}):
        encoded_data = json.dumps(body).encode('utf-8')
        response = Response(self.client.request('POST',
                                                f'{self.api_url}/{url}',
                                                body=encoded_data,
                                                headers={
                                                    **self.default_headers,
                                                    **headers
                                                }
                                                ))

        self.__handle_errors__(response)
        return response

    def put(self, url, body, headers={}):
        encoded_data = json.dumps(body).encode('utf-8')
        response = Response(self.client.request('PUT',
                                                f'{self.api_url}/{url}',
                                                body=encoded_data,
                                                headers={
                                                    **self.default_headers,
                                                    **headers
                                                }
                                                ))
        self.__handle_errors__(response)
        return response

    @staticmethod
    def __handle_errors__(response):
        if response.status == 400:
            raise RequestValidationError(
                response.json['error']['code'],
                response.json['error']['type']
            )

        if response.status == 401:
            raise UnauthorizedError(
                response.json['error']['code'],
                response.json['error']['type']
            )

        if response.status == 403:
            raise ForbiddenError(
                response.json['error']['code'],
                response.json['error']['type']
            )

        if response.status == 404:
            raise NotFoundError(
                response.json['error']['code'],
                response.json['error']['type']
            )

        if response.status == 405:
            raise MethodNotAllowedError(
                response.json['error']['code'],
                response.json['error']['type']
            )

        if response.status == 409:
            raise ConflictError(
                response.json['error']['code'],
                response.json['error']['type']
            )

        if response.status == 500:
            raise ApiError(
                response.json['error']['code'],
                response.json['error']['type'],
                response.json['error']['traceback']
            )


__api__ = None


def default():
    """Returns default api object and if not present creates a new one
    By default points to developer sandbox
    """
    global __api__
    if __api__ is None:
        try:
            api_key = os.getenv('OLYN_API_KEY')
            org_code = os.getenv('OLYN_ORG_CODE')
        except KeyError:
            raise Exception("Missing required API config values.")

        __api__ = Api(api_key, org_code)

    return __api__


def configure(api_key, org_code, url='https://sandbox.olyn.com'):
    """Create new default api object with given configuration
    """
    global __api__
    __api__ = Api(api_key, org_code, url)
    return __api__
