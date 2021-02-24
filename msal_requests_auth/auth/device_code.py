"""
Module for handling the Device Code flow with MSAL and credential refresh.
"""
import webbrowser

import pyperclip
from msal import PublicClientApplication

from .base_auth_client import BaseMSALRefreshAuth


class DeviceCodeAuth(BaseMSALRefreshAuth):
    """
    Auth class for the device code flow with MSAL
    """

    _client_class = PublicClientApplication

    def _get_access_token(self):
        """
        Retrieve access token from MSAL using device code flow.

        Based on README: https://github.com/AzureAD/microsoft-authentication-library-for-python
        """
        accounts = self.client.get_accounts()
        result = None
        if accounts:
            # use MSAL cache if available
            result = self.client.acquire_token_silent(
                scopes=self.scopes,
                account=accounts[0],
            )
            if result:
                return result
        # "No suitable token exists in cache. Get a new one from AAD
        flow = self.client.initiate_device_flow(
            scopes=self.scopes,
        )
        print(flow["message"])
        # copy code to clipboard
        pyperclip.copy(flow["user_code"])
        webbrowser.open(flow["verification_uri"])
        return self.client.acquire_token_by_device_flow(flow)
