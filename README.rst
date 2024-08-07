==================
msal-requests-auth
==================

Authentication using python requests and MSAL. This uses the MSAL cache
for repeated requests.

.. image:: https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square
    :alt: All Contributors
    :target: https://github.com/corteva/msal-requests-auth/blob/master/AUTHORS.rst

.. image:: https://img.shields.io/badge/License-BSD%203--Clause-yellow.svg
    :target: https://github.com/corteva/msal-requests-auth/blob/master/LICENSE

.. image:: https://img.shields.io/pypi/v/msal_requests_auth.svg
    :target: https://pypi.python.org/pypi/msal_requests_auth

.. image:: https://pepy.tech/badge/msal_requests_auth
    :target: https://pepy.tech/project/msal_requests_auth

.. image:: https://img.shields.io/conda/vn/conda-forge/msal_requests_auth.svg
    :target: https://anaconda.org/conda-forge/msal_requests_auth

.. image:: https://github.com/corteva/msal-requests-auth/workflows/Tests/badge.svg
    :target: https://github.com/corteva/msal-requests-auth/actions?query=workflow%3ATests

.. image:: https://codecov.io/gh/corteva/msal-requests-auth/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/corteva/msal-requests-auth

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
    :target: https://github.com/pre-commit/pre-commit

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/python/black


Bugs/Questions
--------------

- Report bugs/feature requests: https://github.com/corteva/msal-requests-auth/issues
- Ask questions: https://github.com/corteva/msal-requests-auth/discussions


Usage
-----

Compatible with:

- `requests <https://requests.readthedocs.io/en/latest/>`_
- `httpx <https://www.python-httpx.org/>`_


Device Code Flow
~~~~~~~~~~~~~~~~

.. note:: By default, `DeviceCodeAuth` copys the code to your clipboard and opens a webbrowser.
          To disable, either set `headless=True` when initializing `DeviceCodeAuth`
          or set the environment variable `MSAL_REQUESTS_AUTH_HEADLESS` to `true`.

- New in version 0.2.0: headless
- New in version 0.6.0: MSAL_REQUESTS_AUTH_HEADLESS environment variable
- New in version 0.7.0: KeyringTokenCache

.. code-block:: python

    import requests
    import msal
    from msal_requests_auth.auth import DeviceCodeAuth
    from msal_requests_auth.cache import KeyringTokenCache

    client_id = "<client ID from Azure AD>"
    tenant_id = "<tenant ID from Azure AD>"
    application_id = "<client ID of application you want to get a token for from Azure AD>"

    with KeyringTokenCache() as token_cache:
        app = msal.PublicClientApplication(
            client_id,
            authority=f"https://login.microsoftonline.com/{tenant_id}/",
            token_cache=token_cache,
        )
        auth = DeviceCodeAuth(
            client=app,
            scopes=[f"{application_id}/.default"],
        )
        response = requests.get(
            endpoint,
            auth=auth,
        )


Client Credentials Flow
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import requests
    import msal
    from msal_requests_auth.auth import ClientCredentialAuth

    client_id = "<client ID from Azure AD>"
    client_secret = "<client secret for client in Azure AD>"
    tenant_id = "<tenant ID from Azure AD>"
    application_id = "<client ID of application you want to get a token for from Azure AD>"
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=(f"https://login.microsoftonline.com/{tenant_id}/"),
        client_credential=client_secret,
    )
    auth = ClientCredentialAuth(
        client=app,
        scopes=[f"{application_id}/.default"],
    )
    response = requests.get(
        endpoint,
        auth=auth,
    )


Installation
------------

To install msal-requests-auth, run this command in your terminal:

.. code-block:: console

    $ python -m pip install msal_requests_auth


If you use conda:

.. code-block:: console

    $ conda install -c conda-forge msal_requests_auth


Windows keyring backend
~~~~~~~~~~~~~~~~~~~~~~~~

The Windows Credential Locker is used by default by ``keyring``.
However, its password length limitations often prevent
storing tokens. An alternative backend may resolve this limitation.
When choosing a backend, be sure you are aware of its limitations.

``keyrings.alt`` is an alternative ``keyring`` backend to consider:

.. code-block:: console

    python -m pip install keyrings.alt


Here is an example of how to set an alternative backend for ``keyring``:

.. code-block:: python

    import keyring

    keyring.core._config_path().parent.mkdir(parents=True, exist_ok=True)
    keyring.core._config_path().write_text(
        "[backend]\ndefault-keyring=keyrings.alt.Windows.EncryptedKeyring"
    )


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
