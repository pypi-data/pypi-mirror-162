# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['setlist_fm_client']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.23.0,<0.24.0', 'pydantic>=1.9.1,<2.0.0', 'pyhumps>=3.7.1,<4.0.0']

setup_kwargs = {
    'name': 'setlist-fm-client',
    'version': '0.4.0',
    'description': 'a python client for the setlist.fm api',
    'long_description': '[![test](https://github.com/zschumacher/setlist-fm-client/actions/workflows/test.yml/badge.svg)](https://github.com/zschumacher/setlist-fm-client/actions/workflows/test.yml)\n[![PyPI version](https://badge.fury.io/py/setlist-fm-client.svg)](https://badge.fury.io/py/setlist-fm-client)\n[![Documentation Status](https://readthedocs.org/projects/setlist-fm-client/badge/?version=latest)](https://setlist-fm-client.readthedocs.io/en/latest/?badge=latest)\n[![codecov](https://codecov.io/gh/zschumacher/setlist-fm-client/branch/main/graph/badge.svg?token=ZNUE1K18VD)](https://codecov.io/gh/zschumacher/setlist-fm-client)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/setlist-fm-client)\n\n# setlist-fm-client\n`setlist-fm-client` is a python client for the  [setlist.fm REST API](https://api.setlist.fm/docs/1.0/index.html).\n\n## Installation\n\n### pip\n```console\npip install setlist-fm-client\n```\n\n### poetry\n\n```console\npoetry add setlist-fm-client\n```\n\n## Help\nSee the [documentation](https://setlist-fm-client.readthedocs.io/en/latest/) for more details.\n\n\n## Authentication\nIn order to authenticate to the setlist.fm REST API, you must [apply for an API key](https://www.setlist.fm/settings/api) \n(link for logged-in users only) - if you\'re not registered user yet, then \n[register first](https://www.setlist.fm/signup) (it\'s free).\n\nOnce you have your key, you can use it in the *setlist-fm-client* by setting the `SETLIST_FM_API_KEY` environment \nvariable or by passing `api_key="xxx"` as a kwarg to any function (see [docs]()).\n\n\n## Simple Example\n*setlist-fm-client* is extremely easy to use.  By setting `serialize=True`, you get a pydantic model returned to you instead of\na `httpx.Response` object.\n\nBelow are examples of what the code looks like for both the sync and async apis.\n\n### sync\n```python\nimport setlist_fm_client\n\nsetlists = setlist_fm_client.get_artist_setlists(\n    "0bfba3d3-6a04-4779-bb0a-df07df5b0558", api_key="xxx", serialize=True\n)\nprint(setlists)\n```\n\n### async\n```python\nimport asyncio \n\nimport setlist_fm_client\n\nasync def main():\n    setlists = await setlist_fm_client.get_artist_setlists(\n        "0bfba3d3-6a04-4779-bb0a-df07df5b0558", api_key="xxx", serialize=True\n    )\n    print(setlists)\n\nasyncio.run(main())\n```\n\nThis will give you an `ArtistSetListResponse` object.\n\n\n## Buy me a coffee\nIf you find this project useful, consider buying me a coffee! \n\n<a href="https://www.buymeacoffee.com/zachschumacher" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>\n\n\n',
    'author': 'Zach Schumacher',
    'author_email': 'zschu15@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
