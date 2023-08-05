# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['toucan_connectors',
 'toucan_connectors.adobe_analytics',
 'toucan_connectors.aircall',
 'toucan_connectors.anaplan',
 'toucan_connectors.awsathena',
 'toucan_connectors.azure_mssql',
 'toucan_connectors.clickhouse',
 'toucan_connectors.databricks',
 'toucan_connectors.dataiku',
 'toucan_connectors.elasticsearch',
 'toucan_connectors.facebook_ads',
 'toucan_connectors.facebook_insights',
 'toucan_connectors.github',
 'toucan_connectors.google_adwords',
 'toucan_connectors.google_analytics',
 'toucan_connectors.google_big_query',
 'toucan_connectors.google_cloud_mysql',
 'toucan_connectors.google_my_business',
 'toucan_connectors.google_sheets',
 'toucan_connectors.google_sheets_2',
 'toucan_connectors.google_spreadsheet',
 'toucan_connectors.hive',
 'toucan_connectors.http_api',
 'toucan_connectors.hubspot',
 'toucan_connectors.install_scripts',
 'toucan_connectors.lightspeed',
 'toucan_connectors.linkedinads',
 'toucan_connectors.micro_strategy',
 'toucan_connectors.mongo',
 'toucan_connectors.mssql',
 'toucan_connectors.mssql_TLSv1_0',
 'toucan_connectors.mysql',
 'toucan_connectors.net_explorer',
 'toucan_connectors.oauth2_connector',
 'toucan_connectors.odata',
 'toucan_connectors.odbc',
 'toucan_connectors.one_drive',
 'toucan_connectors.oracle_sql',
 'toucan_connectors.postgres',
 'toucan_connectors.redshift',
 'toucan_connectors.revinate',
 'toucan_connectors.rok',
 'toucan_connectors.salesforce',
 'toucan_connectors.salesforce_sandbox',
 'toucan_connectors.sap_hana',
 'toucan_connectors.snowflake',
 'toucan_connectors.snowflake_oauth2',
 'toucan_connectors.soap',
 'toucan_connectors.toucan_toco',
 'toucan_connectors.trello',
 'toucan_connectors.utils',
 'toucan_connectors.wootric']

package_data = \
{'': ['*'], 'toucan_connectors': ['aws/*', 'denodo/*', 'share_point/*']}

install_requires = \
['Authlib>=1.0.1,<2.0.0',
 'Jinja2>=3.0.3,<4.0.0',
 'aiohttp>=3.8.1,<4.0.0',
 'cached-property>=1.5.2,<2.0.0',
 'jq>=1.2.2,<2.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'tenacity>=8.0.1,<9.0.0',
 'toucan-data-sdk>=7.4.2,<8.0.0']

extras_require = \
{':extra == "ROK"': ['requests>=2.27.1,<3.0.0'],
 'ROK': ['PyJWT>=1.5.3,<3', 'simplejson>=3.17.6,<4.0.0'],
 'Redshift': ['redshift-connector>=2.0.907,<3.0.0', 'lxml==4.6.5'],
 'adobe': ['adobe-analytics>=1.2.3,<2.0.0'],
 'aircall': ['bearer==3.1.0'],
 'all': ['adobe-analytics>=1.2.3,<2.0.0',
         'bearer==3.1.0',
         'oauthlib==3.2.0',
         'requests-oauthlib==1.3.1',
         'awswrangler>=2.15.1,<3.0.0',
         'pyodbc>=4,<5',
         'clickhouse-driver>=0.2.3,<1.0',
         'dataiku-api-client>=9.0.1,<10.0.0',
         'elasticsearch>=7.11.0,<8',
         'facebook-sdk>=3.1.0,<4.0.0',
         'python-graphql-client>=0.4.3,<1.0',
         'google-api-python-client>=2,<3',
         'oauth2client>=4.1.3,<5.0.0',
         'googleads>=32.0.0,<33.0.0',
         'google-cloud-bigquery[bqstorage,pandas]>=2,<3',
         'PyMySQL>=1.0.2,<2.0.0',
         'gspread>=5.4.0,<6.0.0',
         'PyHive[hive]>=0.6.5,<1.0',
         'xmltodict>=0.13.0,<1.0',
         'pymongo',
         'tctc-odata>=0.3,<1.0',
         'cx-Oracle>=8.3.0,<9.0.0',
         'openpyxl>=3.0.9,<4.0.0',
         'psycopg2>=2.7.4,<3.0.0',
         'redshift-connector>=2.0.907,<3.0.0',
         'lxml==4.6.5',
         'PyJWT>=1.5.3,<3',
         'simplejson>=3.17.6,<4.0.0',
         'pyhdb>=0.3.4,<1.0',
         'zeep>=4.1.0,<5.0.0',
         'snowflake-connector-python>=2.7.8,<3.0.0',
         'pyarrow<7',
         'toucan-client>=1.0.1,<2.0.0'],
 'awsathena': ['awswrangler>=2.15.1,<3.0.0'],
 'azure_mssql': ['pyodbc>=4,<5'],
 'clickhouse': ['clickhouse-driver>=0.2.3,<1.0'],
 'dataiku': ['dataiku-api-client>=9.0.1,<10.0.0'],
 'elasticsearch': ['elasticsearch>=7.11.0,<8'],
 'facebook': ['facebook-sdk>=3.1.0,<4.0.0'],
 'github': ['python-graphql-client>=0.4.3,<1.0'],
 'google_analytics': ['google-api-python-client>=2,<3',
                      'oauth2client>=4.1.3,<5.0.0'],
 'google_big_query': ['google-cloud-bigquery[bqstorage,pandas]>=2,<3'],
 'google_cloud_mysql': ['PyMySQL>=1.0.2,<2.0.0'],
 'google_my_business': ['google-api-python-client>=2,<3'],
 'google_sheets': ['google-api-python-client>=2,<3'],
 'google_spreadsheet': ['oauth2client>=4.1.3,<5.0.0', 'gspread>=5.4.0,<6.0.0'],
 'hive': ['PyHive[hive]>=0.6.5,<1.0'],
 'http_api': ['oauthlib==3.2.0',
              'requests-oauthlib==1.3.1',
              'xmltodict>=0.13.0,<1.0'],
 'lightspeed': ['bearer==3.1.0'],
 'mongo': ['pymongo'],
 'mssql': ['pyodbc>=4,<5'],
 'mssql_TLSv1_0': ['pyodbc>=4,<5'],
 'mysql': ['PyMySQL>=1.0.2,<2.0.0'],
 'net_explorer': ['openpyxl>=3.0.9,<4.0.0'],
 'odata': ['oauthlib==3.2.0',
           'requests-oauthlib==1.3.1',
           'tctc-odata>=0.3,<1.0'],
 'oracle_sql': ['cx-Oracle>=8.3.0,<9.0.0'],
 'postgres': ['psycopg2>=2.7.4,<3.0.0'],
 'sap_hana': ['pyhdb>=0.3.4,<1.0'],
 'snowflake': ['PyJWT>=1.5.3,<3',
               'snowflake-connector-python>=2.7.8,<3.0.0',
               'pyarrow<7'],
 'soap': ['lxml==4.6.5', 'zeep>=4.1.0,<5.0.0'],
 'toucan_toco': ['toucan-client>=1.0.1,<2.0.0']}

setup_kwargs = {
    'name': 'toucan-connectors',
    'version': '3.17.4',
    'description': 'Toucan Toco Connectors',
    'long_description': '[![Pypi-v](https://img.shields.io/pypi/v/toucan-connectors.svg)](https://pypi.python.org/pypi/toucan-connectors)\n[![Pypi-pyversions](https://img.shields.io/pypi/pyversions/toucan-connectors.svg)](https://pypi.python.org/pypi/toucan-connectors)\n[![Pypi-l](https://img.shields.io/pypi/l/toucan-connectors.svg)](https://pypi.python.org/pypi/toucan-connectors)\n[![Pypi-wheel](https://img.shields.io/pypi/wheel/toucan-connectors.svg)](https://pypi.python.org/pypi/toucan-connectors)\n[![GitHub Actions](https://github.com/ToucanToco/toucan-connectors/workflows/CI/badge.svg)](https://github.com/ToucanToco/toucan-connectors/actions?query=workflow%3ACI)\n[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=ToucanToco_toucan-connectors&metric=coverage)](https://sonarcloud.io/dashboard?id=ToucanToco_toucan-connectors)\n\n# Toucan Connectors\n[Toucan Toco](https://toucantoco.com/fr/) data connectors are plugins to the Toucan Toco platform. Their role is to return [Pandas DataFrames](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) from many different sources.\n\n![Components Diagram](doc/ComponentsDiagram.jpeg)\n\nEach connector is dedicated to a single type of source (PostrgeSQL, Mongo, Salesforce, etc...) and is made of two classes:\n\n- `Connector` which contains all the necessary information to *use a data provider* (e.g. hostname,  auth method and details, etc...).\n- `DataSource` which contains all the information to *get a dataframe* (query, path, etc...) using the `Connector` class above.\n\nThe Toucan Toco platform instantiates these classes using values provided by Toucan admin and app designers, it then uses the following methods to get data and metadata:\n\n- `Connector._retrieve_data` returning an instance of `pandas.DataFrame`, method used to return data to a Toucan Toco end user\n- `Connector.get_slice` returning an instance of `DataSlice`, method used to return data to a Toucan Toco application designer when building a query.\n- `Connector.get_status` returning an instance of `ConnectorStatus`, method used to inform an admin or Toucan Toco application designer of the status of its connection to a third party data service. Is it reachable from our servers? Are the authentication details and method working? etc...\n\n## Installing for development\n\nWe use `poetry` for packaging and development. Use the following command to install the project for development:\n\n```\npoetry install -E all\n```\n\n## Dependencies\n\nThis project uses `make` and `Python 3.8`. Install the main dependencies :\n\n```bash\npip install -e .\n```\n\nWe are using the `setuptools` construct `extra_requires` to define each connector\'s dependencies separately. For example to install the MySQL connector dependencies:\n\n```bash\npip install -e ".[mysql]"\n```\n\nThere is a shortcut called `all` to install all the dependencies for all the connectors. I do not recommend that you use this as a contributor to this package, but if you do, use the section below to install the necessary system packages.\n\n```bash\npip install -e ".[all]"\n```\n\nYou may face issues when instally the repo locally due to dependencies.\nThat\'s why a dev container is available to be used with visual studio.\nRefer to [this doc](https://code.visualstudio.com/docs/remote/containers) to use it.\n\n\n### System packages\n\nSome connectors dependencies require specific system packages. As each connector can define its dependencies separatly you do not need this until you want to use these specific connectors.\n\n#### ODBC\n\nOn `linux`, you\'re going to need bindings for `unixodbc` to install `pyodbc` from the requirements, and to install that (using apt), just follow:\n\n```bash\nsudo apt-get update\nsudo apt-get install unixodbc-dev\n```\n\n#### MSSSQL\n\nTo test and use `mssql` (and `azure_mssql`) you need to install the Microsoft ODBC driver for SQL Server for\n[Linux](https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver15)\nor [MacOS](https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/install-microsoft-odbc-driver-sql-server-macos?view=sql-server-ver15)\n\n#### PostgreSQL\n\nOn macOS, to test the `postgres` connector, you need to install `postgresql` by running for instance `brew install postgres`.\nYou can then install the library with `env LDFLAGS=\'-L/usr/local/lib -L/usr/local/opt/openssl/lib -L/usr/local/opt/readline/lib\' pip install psycopg2`\n\n## Testing\n\nWe are using `pytest` and various packages of its ecosystem.\nTo install the testing dependencies, run:\n\n```bash\npip install -r requirements-testing.txt\n```\n\nAs each connector is an independant plugin, its tests are written independently from the rest of the codebase.\nRun the tests for a specifc connector (`http_api` in this example) like this:\n\n```bash\npytest tests/http_api\n```\n\nNote: running the tests above implies that you have installed the specific dependencies of the `http_api` connector (using the `pip install -e .[http_api]` command)\n\nOur CI does run all the tests for all the connectors, like this:\n\n```\npip install -e ".[all]"\nmake test\n```\n\nSome connectors are tested using mocks (cf. `trello`), others are tested by making calls to data providers (cf. `elasticsearch`) running on the system in docker containers. The required images are in the `tests/docker-compose.yml` file, they need to be pulled (cf. `pytest --pull`) to run the relevant tests.\n\n## Contributing\n\nThis is an open source repository under the [BSD 3-Clause Licence](https://github.com/ToucanToco/toucan-connectors/blob/master/LICENSE). The Toucan Toco tech team are the maintainers of this repository, we welcome contributions. \n\nAt the moment the main use of this code is its integration into Toucan Toco commercially licenced software, as a result our dev and maintenance efforts applied here are mostly driven by Toucan Toco internal priorities.\n\nThe starting point of a contribution should be an [Issue](https://github.com/ToucanToco/toucan-connectors/issues), either one you create or an existing one. This allows us (maintainers) to discuss the contribution before it is produced and avoids back and forth in reviews or stalled pull requests.\n\n### Step 1: Generate base classes and tests files\n\nTo generate the connector and test modules from boilerplate, run:\n\n```\nmake new_connector type=mytype\n```\n\n`mytype` should be the name of a system we would like to build a connector for,\nsuch as `MySQL` or `Hive` or `Magento`.\n\nOpen the folder in `tests` for the new connector. You can start writing your tests before implementing it.\n\nSome connectors are tested with calls to the actual data systems that they target,\nfor example `elasticsearch`, `mongo`, `mssql`.\n\nOthers are tested with mocks of the\nclasses or functions returning data that you are wrapping (see : `HttpAPI`, or\n`microstrategy`).\n\nIf you have a container for your target system, add a docker image in\nthe `docker-compose.yml`, then use the `pytest` fixture `service_container` to automatically\nstart the docker and shut it down for you when you are running tests.\n\nThe fixture will not pull the image for you for each test runs, you need to pull the image on your machine (at least once) using the `pytest --pull` option.\n\n### Step 2: New connector\n\nOpen the folder `mytype` in `toucan_connectors` for your new connector and create your classes.\n\n```python\nimport pandas as pd\n\n# Careful here you need to import ToucanConnector from the deep path, not the __init__ path.\nfrom toucan_connectors.toucan_connector import ToucanConnector, ToucanDataSource\n\n\nclass MyTypeDataSource(ToucanDataSource):\n    """Model of my datasource"""\n    query: str\n\n\nclass MyTypeConnector(ToucanConnector):\n    """Model of my connector"""\n    data_source_model: MyTypeDataSource\n\n    host: str\n    port: int\n    database: str\n\n    def _retrieve_data(self, data_source: MyTypeDataSource) -> pd.DataFrame:\n        ...\n\n    def get_slice(self, ...) -> DataSlice:\n        ...\n\n    def get_status(self) -> ConnectorStatus:\n        ...\n```\n\n### Step 3: Register your connector, add documentation\n\nAdd your connector in `toucan_connectors/__init__.py`.\nThe key is what we call the `type` of the connector, which\nis an id used to retrieve it when used in Toucan Toco platform.\n\n```python\nCONNECTORS_CATALOGUE = {\n  ...,\n  \'MyType\': \'mytype.mytype_connector.MyTypeConnector\',\n  ...\n}\n```\n\nAdd you connector requirements to the `setup.py` in the `extras_require` dictionary:\n\n```ini\nextras_require = {\n    ...\n    \'mytype\': [\'my_dependency_pkg1==x.x.x\', \'my_dependency_pkg2>=x.x.x\']\n}\n```\n\nIf you need to add testing dependencies, add them to the `requirements-testing.txt` file.\n\nYou can now generate and edit the documentation page for your connector:\n\n```shell\n# Example: PYTHONPATH=. python doc/generate.py github > doc/connectors/github.md\nPYTHONPATH=. python doc/generate.py myconnectormodule > doc/connectors/mytypeconnector.md\n```\n\n### Step 4 : Create a pull request\n\nMake sure your new code is properly formatted by running `make lint`. If it\'s not, please use `make format`. You can now create a pull request.\n\n## Publish\n\nInstall the `wheel` package:\n\n```shell\npip install wheel\n```\n\nTo publish the `toucan-connectors` package on pypi, use:\n\n```shell\nmake build\nmake upload\n```\n',
    'author': 'Toucan Toco',
    'author_email': 'dev@toucantoco.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
