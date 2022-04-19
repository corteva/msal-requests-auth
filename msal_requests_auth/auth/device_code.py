"""
Module for handling the Device Code flow with MSAL and credential refresh.
"""
import webbrowser
from typing import Dict, List

import pyperclip
from msal import PublicClientApplication

from .base_auth_client import BaseMSALRefreshAuth


class DeviceCodeAuth(BaseMSALRefreshAuth):
    """
    Auth class for the device code flow with MSAL
    """

    _client_class = PublicClientApplication

    def __init__(
        self,
        client: PublicClientApplication,
        scopes: List[str],
        headless: bool = False,
    ):
        """
        .. versionadded:: 0.2.0 headless

        Parameters
        ----------
        client: msal.PublicClientApplication
            The MSAL client to use to get tokens.
        scopes: List[str]
            List of scopes to get token for.
        headless: bool, default=False
            If True, will skip automatically opening webbrowser and copying to clipboard.
        """
        super().__init__(client, scopes)
        self._headless = headless

    def _get_access_token(self) -> Dict[str, str]:
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
        if not self._headless:
            # copy code to clipboard
            pyperclip.copy(flow["user_code"])
            webbrowser.open(flow["verification_uri"])
        return self.client.acquire_token_by_device_flow(flow)
