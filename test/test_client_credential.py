from unittest.mock import MagicMock, patch

import pytest

from msal_requests_auth.auth import ClientCredentialAuth


@patch("msal.ConfidentialClientApplication", autospec=True)
def test_client_credential_auth__no_cache(cca_mock):
    cca_mock.acquire_token_silent.return_value = None
    cca_mock.acquire_token_for_client.return_value = {
        "token_type": "Bearer",
        "access_token": "TEST TOKEN",
    }
    request_mock = MagicMock()
    request_mock.headers = {}
    returned_request = ClientCredentialAuth(client=cca_mock, scopes=["TEST SCOPE"])(
        request_mock
    )
    cca_mock.acquire_token_silent.assert_called_with(
        scopes=["TEST SCOPE"], account=None
    )
    cca_mock.acquire_token_for_client.assert_called_with(scopes=["TEST SCOPE"])

    assert returned_request.headers == {"Authorization": "Bearer TEST TOKEN"}


@patch("msal.ConfidentialClientApplication", autospec=True)
def test_client_credential_auth__unable_to_get_token(cca_mock):
    cca_mock.acquire_token_silent.return_value = None
    cca_mock.acquire_token_for_client.return_value = {
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
        ClientCredentialAuth(client=cca_mock, scopes=["TEST SCOPE"])(request_mock)

    cca_mock.acquire_token_silent.assert_called_with(
        scopes=["TEST SCOPE"], account=None
    )
    cca_mock.acquire_token_for_client.assert_called_with(scopes=["TEST SCOPE"])


@patch("msal.ConfidentialClientApplication", autospec=True)
def test_client_credential_auth__cache(cca_mock):
    cca_mock.acquire_token_silent.return_value = {
        "token_type": "Bearer",
        "access_token": "TEST TOKEN",
    }
    request_mock = MagicMock()
    request_mock.headers = {}
    returned_request = ClientCredentialAuth(client=cca_mock, scopes=["TEST SCOPE"])(
        request_mock
    )
    cca_mock.acquire_token_silent.assert_called_with(
        scopes=["TEST SCOPE"], account=None
    )
    cca_mock.acquire_token_for_client.assert_not_called()

    assert returned_request.headers == {"Authorization": "Bearer TEST TOKEN"}
