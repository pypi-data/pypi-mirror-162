# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['elastic_log_cli',
 'elastic_log_cli._compat',
 'elastic_log_cli.kql',
 'elastic_log_cli.utils']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.4,<9.0.0',
 'lark>=1.1.1,<2.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'requests>=2.28.1,<3.0.0']

extras_require = \
{'aws': ['botocore>=1.27.46,<2.0.0', 'boto3>=1.24.46,<2.0.0']}

entry_points = \
{'console_scripts': ['elastic-logs = elastic_log_cli.__main__:run_cli']}

setup_kwargs = {
    'name': 'elastic-log-cli',
    'version': '0.2.0',
    'description': '',
    'long_description': '# Elastic Log CLI\n\nCLI for streaming logs from Elasticsearch to a terminal.\n\n## Installation\n\nInstall with `pip`:\n\n```bash\npip install elastic-log-cli\n```\n\n> :memo: Requires Python 3.10\n\n\n## Configuration\n\nThe following environment variables are used to configure the tool. For secure, easy selection of target clusters, a tool like [envchain](https://github.com/sorah/envchain) is recommended.\n\nWhere available, CLI options will override environment variables.\n\n<!-- generated env. vars. start -->\n### `ELASTICSEARCH_URL`\n\n**Required**\n\nURL of the Elasticsearch cluster containing logs. You can also provide an Elastic Cloud ID by prefixing with it `cloud:`.\n\n### `ELASTICSEARCH_USERNAME`\n\n*Optional*\n\nUsername for the Elasticsearch cluster containing logs.\n\n### `ELASTICSEARCH_PASSWORD`\n\n*Optional*\n\nPassword for the Elasticsearch cluster containing logs.\n\n### `ELASTICSEARCH_AUTH_MODE`\n\n*Optional*, default value: `basicauth`\n\nSpecify which authentication mode you are using.\n\nThe default behaviour is `basicauth`, which encodes the username and password using HTTP Basic Auth.\n\nYou may also set this to `apikey`, in which case the API Keys should be provided as follows:\n\n```\nELASTICSEARCH_USERNAME=${APIKEY_NAME}\nELASTICSEARCH_PASSWORD=${APIKEY_KEY}\n```\n\nFinally, if you are using [Amazon OpenSearch Service](https://aws.amazon.com/opensearch-service/) with [AWS Signature V4](https://docs.aws.amazon.com/general/latest/gr/signature-version-4.html) auth, then set this to `awssigv4`. AWS credentials will be read from the environment and used to sign your requests.\n\n\n#### Possible values\n\n`basicauth`, `apikey`, `awssigv4`\n\n### `ELASTICSEARCH_TIMEOUT`\n\n*Optional*, default value: `40`\n\nHow long to wait on Elasticsearch requests.\n\n### `ELASTICSEARCH_INDEX`\n\n*Optional*, default value: `filebeat-*`\n\nThe index to target. Globs are supported.\n\n### `ELASTICSEARCH_TIMESTAMP_FIELD`\n\n*Optional*, default value: `@timestamp`\n\nThe field which denotes the timestamp in the indexed logs.\n<!-- generated env. vars. end -->\n\n## Usage\n\n<!-- generated usage start -->\n```\nUsage: elastic-logs [OPTIONS] QUERY\n\n  Stream logs from Elasticsearch.\n\n  Accepts a KQL query as its only positional argument.\n\nOptions:\n  -p, --page-size INTEGER RANGE  The number of logs to fetch per page  [x>=0]\n  -i, --index TEXT               The index to target. Globs are supported.\n                                 [default: (filebeat-*)]\n  -s, --start TEXT               When to begin streaming logs from.\n  -e, --end TEXT                 When to stop streaming logs. Omit to\n                                 continuously stream logs until interrupted.\n  --source CSV                   Source fields to retrieve, comma-separated.\n                                 Default behaviour is to fetch full document.\n  -t, --timestamp-field TEXT     The field which denotes the timestamp in the\n                                 indexed logs.  [default: (@timestamp)]\n  --version                      Show version and exit.\n  --help                         Show this message and exit.\n\n```\n<!-- generated usage end -->\n\n\n### Example\n\n```shell\nelastic-logs \\\n    --start 2022-03-05T12:00:00 \\\n    --end 2022-03-05T13:00:00 \\\n    --source time,level,message,error \\\n    --index filebeat-7.16.2 \\\n    --timestamp-field time \\\n    \'level:ERROR and error.code:500\'\n```\n\n### KQL support\n\nThe following KQL features are not yet supported:\n\n- Wildcard fields, e.g. `*:value` or `machine.os*:windows 10`\n- Prefix matching, e.g. `machine.os:win*`\n- Match phrase, e.g. `message:"A quick brown fox"`\n\n## Development\n\nInstall dependencies:\n\n```shell\npyenv shell 3.10.x\npre-commit install  # Configure commit hooks\npoetry install  # Install Python dependencies\n```\n\nRun tests:\n\n```shell\npoetry run inv verify\n```\n\n# License\nThis project is distributed under the MIT license.\n',
    'author': 'Jack Smith',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jacksmith15/elastic-log-cli',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
