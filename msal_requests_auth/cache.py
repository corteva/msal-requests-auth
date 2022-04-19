"""
Based on:
https://msal-python.readthedocs.io/en/latest/#msal.SerializableTokenCache
"""
import os
from pathlib import Path
from typing import Union

from appdirs import user_cache_dir
from msal import SerializableTokenCache


class SimpleTokenCache(SerializableTokenCache):
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

    def __del__(self):
        self.write_cache()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.write_cache()
