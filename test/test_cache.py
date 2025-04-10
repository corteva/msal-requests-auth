import os
from unittest.mock import patch

import pytest

from msal_requests_auth.cache import (
    EnvironmentTokenCache,
    KeyringTokenCache,
    NullCache,
    SimpleTokenCache,
    get_token_cache,
)


@patch("msal_requests_auth.cache.user_cache_dir")
@patch("msal_requests_auth.cache.SimpleTokenCache.serialize")
def test_simple_token_cache(serialize_mock, user_cache_dir_mock, tmp_path):
    serialize_mock.return_value = "TEST"
    user_cache_dir_mock.return_value = str(tmp_path / "msal-requests-auth")
    with SimpleTokenCache() as cache:
        cache.has_state_changed = True
    assert cache.cache_file.read_text() == "TEST"
    user_cache_dir_mock.assert_called_with("msal-requests-auth", appauthor=False)
    assert cache.cache_file == tmp_path / "msal-requests-auth" / "token-cache.bin"
    assert (tmp_path / "msal-requests-auth").exists()


@patch("msal_requests_auth.cache.user_cache_dir")
@patch("msal_requests_auth.cache.SimpleTokenCache.serialize")
def test_simple_token_cache__write_cache(serialize_mock, user_cache_dir_mock, tmp_path):
    serialize_mock.return_value = "TEST"
    user_cache_dir_mock.return_value = str(tmp_path / "msal-requests-auth")
    cache = SimpleTokenCache()
    cache.write_cache()
    assert not cache.cache_file.exists()
    cache.has_state_changed = True
    cache.write_cache()
    assert cache.cache_file.read_text() == "TEST"


@patch("msal_requests_auth.cache.user_cache_dir")
def test_simple_token_cache__custom_path(user_cache_dir_mock, tmp_path):
    test_file = tmp_path / "test.bin"
    cache = SimpleTokenCache(test_file)
    user_cache_dir_mock.assert_not_called()
    assert cache.cache_file == test_file


@patch("msal_requests_auth.cache.user_cache_dir")
@patch("msal_requests_auth.cache.SimpleTokenCache.deserialize")
def test_simple_token_cache__deserialize(
    deserialize_mock, user_cache_dir_mock, tmp_path
):
    test_file = tmp_path / "test.bin"
    test_file.write_text("TEST")
    cache = SimpleTokenCache(test_file)
    deserialize_mock.assert_called_with("TEST")
    user_cache_dir_mock.assert_not_called()
    assert cache.cache_file == test_file


@patch("msal_requests_auth.cache._import_keyring")
@patch("msal_requests_auth.cache.KeyringTokenCache.serialize")
def test_keyring_token_cache(serialize_mock, keyring_mock):
    serialize_mock.return_value = "TEST"
    keyring_mock.return_value.get_password.return_value = None
    with KeyringTokenCache() as cache:
        cache.has_state_changed = True
    keyring_mock.return_value.get_password.assert_called_with(
        "__msal_requests_auth__", "token"
    )
    keyring_mock.return_value.set_password.assert_called_with(
        "__msal_requests_auth__", "token", "TEST"
    )


@patch("msal_requests_auth.cache._import_keyring")
@patch("msal_requests_auth.cache.KeyringTokenCache.serialize")
def test_keyring_token_cache__write_cache(serialize_mock, keyring_mock):
    serialize_mock.return_value = "TEST"
    keyring_mock.return_value.get_password.return_value = None
    cache = KeyringTokenCache()
    keyring_mock.return_value.get_password.assert_called_with(
        "__msal_requests_auth__", "token"
    )
    cache.write_cache()
    keyring_mock.return_value.set_password.assert_not_called()
    cache.has_state_changed = True
    cache.write_cache()
    keyring_mock.return_value.set_password.assert_called_with(
        "__msal_requests_auth__", "token", "TEST"
    )


@patch("msal_requests_auth.cache._import_keyring")
@patch("msal_requests_auth.cache.KeyringTokenCache.deserialize")
def test_keyring_token_cache__deserialize(deserialize_mock, keyring_mock):
    keyring_mock.return_value.get_password.return_value = "TEST"
    KeyringTokenCache()
    deserialize_mock.assert_called_with("TEST")


@patch("msal_requests_auth.cache._import_keyring")
@patch("msal_requests_auth.cache.KeyringTokenCache.serialize")
def test_keyring_token_cache__write_cache__windows_error(serialize_mock, keyring_mock):
    class MyException(Exception):
        def __init__(self, *args, **kwargs) -> None:
            self.winerror = 1783
            super().__init__(*args, **kwargs)

    keyring_mock.return_value.set_password.side_effect = MyException

    serialize_mock.return_value = "TEST"
    keyring_mock.return_value.get_password.return_value = None
    with KeyringTokenCache() as cache:
        pass
    keyring_mock.return_value.get_password.assert_called_with(
        "__msal_requests_auth__", "token"
    )
    keyring_mock.return_value.set_password.assert_not_called()
    cache.has_state_changed = True
    with pytest.warns(match="Token cache skipped due to error writing to keyring"):
        with KeyringTokenCache() as cache:
            cache.has_state_changed = True
    keyring_mock.return_value.set_password.assert_called_with(
        "__msal_requests_auth__", "token", "TEST"
    )


@patch("msal_requests_auth.cache._import_keyring")
@patch("msal_requests_auth.cache.KeyringTokenCache.serialize")
def test_keyring_token_cache__write_cache__error(serialize_mock, keyring_mock):
    keyring_mock.return_value.set_password.side_effect = RuntimeError
    serialize_mock.return_value = "TEST"
    keyring_mock.return_value.get_password.return_value = None
    with KeyringTokenCache() as cache:
        pass
    keyring_mock.return_value.get_password.assert_called_with(
        "__msal_requests_auth__", "token"
    )
    keyring_mock.return_value.set_password.assert_not_called()
    with pytest.raises(RuntimeError):
        with KeyringTokenCache() as cache:
            cache.has_state_changed = True
    keyring_mock.return_value.set_password.assert_called_with(
        "__msal_requests_auth__", "token", "TEST"
    )


def test_null_cache():
    with NullCache() as cache:
        cache.has_state_changed = True


@patch.dict(os.environ, {}, clear=True)
@patch("msal_requests_auth.cache.EnvironmentTokenCache.deserialize")
@patch("msal_requests_auth.cache.EnvironmentTokenCache.serialize")
def test_environment_token_cache(serialize_mock, deserialize_mock):
    serialize_mock.return_value = "INPUT FROM CACHE"
    with EnvironmentTokenCache() as cache:
        cache.has_state_changed = True
    assert os.environ == {"__msal_requests_auth_cache__": "INPUT FROM CACHE"}
    deserialize_mock.assert_not_called()


@patch.dict(os.environ, {"__msal_requests_auth_cache__": "INPUT"}, clear=True)
@patch("msal_requests_auth.cache.EnvironmentTokenCache.deserialize")
@patch("msal_requests_auth.cache.EnvironmentTokenCache.serialize")
def test_environment_token_cache__initialized(serialize_mock, deserialize_mock):
    serialize_mock.return_value = "INPUT FROM CACHE"
    with EnvironmentTokenCache() as cache:
        assert os.environ == {"__msal_requests_auth_cache__": "INPUT"}
        cache.has_state_changed = True
    assert os.environ == {"__msal_requests_auth_cache__": "INPUT FROM CACHE"}
    deserialize_mock.assert_called_once_with("INPUT")


@patch.dict(os.environ, {"__msal_requests_auth_cache__": "INPUT"}, clear=True)
@patch("msal_requests_auth.cache._import_keyring")
def test_get_token_cache__keyring(keyring_mock):
    class NoKeyringError(Exception):
        pass

    keyring_mock.return_value.get_password.return_value = None
    keyring_mock.return_value.errors.NoKeyringError = NoKeyringError
    assert isinstance(get_token_cache(), KeyringTokenCache)


@patch.dict(os.environ, {}, clear=True)
@patch("msal_requests_auth.cache._import_keyring")
def test_get_token_cache__keyring__env_enabled(keyring_mock):
    class NoKeyringError(Exception):
        pass

    keyring_mock.return_value.get_password.return_value = None
    keyring_mock.return_value.errors.NoKeyringError = NoKeyringError
    assert isinstance(
        get_token_cache(allow_environment_token_cache=True), KeyringTokenCache
    )


@patch.dict(os.environ, {"__msal_requests_auth_cache__": "INPUT"}, clear=True)
@patch("msal_requests_auth.cache._import_keyring")
def test_get_token_cache__null(keyring_mock):
    class NoKeyringError(Exception):
        pass

    keyring_mock.return_value.get_password.side_effect = NoKeyringError
    keyring_mock.return_value.errors.NoKeyringError = NoKeyringError
    with pytest.warns(UserWarning, match="Keyring backend not detected"):
        assert isinstance(get_token_cache(), NullCache)


@patch.dict(os.environ, {}, clear=True)
@patch("msal_requests_auth.cache._import_keyring")
def test_get_token_cache__null__env_enabled(keyring_mock):
    class NoKeyringError(Exception):
        pass

    keyring_mock.return_value.get_password.side_effect = NoKeyringError
    keyring_mock.return_value.errors.NoKeyringError = NoKeyringError
    with pytest.warns(UserWarning, match="Keyring backend not detected"):
        assert isinstance(
            get_token_cache(allow_environment_token_cache=True), NullCache
        )


@patch.dict(os.environ, {"__msal_requests_auth_cache__": "INPUT"}, clear=True)
@patch("msal_requests_auth.cache.EnvironmentTokenCache.deserialize")
def test_get_token_cache__environment(deserialize_mock):
    assert isinstance(
        get_token_cache(allow_environment_token_cache=True), EnvironmentTokenCache
    )
    deserialize_mock.assert_called_once_with("INPUT")
