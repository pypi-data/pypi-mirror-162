# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['connect', 'connect.reports', 'connect.reports.renderers']

package_data = \
{'': ['*'], 'connect.reports': ['schemas/*']}

install_requires = \
['Jinja2>=2,<4',
 'WeasyPrint>=53.4,<54.0',
 'jsonschema>=3.2.0,<4.0.0',
 'kaleido==0.2.1',
 'lxml>=4.9',
 'openpyxl>=2.5.14',
 'orjson>=3.5.2,<4.0.0',
 'plotly>=5.3.0,<6.0.0',
 'pytz>=2022']

setup_kwargs = {
    'name': 'connect-reports-core',
    'version': '26.0.0',
    'description': 'Connect Reports Core',
    'long_description': '# Connect Reports Core\n\n![pyversions](https://img.shields.io/pypi/pyversions/connect-reports-core.svg) [![PyPi Status](https://img.shields.io/pypi/v/connect-reports-core.svg)](https://pypi.org/project/connect-reports-core/) [![Build Connect Reports Core](https://github.com/cloudblue/connect-reports-core/actions/workflows/build.yml/badge.svg)](https://github.com/cloudblue/connect-reports-core/actions/workflows/build.yml) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=connect-reports-core&metric=alert_status)](https://sonarcloud.io/dashboard?id=connect-reports-core) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=connect-reports-core&metric=coverage)](https://sonarcloud.io/dashboard?id=connect-reports-core) [![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=connect-reports-core&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=connect-reports-core)\n\n## Introduction\n\n`Connect Reports Core` is the kernel package for handling reports on CloudBlue Connect Ecosystem. \nThis library is reponsible for validation of reports definition, choosing of renderer for parsing process and writing results of reports execution.\n\n\n## Install\n\n`Connect Reports Core` requires python 3.8 or later and has the following dependencies:\n\n* openpyxl>=2.5.14\n* WeasyPrint>=53.4\n* Jinja2>=2.11.3\n* jsonschema<=3.2.0\n* pytz>=2021.1\n* lxml>=4.7.1\n\n`Connect Reports Core` can be installed from [pypi.org](https://pypi.org/project/connect-reports-core/) using pip:\n\n```\n$ pip install connect-reports-core\n```\n\n## Testing\n\nOn MacOs:\n* Install system dependencies\n```commandline\nbrew install py3cairo pango\n```\n* Create virtualenv\n* Install project dependencies\n```commandline\npip install poetry\npoetry update\n```\n* Run tests\n```commandline\npoetry run pytest\n```\n\n\n## License\n\n``Connect Reports Core`` is released under the [Apache License Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).\n',
    'author': 'CloudBlue LLC',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://connect.cloudblue.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
