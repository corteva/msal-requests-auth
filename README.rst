==================
msal-requests-auth
==================

Authentication using python requests and MSAL. This uses the MSAL cache
for repeated requests.

.. image:: https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square
    :alt: All Contributors
    :target: https://github.com/corteva/msal-requests-auth/blob/master/AUTHORS.rst

.. image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
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


.. highlight:: shell


Usage
-----

Device Code Flow
~~~~~~~~~~~~~~~~

.. note:: This will automatically copy the code to your clipboard and open the browser window for you.

.. code-block:: python

    import requests
    import msal
    from msal_requests_auth.auth import DeviceCodeAuth

    client_id = "<client ID from Azure AD>"
    tenant_id = "<tenant ID from Azure AD>"
    application_id = "<client ID of application you want to get a token for from Azure AD>"
    app = msal.PublicClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}/",
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
    credential_client = msal.ConfidentialClientApplication(
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


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
