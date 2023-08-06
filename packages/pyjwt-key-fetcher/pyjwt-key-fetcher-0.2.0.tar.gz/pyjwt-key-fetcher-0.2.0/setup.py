# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['pyjwt_key_fetcher', 'pyjwt_key_fetcher.tests']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT[crypto]>=2.4.0,<3.0.0',
 'aiocache>=0.11.1,<0.12.0',
 'aiohttp[speedups]>=3.8.1,<4.0.0',
 'cachetools>=5.2.0,<6.0.0']

setup_kwargs = {
    'name': 'pyjwt-key-fetcher',
    'version': '0.2.0',
    'description': 'Async library to fetch JWKs for JWT tokens',
    'long_description': '# pyjwt-key-fetcher\n\n[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/ioxiocom/pyjwt-key-fetcher/Build%20and%20upload%20to%20PyPI)](https://github.com/ioxiocom/pyjwt-key-fetcher/actions/workflows/publish.yaml)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![PyPI](https://img.shields.io/pypi/v/pyjwt-key-fetcher)](https://pypi.org/project/pyjwt-key-fetcher/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyjwt-key-fetcher)](https://pypi.org/project/pyjwt-key-fetcher/)\n[![License: BSD 3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)\n\nAsync library to fetch JWKs for JWT tokens.\n\nThis library is intended to be used together with\n[PyJWT](https://pyjwt.readthedocs.io/en/stable/) to automatically verify keys signed by\nOpenID Connect providers. It retrieves the `iss` (issuer) and the `kid` (key ID) from\nthe JWT, fetches the `.well-known/openid-configuration` from the issuer to find out the\n`jwks_uri` and fetches that to find the right key.\n\nThis should give similar ability to verify keys as for example\n[https://jwt.io/](https://jwt.io/), where you can just paste in a token, and it will\nautomatically reach out and retrieve the key for you.\n\nThe `AsyncKeyFetcher` provided by this library acts as an improved async replacement for\n[PyJWKClient](https://pyjwt.readthedocs.io/en/2.1.0/usage.html#retrieve-rsa-signing-keys-from-a-jwks-endpoint).\n\n## Installation\n\nThe package is available on PyPI:\n\n```bash\npip install pyjwt-key-fetcher\n```\n\n## Usage\n\n### Example\n\n```python\nimport asyncio\n\nimport jwt\n\nfrom pyjwt_key_fetcher import AsyncKeyFetcher\n\n\nasync def main():\n    fetcher = AsyncKeyFetcher()\n    # Token and options copied from\n    # https://pyjwt.readthedocs.io/en/2.1.0/usage.html#retrieve-rsa-signing-keys-from-a-jwks-endpoint\n    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ik5FRTFRVVJCT1RNNE16STVSa0ZETlRZeE9UVTFNRGcyT0Rnd1EwVXpNVGsxUWpZeVJrUkZRdyJ9.eyJpc3MiOiJodHRwczovL2Rldi04N2V2eDlydS5hdXRoMC5jb20vIiwic3ViIjoiYVc0Q2NhNzl4UmVMV1V6MGFFMkg2a0QwTzNjWEJWdENAY2xpZW50cyIsImF1ZCI6Imh0dHBzOi8vZXhwZW5zZXMtYXBpIiwiaWF0IjoxNTcyMDA2OTU0LCJleHAiOjE1NzIwMDY5NjQsImF6cCI6ImFXNENjYTc5eFJlTFdVejBhRTJINmtEME8zY1hCVnRDIiwiZ3R5IjoiY2xpZW50LWNyZWRlbnRpYWxzIn0.PUxE7xn52aTCohGiWoSdMBZGiYAHwE5FYie0Y1qUT68IHSTXwXVd6hn02HTah6epvHHVKA2FqcFZ4GGv5VTHEvYpeggiiZMgbxFrmTEY0csL6VNkX1eaJGcuehwQCRBKRLL3zKmA5IKGy5GeUnIbpPHLHDxr-GXvgFzsdsyWlVQvPX2xjeaQ217r2PtxDeqjlf66UYl6oY6AqNS8DH3iryCvIfCcybRZkc_hdy-6ZMoKT6Piijvk_aXdm7-QQqKJFHLuEqrVSOuBqqiNfVrG27QzAPuPOxvfXTVLXL2jek5meH6n-VWgrBdoMFH93QEszEDowDAEhQPHVs0xj7SIzA"\n    key_entry = await fetcher.get_key(token)\n    token = jwt.decode(\n        jwt=token,\n        options={"verify_exp": False},\n        audience="https://expenses-api",\n        **key_entry\n    )\n    print(token)\n\n\nif __name__ == "__main__":\n    asyncio.run(main())\n```\n\n### Options\n\n#### Limiting issuers\n\nYou can limit the issuers you allow fetching keys from by setting the `valid_issuers`\nwhen creating the `AsyncKeyFetcher`, like this:\n\n```python\nAsyncKeyFetcher(valid_issuers=["https://example.com"])\n```\n\n#### Adjusting caching\n\nThe `AsyncKeyFetcher` will by default cache data for up to 32 different issuers with a\nTTL of 3600 seconds (1 hour) each. This means that in case of key-revocation, the key\nwill be trusted for up to 1 hour after it was removed from the JWKs.\n\nIf a previously unseen kid for an already seen issuer is seen, it will trigger a\nre-fetch of the JWKs, provided they have not been fetched in the past 5 minutes, in\norder to rather quickly react to new keys being published.\n\nThe amount of issuers to cache data for, as well as the cache time for the data can be\nadjusted like this:\n\n```python\nAsyncKeyFetcher(cache_maxsize=10, cache_ttl=2*60*60)\n```\n\nThe minimum interval for checking for new keys can for now not be adjusted.\n\n#### Using your own HTTP Client\n\nThe library ships with a `DefaultHTTPClient` that uses `aiohttp` for fetching the JSON\ndata; the openid-configuration and the jwks. If you want, you can write your own custom\nclient by inheriting from the `HTTPClient`. The only requirement is that it implements\nan async function to fetch JSON from a given URL and return it as a dictionary.\n',
    'author': 'Digital Living International Ltd',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ioxiocom/pyjwt-key-fetcher',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
