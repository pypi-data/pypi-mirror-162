# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['inaturalist']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.6.0', 'minio>=7.1.10', 'python-dotenv>=0.20.0', 'requests>=2.28.1']

entry_points = \
{'console_scripts': ['inat = inaturalist:cli.main',
                     'inaturalist = inaturalist:cli.main']}

setup_kwargs = {
    'name': 'inaturalist',
    'version': '0.1.5',
    'description': 'iNaturalist Photo Scraper',
    'long_description': '# iNaturalist Photo Scraper\n\n[![Supported Python versions](https://img.shields.io/badge/Python-%3E=3.7-blue.svg)](https://www.python.org/downloads/) [![PEP8](https://img.shields.io/badge/Code%20style-PEP%208-orange.svg)](https://www.python.org/dev/peps/pep-0008/) \n\n\n## Requirements\n- 🐍 [python>=3.7](https://www.python.org/downloads/)\n\n\n## ⬇️ Installation\n\n```sh\npip install inaturalist\n```\n\n## ⌨️ Usage\n\n```\nusage: inat [-h] -t TAXON_ID [-o OUTPUT_DIR] [-p RESUME_FROM_PAGE] [-P STOP_AT_PAGE] [-u RESUME_FROM_UUID_INDEX] [--upload-to-s3] [-O]\n            [-r RESULTS_PER_PAGE] [-s START_YEAR] [-e END_YEAR] [-Y] [--get-current-progress]\n\noptions:\n  -h, --help            show this help message and exit\n  -t TAXON_ID, --taxon-id TAXON_ID\n                        Taxon id\n  -o OUTPUT_DIR, --output-dir OUTPUT_DIR\n                        Output directory\n  -p RESUME_FROM_PAGE, --resume-from-page RESUME_FROM_PAGE\n                        Page to resume from\n  -P STOP_AT_PAGE, --stop-at-page STOP_AT_PAGE\n                        Page to stop at\n  -u RESUME_FROM_UUID_INDEX, --resume-from-uuid-index RESUME_FROM_UUID_INDEX\n                        UUID index to resume from\n  --upload-to-s3        Upload to a S3-compatible bucket\n  -O, --one-page-only   Terminate after completing a single page\n  -r RESULTS_PER_PAGE, --results-per-page RESULTS_PER_PAGE\n                        Number of results per page\n  -s START_YEAR, --start-year START_YEAR\n                        Year to start from (only relevant when number of observations > 10,000)\n  -e END_YEAR, --end-year END_YEAR\n                        Year to stop at (only relevant when number of observations > 10,000)\n  -Y, --one-year-only   Terminate after completing a single year\n  --get-current-progress\n                        Get current progress\n```\n',
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
