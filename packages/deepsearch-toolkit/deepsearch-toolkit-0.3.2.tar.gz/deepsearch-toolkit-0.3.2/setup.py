# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deepsearch',
 'deepsearch.core',
 'deepsearch.core.cli',
 'deepsearch.core.client',
 'deepsearch.core.util',
 'deepsearch.cps',
 'deepsearch.cps.apis',
 'deepsearch.cps.apis.kg',
 'deepsearch.cps.apis.kg.create',
 'deepsearch.cps.apis.kg.create.api',
 'deepsearch.cps.apis.kg.create.models',
 'deepsearch.cps.apis.kg.query',
 'deepsearch.cps.apis.kg.query.api',
 'deepsearch.cps.apis.kg.query.models',
 'deepsearch.cps.apis.public',
 'deepsearch.cps.apis.public.api',
 'deepsearch.cps.apis.public.models',
 'deepsearch.cps.apis.user',
 'deepsearch.cps.apis.user.api',
 'deepsearch.cps.apis.user.models',
 'deepsearch.cps.cli',
 'deepsearch.cps.client',
 'deepsearch.cps.client.builders',
 'deepsearch.cps.client.components',
 'deepsearch.cps.client.queries',
 'deepsearch.cps.client.queries.query_tasks',
 'deepsearch.cps.data_indices',
 'deepsearch.cps.ipython',
 'deepsearch.cps.kg',
 'deepsearch.cps.kg.workflow',
 'deepsearch.cps.queries',
 'deepsearch.documents',
 'deepsearch.documents.cli',
 'deepsearch.documents.core',
 'deepsearch.plugins',
 'deepsearch.query',
 'deepsearch.query.cli']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'certifi>=2021.10.8,<2022.0.0',
 'pluggy>=1.0.0,<2.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'python-jose>=3.3.0,<4.0.0',
 'requests>=2.27.1,<3.0.0',
 'six>=1.16.0,<2.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'tqdm>=4.64.0,<5.0.0',
 'typer>=0.4.0,<0.5.0',
 'urllib3>=1.26.8,<2.0.0']

extras_require = \
{'examples': ['ipython-blocking>=0.3.1,<0.4.0',
              'ipywidgets>=7.6.5,<8.0.0',
              'numpy>=1.22.4,<2.0.0',
              'jupyter>=1.0.0,<2.0.0',
              'pandas>=1.4.2,<2.0.0']}

entry_points = \
{'console_scripts': ['deepsearch = deepsearch.cli:app']}

setup_kwargs = {
    'name': 'deepsearch-toolkit',
    'version': '0.3.2',
    'description': 'Interact with the Deep Search platform for new knowledge explorations and discoveries',
    'long_description': '# DeepSearch Toolkit\n\n[![PyPI version](https://img.shields.io/pypi/v/deepsearch-toolkit)](https://pypi.org/project/deepsearch-toolkit/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/deepsearch-toolkit)](https://pypi.org/project/deepsearch-toolkit/)\n[![License MIT](https://img.shields.io/github/license/ds4sd/deepsearch-toolkit)](https://opensource.org/licenses/MIT)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Docs](https://img.shields.io/badge/website-live-brightgreen)](https://ds4sd.github.io/deepsearch-toolkit/)\n\n\n*Interact with the Deep Search platform for new knowledge explorations and discoveries*\n\n\nThe Deep Search Toolkit is a Python SDK allowing a user to interact with the Deep Search platform. The Toolkit provides easy-to-use functionalities for several common processes such as document conversion, graph creation and querying.\n\n\n[Learn about IBM Deep Search](https://ds4sd.github.io/)\n\n\n## Quick links\n\n- [Github repository](https://github.com/ds4sd/deepsearch-toolkit)\n- [Documentation](https://ds4sd.github.io/deepsearch-toolkit/)\n\n\n## Install\n\nUsing `poetry` in your project? Add the toolkit with:\n```console\n$ poetry add deepsearch-toolkit\n```\n\nNew to `poetry`? Visit https://python-poetry.org/ or our [CONTRIBUTING.md](CONTRIBUTING.md) section.\n\n\nUsing `pip`:\n```console\n$ pip install deepsearch-toolkit\n```\n\n### Requirements\n\nPython 3.8+\n\n\n## Start using the toolkit\n\n ```console\n// Login to Deep Search,\n// see https://ds4sd.github.io/deepsearch-toolkit/getting_started/#authentication\n$ deepsearch login\n...\n\n\n// Convert a document\n// for more details, see https://ds4sd.github.io/deepsearch-toolkit/guide/convert_doc/\n$ deepsearch documents convert -p 1234567890abcdefghijklmnopqrstvwyz123456 -u https://arxiv.org/pdf/2206.00785.pdf\nSubmitting input:     : 100%|██████████████████████████████| 1/1 [00:01<00:00,  1.52s/it]\nConverting input:     : 100%|██████████████████████████████| 1/1 [00:33<00:00, 33.80s/it]\nDownloading result:   : 100%|██████████████████████████████| 1/1 [00:01<00:00,  1.11s/it]\nTotal online documents             1\nSuccessfully converted documents   1\n```\n\n\n## Get help and support\n\nPlease feel free to connect with us using the [discussion section](https://github.com/DS4SD/deepsearch-toolkit/discussions).\n\n\n## Contributing\n\nPlease read [Contributing to Deep Search Toolkit](./CONTRIBUTING.md) for details.\n\n\n## References\n\nIf you use `Deep Search` in your projects, please consider citing the following:\n\n```bib\n@software{Deep Search Toolkit,\nauthor = {Deep Search Team},\nmonth = {6},\ntitle = {{Deep Search Toolkit}},\nurl = {https://github.com/DS4SD/deepsearch-toolkit},\nversion = {main},\nyear = {2022}\n}\n```\n\n## License\n\nThe `Deep Search Toolkit` codebase is under MIT license.\nFor individual model usage, please refer to the model licenses found in the original packages.\n',
    'author': 'Michele Dolfi',
    'author_email': 'dol@zurich.ibm.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://ds4sd.github.io/deepsearch-toolkit/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
