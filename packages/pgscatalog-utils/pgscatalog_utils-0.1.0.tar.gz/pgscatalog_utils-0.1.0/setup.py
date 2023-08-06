# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pgscatalog_utils',
 'pgscatalog_utils.download',
 'pgscatalog_utils.match',
 'pgscatalog_utils.scorefile']

package_data = \
{'': ['*']}

install_requires = \
['jq>=1.2.2,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'polars==0.13.5',
 'pyliftover>=0.4,<0.5',
 'requests>=2.28.1,<3.0.0']

entry_points = \
{'console_scripts': ['combine_scorefiles = '
                     'pgscatalog_utils.scorefile.combine_scorefiles:combine_scorefiles',
                     'download_scorefiles = '
                     'pgscatalog_utils.download.download_scorefile:download_scorefile',
                     'match_variants = '
                     'pgscatalog_utils.match.match_variants:match_variants']}

setup_kwargs = {
    'name': 'pgscatalog-utils',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Benjamin Wingfield',
    'author_email': 'bwingfield@ebi.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
