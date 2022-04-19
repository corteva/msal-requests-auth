"""
Handles refresing tokens with MSAL.
"""
from abc import abstractmethod
from typing import Dict, List, Type

import msal
import requests

from msal_requests_auth.exceptions import AuthenticationError


class BaseMSALRefreshAuth(requests.auth.AuthBase):
    """
    Auth class for the device code flow with MSAL
    """

    def __init__(self, client: msal.ClientApplication, scopes: List[str]):
        """
        Parameters
        ----------
        client: msal.ClientApplication
            The MSAL client to use to get tokens.
        scopes: List[str]
            List of scopes to get token for.
        """
        if not isinstance(client, self._client_class):
            raise ValueError(
                f"Invalid client provided. Must be a {self._client_class.__name__}."
            )
        self.client = client
        self.scopes = scopes

    @property
    @abstractmethod
    def _client_class(self) -> Type[msal.ClientApplication]:
        """
        This is the expected type of the client class.
        """
        raise NotImplementedError

    def __call__(
        self, input_request: requests.PreparedRequest
    ) -> requests.PreparedRequest:
        """
        Adds the token to the authorization header.
        """
        token = self._get_access_token()
        if "access_token" not in token:
            error = token.get("error")
            description = token.get("error_description")
            raise AuthenticationError(
                f"Unable to get token. Error: {error} (Details: {description})."
            )
        input_request.headers[
            "Authorization"
        ] = f"{token['token_type']} {token['access_token']}"
        return input_request

    @abstractmethod
    def _get_access_token(self) -> Dict[str, str]:
        """
        Retrieves the token dictionary from Azure AD.

        Returns
        -------
        dict
        """
        raise NotImplementedError
