# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sayn',
 'sayn.core',
 'sayn.database',
 'sayn.logging',
 'sayn.scaffolding',
 'sayn.scaffolding.data.init_project.python',
 'sayn.tasks',
 'sayn.utils']

package_data = \
{'': ['*'],
 'sayn.database': ['templates/*'],
 'sayn.scaffolding': ['data/init_project/*', 'data/init_project/sql/*'],
 'sayn.tasks': ['tests/*']}

install_requires = \
['Click==8.0.4',
 'Jinja2==3.0.3',
 'MarkupSafe==2.1.0',
 'SQLAlchemy==1.4.25',
 'colorama==0.4.4',
 'halo==0.0.31',
 'log-symbols==0.0.14',
 'orjson==3.7.7',
 'pydantic==1.9.0',
 'ruamel.yaml.clib==0.2.6',
 'ruamel.yaml==0.17.21',
 'six==1.16.0',
 'spinners==0.0.24',
 'termcolor==1.1.0',
 'typing_extensions==4.1.1']

extras_require = \
{'all': ['psycopg2==2.9.3',
         'PyMySQL==1.0.2',
         'snowflake-connector-python==2.7.4',
         'snowflake-sqlalchemy==1.3.3',
         'graphviz==0.19.1'],
 'bigquery': ['sqlalchemy-bigquery==1.3.0',
              'cachetools==5.0.0',
              'future==0.18.2',
              'google-api-core==2.5.0',
              'google-auth==2.6.0',
              'google-cloud-bigquery==2.34.0',
              'google-cloud-core==2.2.2',
              'google-crc32c==1.3.0',
              'google-resumable-media==2.2.1',
              'googleapis-common-protos==1.54.0',
              'grpcio==1.44.0',
              'grpcio-status==1.44.0',
              'packaging==21.3',
              'proto-plus==1.20.3',
              'protobuf==3.19.4',
              'pyasn1==0.4.8',
              'pyasn1-modules==0.2.8',
              'pyparsing==3.0.7',
              'python-dateutil==2.8.2',
              'rsa==4.8',
              'google-cloud-bigquery-storage==2.11.0',
              'libcst==0.4.1',
              'mypy-extensions==0.4.3',
              'typing-inspect==0.7.1',
              'charset-normalizer==2.0.12',
              'certifi==2021.10.8',
              'idna==3.3',
              'requests==2.27.1',
              'urllib3==1.26.8',
              'numpy==1.21.4',
              'pyarrow==6.0.0'],
 'graphviz': ['graphviz==0.19.1'],
 'mysql': ['PyMySQL==1.0.2'],
 'postgresql': ['psycopg2==2.9.3'],
 'snowflake': ['snowflake-connector-python==2.7.4',
               'snowflake-sqlalchemy==1.3.3',
               'asn1crypto==1.4.0',
               'cffi==1.15.0',
               'cryptography==36.0.1',
               'oscrypto==1.2.1',
               'pycparser==2.21',
               'pycryptodomex==3.14.1',
               'PyJWT==2.4.0',
               'pyOpenSSL==21.0.0',
               'pytz==2021.3',
               'charset-normalizer==2.0.12',
               'certifi==2021.10.8',
               'idna==3.3',
               'requests==2.27.1',
               'urllib3==1.26.8',
               'numpy==1.21.4',
               'pyarrow==6.0.0']}

entry_points = \
{'console_scripts': ['sayn = sayn.cli:cli']}

setup_kwargs = {
    'name': 'sayn',
    'version': '0.6.6',
    'description': 'Data-modelling and processing framework for automating Python and SQL tasks',
    'long_description': '<img\n  src="https://173-static-files.s3.eu-west-2.amazonaws.com/sayn_docs/logos/sayn_logo.png"\n  alt="SAYN logo"\n  style="width: 50%; height: 50%;"\n/>\n\n#\n\nSAYN is a modern data processing and modelling framework. Users define tasks (incl. Python, automated SQL transformations and more) and their relationships, SAYN takes care of the rest. It is designed for simplicity, flexibility and centralisation in order to bring significant efficiency gains to the data engineering workflow.\n\n## Use Cases\n\nSAYN can be used for multiple purposes across the data engineering and analytics workflows:\n\n* Data extraction: complement tools such as Fivetran or Stitch with customised extraction processes.\n* Data modelling: transform raw data in your data warehouse (e.g. aggregate activity or sessions, calculate marketing campaign ROI, etc.).\n* Data science: integrate and execute data science models.\n\n## Key Features\n\nSAYN has the following key features:\n\n* YAML based DAG (Direct Acyclic Graph) creation. This means all analysts, including non Python proficient ones, can easily add tasks to ETL processes with SAYN.\n* [Automated SQL transformations](https://173tech.github.io/sayn/tasks/autosql/): write your SELECT statement. SAYN turns it into a table/view and manages everything for you.\n* [Jinja parameters](https://173tech.github.io/sayn/parameters/): switch easily between development and product environment and other tricks with Jinja templating.\n* [Python tasks](https://173tech.github.io/sayn/tasks/python/): use Python scripts to complement your extraction and loading layer and build data science models.\n* Multiple [databases](https://173tech.github.io/sayn/databases/overview/) supported.\n* and much more... See the [Documentation](https://173tech.github.io/sayn/).\n\n## Design Principles\n\nSAYN aims to empower data engineers and analysts through its  three core design principles:\n\n* **Simplicity**: data processes should be easy to create, scale and maintain. So your team can focus on data transformation instead of writing processes. SAYN orchestrates all your tasks systematically and provides a lot of automation features.\n* **Flexibility**: the power of data is unlimited and so should your tooling. SAYN supports both SQL and Python so your analysts can choose the most optimal solution for each process.\n* **Centralisation**: all analytics code should live in one place, making your life easier and allowing dependencies throughout the whole analytics process.\n\n## Quick Start\n\nSAYN supports Python 3.7 to 3.10.\n\n```bash\n$ pip install sayn\n$ sayn init test_sayn\n$ cd test_sayn\n$ sayn run\n```\n\nThis is it! You completed your first SAYN run on the example project. Continue with the [Tutorial: Part 1](https://173tech.github.io/sayn/tutorials/tutorial_part1/) which will give you a good overview of SAYN\'s true power!\n\n## Release Updates\n\nIf you want to receive update emails about SAYN releases, you can sign up [here](http://eepurl.com/hnfJIr).\n\n## Support\n\nIf you need any help with SAYN, or simply want to know more, please contact the team at <sayn@173tech.com>.\n\n## License\n\nSAYN is open source under the [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) license.\n\n---\n\nMade with :heart: by [173tech](https://www.173tech.com).\n',
    'author': 'Robin Watteaux',
    'author_email': 'robin@173tech.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://173tech.github.io/sayn',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
