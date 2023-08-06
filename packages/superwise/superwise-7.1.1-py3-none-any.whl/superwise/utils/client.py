""" wrapper for requests class and superwise token handling """
import json

import jwt
import requests
from requests import Response

from superwise import logger
from superwise.config import Config
from superwise.utils.exceptions import *
from superwise.models.validation_error import ValidationError


def token_retry(input_func):
    """
    ### Description:

    A decorator for token retry handling (ie, refresh token if needed)

    """

    def wrapper(*args, **kwargs) -> Response:
        res = input_func(*args, **kwargs)
        if res.status_code == 403:
            args[0].refresh_token()
            res = input_func(*args, **kwargs)
        return res

    return wrapper


class Client:
    """  A Client for http requests, set of wrappers around requests library """

    def __init__(self, client_id, secret, api_host, email=None, password=None):
        """

        ### Args:

        `client_id`:  user client token id (string)

        `secret`: secret token (string)

        `api_host`:  superwise api server host

        `email`: optional email

        `password`: Optional password

        """
        self.client_id = client_id
        self.secret = secret
        self.api_host = api_host
        self.email = email
        self.password = password
        self.token = self.get_token()
        self.tenant_id = self.get_tenant_id(self.token)
        self.logger = logger
        self.headers = self.build_headers()

    def get_tenant_id(self, token) -> str:
        """
        ### Description:

        Get tenant id from JWT token

        ### Args:

        `token`: secret token (string)

        ### Return:

        tenant_id string
        """
        try:
            jwt_payload = jwt.decode(token, "secret", options={"verify_signature": False})
        except:
            raise SuperwiseTokenException("error parsing jwt token: {}".format(token))
        if jwt_payload:
            return jwt_payload.get("tenantId")
        else:
            raise SuperwiseException("error decoding JWT")

    def build_headers(self):
        """
        ### Description:

        ### Return:
        Headers to send (dict)
        """
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.token,
        }

    def refresh_token(self):
        """
        ### Description:

        refresh  bearer token

        ### Return:

        token string
        """
        return self.get_token()

    def get_token(self) -> str:
        """
        ### Description:
        Get bearer token to use in each API call

        ### Return:

        token string
        """

        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.email:
            url = "{}/identity/resources/auth/v1/user".format(Config.AUTH_URL)
            params = {"email": self.email, "password": self.password}
        else:
            params = {"clientId": self.client_id, "secret": self.secret}
            url = "{}/identity/resources/auth/v1/api-token".format(Config.AUTH_URL)
        res = self._post(url, params=params, headers=headers)

        error = False
        token = None
        try:
            token = res.json().get("accessToken")
        except:
            error = True
        if not token or error:
            raise SuperwiseAuthException("Error get or refresh token url={} params={} ".format(url, params))

        return token

    def _post(self, url, params, headers=None) -> Response:
        """
        ### Description:

        Wrapper to requests.post(), with no refresh token handling

        ### Args:

        `url`: url string

        `params`: json paramters to send

        `headers`: headers string

        ### Return:

        Response object (requests package)
        """
        headers = self.headers if not headers else headers
        logger.debug("POST:  {} params: {}".format(url, params))
        res = requests.post(url, json=params, headers=headers)
        return self._check_res(res)

    @token_retry
    def post(self, url, params, headers=None) -> Response:
        """
        ### Description:

        Wrapper to requests.post(), with no refresh token handling

        ### Args:

        `url`: url string

        `params`: json paramters to send

        `headers`: headers string

        ### Return:

        Response object (requests package)
        """
        return self._post(url, params, headers)

    def _check_res(self, res) -> Response:
        """
        ### Description:

        Check response status and raise Exception if error

        ### Args:

        `res`: response object from requests call

        ### Return:

        response object
        """
        if res.status_code == 422:
            try:
                body = json.loads(res.content)
            except Exception as ex:
                raise Exception("error loading json, status code {} text {}".format(res.status_code, res.content))

            ValidationError(http_status_code=res.status_code, http_error_reason=res.reason, body=body)
        if res.status_code in [401, 403]:
            logger.error(f"error {res.status_code} - {res.content}")
            raise SuperwiseAuthException(res.content)
        if res.status_code in [500]:
            logger.error(f"error 500 {res.content}")
            raise SuperWiseInternalServerError(res.content)
        if res.status_code not in [200, 201, 202, 204]:
            logger.error(f"error {res.status_code} - {res.content}")
            raise Exception(res.content)
        return res

    @token_retry
    def get(self, url, query_params=None, headers=None) -> Response:
        """
        ### Description:

        Wrapper to requests.post(), with no refresh token handling

        ### Args:

        `url`: url string

        `query_params`: dictionary of parameters to add as query string

        `headers`: headers dictionary

        ### Return:

        Response object (requests package)
        """
        headers = self.headers if not headers else headers
        logger.debug("GET {} query params: {}".format(url, query_params))
        res = requests.get(url=url, headers=headers, params=query_params)
        return self._check_res(res)

    @token_retry
    def delete(self, url, headers=None) -> Response:
        """
        Wrapper for reuqests.delete(),

        :param idx: id int
        :return: Response object (requests package)
        """

        """
        ### Description:

        Wrapper for reuqests.delete()

        ### Args:

        `url`: url of resource to delete

        ### Return:

        Response object (requests package)
        """

        headers = self.headers if not headers else headers
        logger.debug("DELETE {}".format(url))
        res = requests.delete(url=url, headers=headers)
        return self._check_res(res)

    @token_retry
    def patch(self, url, params, headers=None) -> Response:
        """
        ### Description:

        Wrapper to requests.patch(), with no refresh token handling

        ### Args:

        `url`: url string

        `params`: dictionary of fields to update

        `headers`: headers dictionary

        ### Return:

        Response object (requests package)
        """

        headers = self.headers if not headers else headers
        logger.debug("PATCH {}  params: {} ".format(url, params))
        res = requests.patch(url, json=params, headers=headers)
        return self._check_res(res)

    def build_url(self, path):
        """
        ### Description:

        Build an url for a given path

        ### Args:

        `path`:  relative path, normally declared in each model (subclasses of this class)

        ### Return:

        URL string
        """
        return "https://{}/{}/{}".format(self.api_host, self.tenant_id, path)
