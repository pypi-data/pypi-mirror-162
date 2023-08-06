# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['common',
 'common.automl_models',
 'dbt',
 'dbt.adapters.layer_bigquery',
 'dbt.adapters.layer_snowflake',
 'dbt.include.layer_bigquery',
 'dbt.include.layer_snowflake']

package_data = \
{'': ['*']}

install_requires = \
['dbt-core==1.2.0',
 'layer==0.10.2826896527',
 'matplotlib==3.5.1',
 'pandas==1.3.5',
 'scikit-learn==1.0.2',
 'sqlparse>=0.4.2,<0.5.0',
 'typing-extensions>=4.3.0',
 'xgboost==1.5.1']

extras_require = \
{'bigquery': ['dbt-bigquery==1.2.0'], 'snowflake': ['dbt-snowflake==1.2.0']}

setup_kwargs = {
    'name': 'dbt-layer',
    'version': '0.1.2828000257',
    'description': 'The Layer adapter plugin for dbt',
    'long_description': '# Layer dbt Adapter for BigQuery\n\nThis adapter runs dbt builds for ML pipelines with BigQuery as the backing data warehouse.\n',
    'author': 'Layer',
    'author_email': 'info@layer.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.2,<3.11',
}


setup(**setup_kwargs)
