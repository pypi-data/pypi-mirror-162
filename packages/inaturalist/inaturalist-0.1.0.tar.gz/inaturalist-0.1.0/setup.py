# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['inaturalist']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.6.0', 'minio>=7.1.10', 'python-dotenv>=0.20.0', 'requests>=2.28.1']

entry_points = \
{'console_scripts': ['inat = inaturalist:cli.main']}

setup_kwargs = {
    'name': 'inaturalist',
    'version': '0.1.0',
    'description': 'iNaturalist Photo Scraper',
    'long_description': '# iNaturalist Photo Scraper\n\n[![Supported Python versions](https://img.shields.io/badge/Python-%3E=3.7-blue.svg)](https://www.python.org/downloads/) [![PEP8](https://img.shields.io/badge/Code%20style-PEP%208-orange.svg)](https://www.python.org/dev/peps/pep-0008/) \n\n\n## Requirements\n- 🐍 [python>=3.7](https://www.python.org/downloads/)\n\n\n## ⬇️ Installation\n\n```sh\npip install inaturalist\n```\n\n## ⌨️ Usage\n\n```\nusage: inat [-h] -t TAXON_ID [-o OUTPUT_DIR] [-s RESUME_FROM_PAGE]\n                  [-e STOP_AT_PAGE] [-u RESUME_FROM_UUID_INDEX]\n                  [--upload-to-s3] [--one-page-only]\n\noptions:\n  -h, --help            show this help message and exit\n  -t TAXON_ID, --taxon-id TAXON_ID\n                        Taxon id\n  -o OUTPUT_DIR, --output-dir OUTPUT_DIR\n                        Output directory\n  -s RESUME_FROM_PAGE, --resume-from-page RESUME_FROM_PAGE\n                        Page to resume from\n  -e STOP_AT_PAGE, --stop-at-page STOP_AT_PAGE\n                        Page to stop at\n  -u RESUME_FROM_UUID_INDEX, --resume-from-uuid-index RESUME_FROM_UUID_INDEX\n                        UUID index to resume from\n  --upload-to-s3        Upload to a S3-compatible bucket\n  --one-page-only       Terminate after completing a single page\n```\n',
    'author': 'Alyetama',
    'author_email': 'malyetama@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
