"""
Module for handling the Device Code flow with MSAL and credential refresh.
"""
import os
import warnings
import webbrowser
from typing import Dict, List, Optional

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
        headless: Optional[bool] = None,
    ):
        """
        .. versionadded:: 0.2.0 headless
        .. versionadded:: 0.6.0 MSAL_REQUESTS_AUTH_HEADLESS environment variable

        Parameters
        ----------
        client: msal.PublicClientApplication
            The MSAL client to use to get tokens.
        scopes: List[str]
            List of scopes to get token for.
        headless: bool, optional
            If None (default), it will check the MSAL_REQUESTS_AUTH_HEADLESS environment
            variable and default to False if it is not found.
            If False, it will open a webbrowser and copy the code to the clipboard.
            If True, it will skip automatically opening webbrowser and copying to clipboard.
        """
        super().__init__(client, scopes)
        headless_default = bool(os.getenv("MSAL_REQUESTS_AUTH_HEADLESS", False))
        self._headless = headless_default if headless is None else headless

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
            try:
                pyperclip.copy(flow["user_code"])
                webbrowser.open(flow["verification_uri"])
            except Exception as error:  # pylint: disable=broad-exception-caught
                warnings.warn(
                    "Error encountered while copying code to clipboard "
                    f"and opening a webbrowser ({error})."
                    "To hide this message, set headless=True "
                    "or set the MSAL_REQUESTS_AUTH_HEADLESS "
                    "environment variable to 'true'."
                )
        return self.client.acquire_token_by_device_flow(flow)
