# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['data_job_etl',
 'data_job_etl.config',
 'data_job_etl.data',
 'data_job_etl.load',
 'data_job_etl.transform',
 'data_job_etl.transform.ner_technos']

package_data = \
{'': ['*'],
 'data_job_etl.data': ['model_en/model-best/*',
                       'model_en/model-best/ner/*',
                       'model_en/model-best/tok2vec/*',
                       'model_en/model-best/vocab/*',
                       'model_en/model-last/*',
                       'model_en/model-last/ner/*',
                       'model_en/model-last/tok2vec/*',
                       'model_en/model-last/vocab/*']}

install_requires = \
['SQLAlchemy>=1.4.39,<2.0.0', 'pandas>=1.4.3,<2.0.0', 'psycopg2>=2.9.3,<3.0.0']

setup_kwargs = {
    'name': 'data-job-etl',
    'version': '0.5.0',
    'description': '',
    'long_description': None,
    'author': 'Donor',
    'author_email': 'donorfelita@msn.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
