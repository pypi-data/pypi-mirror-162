# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['bq_easy_zfullio']

package_data = \
{'': ['*']}

install_requires = \
['google-cloud-bigquery>=3,<4']

setup_kwargs = {
    'name': 'bq-easy-zfullio',
    'version': '0.0.1',
    'description': 'Простой экспорт из Pandas Dataframe в BQ',
    'long_description': '# BQ Easy\n\nПростой экспорт из Pandas Dataframe в BQ',
    'author': 'viktor',
    'author_email': 'vi.dave@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
