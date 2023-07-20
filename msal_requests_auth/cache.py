"""
Based on:
https://msal-python.readthedocs.io/en/latest/#msal.SerializableTokenCache
"""
import os
import warnings
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

from appdirs import user_cache_dir
from msal import SerializableTokenCache


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


class SimpleTokenCache(_BaseTokenCache):
    """
    Provides a simple token cache for users to
    persist the cache across sessions.

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
