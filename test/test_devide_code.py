from unittest.mock import MagicMock, patch

import pytest

from msal_requests_auth.auth import DeviceCodeAuth


@patch("msal.PublicClientApplication", autospec=True)
@patch("msal_requests_auth.auth.device_code.webbrowser")
@patch("msal_requests_auth.auth.device_code.pyperclip")
def test_device_code_auth__no_accounts(pyperclip_patch, webbrowser_patch, pca_mock):
    pca_mock.get_accounts.return_value = None
    pca_mock.initiate_device_flow.return_value = {
        "message": "TEST MESSAGE",
        "verification_uri": "TEST URL",
        "user_code": "TEST CODE",
    }
    pca_mock.acquire_token_by_device_flow.return_value = {
        "token_type": "Bearer",
        "access_token": "TEST TOKEN",
    }
    request_mock = MagicMock()
    request_mock.headers = {}
    returned_request = DeviceCodeAuth(client=pca_mock, scopes=["TEST SCOPE"])(
        request_mock
    )
    pca_mock.acquire_token_silent.assert_not_called()
    pca_mock.initiate_device_flow.assert_called_with(scopes=["TEST SCOPE"])
    pca_mock.acquire_token_by_device_flow.assert_called_with(
        {
            "message": "TEST MESSAGE",
            "verification_uri": "TEST URL",
            "user_code": "TEST CODE",
        }
    )

    assert returned_request.headers == {"Authorization": "Bearer TEST TOKEN"}
    pyperclip_patch.copy.assert_called_with("TEST CODE")
    webbrowser_patch.open.assert_called_with("TEST URL")


@patch("msal.PublicClientApplication", autospec=True)
@patch("msal_requests_auth.auth.device_code.webbrowser")
@patch("msal_requests_auth.auth.device_code.pyperclip")
def test_device_code_auth__no_accounts__unable_to_get_token(
    pyperclip_patch, webbrowser_patch, pca_mock
):
    pca_mock.get_accounts.return_value = None
    pca_mock.initiate_device_flow.return_value = {
        "message": "TEST MESSAGE",
        "verification_uri": "TEST URL",
        "user_code": "TEST CODE",
    }
    pca_mock.acquire_token_by_device_flow.return_value = {
        "error": "BAD REQUEST",
        "error_description": "Request to get token was bad.",
    }
    request_mock = MagicMock()
    request_mock.headers = {}
    with pytest.raises(
        RuntimeError,
        match=(
            r"Unable to get token\. Error: BAD REQUEST "
            r"\(Details: Request to get token was bad\.\)\."
        ),
    ):
        DeviceCodeAuth(client=pca_mock, scopes=["TEST SCOPE"])(request_mock)
    pca_mock.acquire_token_silent.assert_not_called()
    pca_mock.initiate_device_flow.assert_called_with(scopes=["TEST SCOPE"])
    pca_mock.acquire_token_by_device_flow.assert_called_with(
        {
            "message": "TEST MESSAGE",
            "verification_uri": "TEST URL",
            "user_code": "TEST CODE",
        }
    )
    webbrowser_patch.open.assert_called_with("TEST URL")
    pyperclip_patch.copy.assert_called_with("TEST CODE")


@patch("msal.PublicClientApplication", autospec=True)
@patch("msal_requests_auth.auth.device_code.webbrowser")
@patch("msal_requests_auth.auth.device_code.pyperclip")
def test_device_code_auth__invalid_accounts(
    pyperclip_patch, webbrowser_patch, pca_mock
):
    pca_mock.get_accounts.return_value = [{"account": "TEST ACCOUNT"}]
    pca_mock.acquire_token_silent.return_value = None
    pca_mock.initiate_device_flow.return_value = {
        "message": "TEST MESSAGE",
        "verification_uri": "TEST URL",
        "user_code": "TEST CODE",
    }
    pca_mock.acquire_token_by_device_flow.return_value = {
        "token_type": "Bearer",
        "access_token": "TEST TOKEN",
    }
    request_mock = MagicMock()
    request_mock.headers = {}
    returned_request = DeviceCodeAuth(client=pca_mock, scopes=["TEST SCOPE"])(
        request_mock
    )
    pca_mock.acquire_token_silent.assert_called_with(
        scopes=["TEST SCOPE"], account={"account": "TEST ACCOUNT"}
    )
    pca_mock.initiate_device_flow.assert_called_with(scopes=["TEST SCOPE"])
    pca_mock.acquire_token_by_device_flow.assert_called_with(
        {
            "message": "TEST MESSAGE",
            "verification_uri": "TEST URL",
            "user_code": "TEST CODE",
        }
    )

    assert returned_request.headers == {"Authorization": "Bearer TEST TOKEN"}

    webbrowser_patch.open.assert_called_with("TEST URL")
    pyperclip_patch.copy.assert_called_with("TEST CODE")


@patch("msal.PublicClientApplication", autospec=True)
@patch("msal_requests_auth.auth.device_code.webbrowser")
@patch("msal_requests_auth.auth.device_code.pyperclip")
def test_device_code_auth__accounts(pyperclip_patch, webbrowser_patch, pca_mock):
    pca_mock.get_accounts.return_value = [{"account": "TEST ACCOUNT"}]
    pca_mock.acquire_token_silent.return_value = {
        "token_type": "Bearer",
        "access_token": "TEST TOKEN",
        "user_code": "TEST CODE",
    }
    request_mock = MagicMock()
    request_mock.headers = {}
    returned_request = DeviceCodeAuth(client=pca_mock, scopes=["TEST SCOPE"])(
        request_mock
    )
    pca_mock.acquire_token_silent.assert_called_with(
        scopes=["TEST SCOPE"], account={"account": "TEST ACCOUNT"}
    )
    pca_mock.initiate_device_flow.assert_not_called()
    pca_mock.acquire_token_by_device_flow.assert_not_called()

    assert returned_request.headers == {"Authorization": "Bearer TEST TOKEN"}
    webbrowser_patch.open.assert_not_called()
    pyperclip_patch.copy.assert_not_called()
