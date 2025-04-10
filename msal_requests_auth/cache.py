"""
Based on:
https://msal-python.readthedocs.io/en/latest/#msal.SerializableTokenCache
"""
import os
import warnings
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, overload

from msal import SerializableTokenCache
from platformdirs import user_cache_dir


class _BaseTokenCache(ABC, SerializableTokenCache):
    """
    Base class for a token cache
    """

    @abstractmethod
    def write_cache(self) -> None:
        """
        Write cache if needed.
        """
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.write_cache()


class NullCache(_BaseTokenCache):
    """
    This cache doesn't write anywhere.
    It is used as a backup cache in case others are not enabled.

    .. versionadded:: 0.9.0

    """

    def write_cache(self) -> None:
        pass


class SimpleTokenCache(_BaseTokenCache):
    """
    Provides a simple token cache for users to
    persist the cache across sessions.

    .. warning:: Simple token cache is insecure. It is recommended to use KeyringTokenCache instead.

    .. versionadded:: 0.4.0

    """

    def __init__(self, cache_file: Union[str, os.PathLike, None] = None) -> None:
        """
        Parameters
        ----------
        cache_file: Union[str, os.PathLike, None], optional
            Path to the token cache fike. If not provided,
            it will store one for you in the user cache directory.
        """
        super().__init__()
        if cache_file is None:
            self.cache_file = Path(
                user_cache_dir("msal-requests-auth", appauthor=False), "token-cache.bin"
            )
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            self.cache_file = Path(cache_file)

        if self.cache_file.exists():
            self.deserialize(self.cache_file.read_text())

    def write_cache(self) -> None:
        """
        Write cache to disk if needed.
        """
        if self.has_state_changed:
            self.cache_file.write_text(self.serialize())


def _import_keyring():
    """
    Method to import keyring with error message
    """
    try:
        import keyring
    except ModuleNotFoundError as error:
        raise ModuleNotFoundError(
            "Please install msal_requests_auth with the "
            "'keyring' extra: msal_requests_auth[keyring]."
        ) from error
    return keyring


class KeyringTokenCache(_BaseTokenCache):
    """
    Provides a token cache for users to
    persist the cache across sessions using keyring.

    .. versionadded:: 0.7.0

    .. note:: Requires keyring to be installed. The 'keyring'
              extra can be used for that (msal_requests_auth[keyring]).
    """

    def __init__(self) -> None:
        super().__init__()
        token_cache = _import_keyring().get_password("__msal_requests_auth__", "token")
        if token_cache is not None:
            self.deserialize(token_cache)

    def write_cache(self) -> None:
        """
        Write cache to keyring if needed.
        """
        if not self.has_state_changed:
            return

        try:
            _import_keyring().set_password(
                "__msal_requests_auth__", "token", self.serialize()
            )
        except Exception as error:  # pylint: disable=broad-exception-caught
            # some windows machines have issues writing to keyring
            # win32ctypes.pywin32.pywintypes.error: (1783, 'CredWrite', 'The stub received bad data')
            if getattr(error, "winerror", None) != 1783:
                raise
            warnings.warn(
                f"Token cache skipped due to error writing to keyring. Error: {error}"
            )


class EnvironmentTokenCache(_BaseTokenCache):
    """
    Provides a token cache for users to initialize and persist the cache using environment variables within a Python session.

    .. warning:: Environment token cache is insecure. It is recommended to use KeyringTokenCache instead.

    .. versionadded:: 0.9.0

    """

    _environment_variable = "__msal_requests_auth_cache__"

    def __init__(self) -> None:
        super().__init__()
        token_cache = os.getenv(self._environment_variable)
        if token_cache:
            self.deserialize(token_cache)

    def write_cache(self) -> None:
        """
        Write cache to environment variable if needed.
        """
        if self.has_state_changed:
            os.environ[self._environment_variable] = self.serialize()


@overload
def get_token_cache() -> Union[KeyringTokenCache, NullCache]:
    ...


@overload
def get_token_cache(
    allow_environment_token_cache: bool = True,
) -> Union[KeyringTokenCache, NullCache, EnvironmentTokenCache]:
    ...


def get_token_cache(
    allow_environment_token_cache: bool = False,
) -> Union[KeyringTokenCache, NullCache, EnvironmentTokenCache]:
    """
    Retrieve the token cache based on user set up.

    Order of choosing cache:

    - Use EnvironmentTokenCache if allowed and the environment variable exists.
    - Use KeyringTokenCache if enabled.
    - Use NullCache.

    .. versionadded:: 0.9.0
    """
    if allow_environment_token_cache and os.getenv(
        EnvironmentTokenCache._environment_variable
    ):
        return EnvironmentTokenCache()
    try:
        return KeyringTokenCache()
    except _import_keyring().errors.NoKeyringError:
        warnings.warn(
            "Keyring backend not detected. Not caching tokens. "
            "For more details: https://pypi.org/project/keyring/"
        )
    return NullCache()
