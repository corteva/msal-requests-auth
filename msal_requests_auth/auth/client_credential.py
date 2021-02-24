"""
Module for handling the Device Code flow with MSAL and credential refresh.
"""
from msal import ConfidentialClientApplication

from .base_auth_client import BaseMSALRefreshAuth


class ClientCredentialAuth(BaseMSALRefreshAuth):
    """
    Auth class for the client credential flow with MSAL
    """

    _client_class = ConfidentialClientApplication

    def _get_access_token(self):
        """
        Retrieve access token from MSAL using client credential flow.

        Based on: https://docs.microsoft.com/en-us/azure/active-directory/develop/scenario-daemon-acquire-token?tabs=python#acquiretokenforclient-api
        """
        result = self.client.acquire_token_silent(scopes=self.scopes, account=None)
        if not result:
            # "No suitable token exists in cache. Get a new one from AAD
            result = self.client.acquire_token_for_client(scopes=self.scopes)
        return result
