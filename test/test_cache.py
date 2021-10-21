from unittest.mock import patch

from msal_requests_auth.cache import SimpleTokenCache


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
