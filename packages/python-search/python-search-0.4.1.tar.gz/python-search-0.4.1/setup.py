# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['python_search',
 'python_search.apps',
 'python_search.data_ui',
 'python_search.datasets',
 'python_search.entry_capture',
 'python_search.events',
 'python_search.infrastructure',
 'python_search.interpreter',
 'python_search.observability',
 'python_search.ranking',
 'python_search.ranking.next_item_predictor',
 'python_search.search_ui',
 'python_search.shortcut']

package_data = \
{'': ['*']}

install_requires = \
['PySimpleGUI>=4.60.1,<5.0.0',
 'PyYAML>=6.0,<7.0',
 'fastapi>=0.79.0,<0.80.0',
 'findspark>=2.0.1,<3.0.0',
 'fire>=0.4.0,<0.5.0',
 'kafka-python>=2.0.2,<3.0.0',
 'matplotlib>=3.5.2,<4.0.0',
 'mlflow>=1.27.0,<2.0.0',
 'msgpack-numpy>=0.4.8,<0.5.0',
 'numpy>=1.23.0,<1.24.0',
 'pandas>=1.4.3,<2.0.0',
 'personal-grimoire==1.6',
 'pydantic>=1.9.1,<2.0.0',
 'pyspark>=3.3.0,<4.0.0',
 'redis>=4.3.4,<5.0.0',
 'sentence-transformers>=2.2.2,<3.0.0',
 'sklearn>=0.0,<0.1',
 'typed-pyspark>=0.0.4,<0.1.0',
 'uvicorn>=0.18.2,<0.19.0',
 'xgboost>=1.6.1,<2.0.0']

entry_points = \
{'console_scripts': ['browser = python_search.apps.browser:main',
                     'clipboard = python_search.apps.clipboard:main',
                     'collect_input = python_search.apps.capture_input:main',
                     'entry_embeddings = '
                     'python_search.ranking.entry_embeddings:main',
                     'next_item_pipeline = '
                     'python_search.ranking.next_item_predictor.pipeline:main',
                     'notify_send = python_search.apps.notification_ui:main',
                     'python_search = python_search.cli:main',
                     'python_search_infra = '
                     'python_search.infrastructure.infrastructure:main',
                     'python_search_webapi = python_search.web_api:main']}

setup_kwargs = {
    'name': 'python-search',
    'version': '0.4.1',
    'description': 'Digitalize everything in python',
    'long_description': None,
    'author': 'Jean Carlo Machado',
    'author_email': 'jean.machado@getyourguide.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
