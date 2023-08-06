# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['meltano',
 'meltano.api',
 'meltano.api.controllers',
 'meltano.api.events',
 'meltano.api.executor',
 'meltano.api.models',
 'meltano.api.security',
 'meltano.api.workers',
 'meltano.cli',
 'meltano.core',
 'meltano.core.behavior',
 'meltano.core.block',
 'meltano.core.bundle',
 'meltano.core.container',
 'meltano.core.hub',
 'meltano.core.job',
 'meltano.core.legacy_tracking',
 'meltano.core.logging',
 'meltano.core.plugin',
 'meltano.core.plugin.dbt',
 'meltano.core.plugin.singer',
 'meltano.core.runner',
 'meltano.core.tracking',
 'meltano.core.tracking.contexts',
 'meltano.core.utils',
 'meltano.migrations',
 'meltano.migrations.utils',
 'meltano.migrations.versions',
 'meltano.oauth']

package_data = \
{'': ['*'],
 'meltano.api': ['static/*',
                 'static/css/*',
                 'static/js/*',
                 'static/logos/*',
                 'templates/*',
                 'templates/email/pipeline_manual_run/*',
                 'templates/security/*',
                 'templates/security/email/*'],
 'meltano.core.tracking': ['iglu-client-embedded/schemas/com.meltano/block_event/jsonschema/*',
                           'iglu-client-embedded/schemas/com.meltano/cli_context/jsonschema/*',
                           'iglu-client-embedded/schemas/com.meltano/cli_event/jsonschema/*',
                           'iglu-client-embedded/schemas/com.meltano/environment_context/jsonschema/*',
                           'iglu-client-embedded/schemas/com.meltano/exception_context/jsonschema/*',
                           'iglu-client-embedded/schemas/com.meltano/exit_event/jsonschema/*',
                           'iglu-client-embedded/schemas/com.meltano/plugins_context/jsonschema/*',
                           'iglu-client-embedded/schemas/com.meltano/project_context/jsonschema/*',
                           'iglu-client-embedded/schemas/com.meltano/telemetry_state_change_event/jsonschema/*'],
 'meltano.oauth': ['templates/*']}

install_requires = \
['aiodocker>=0.21.0,<0.22.0',
 'aiohttp>=3.4.4,<4.0.0',
 'alembic>=1.5.0,<2.0.0',
 'atomicwrites>=1.2.1,<2.0.0',
 'authlib>=1.0.1,<2.0.0',
 'backoff>=2.1.2,<3.0.0',
 'bcrypt>=3.2.0,<4.0.0',
 'cached-property>=1,<2',
 'click-default-group>=1.2.1,<2.0.0',
 'click>=8.1,<9.0',
 'email-validator>=1.1.2,<2.0.0',
 'fasteners>=0.17.3,<0.18.0',
 'flask-cors>=3.0.7,<4.0.0',
 'flask-executor>=0.10,<0.11',
 'flask-login==0.6.1',
 'flask-restful>=0.3.7,<0.4.0',
 'flask-sqlalchemy>=2.4.4,<3.0.0',
 'flask>=2.1,<3.0',
 'flatten-dict>=0,<1',
 'gunicorn>=20.1.0,<21.0.0',
 'jsonschema>=4.9,<5.0',
 'markdown>=3.3.7,<4.0.0',
 'meltano-flask-security>=0.1.0,<0.2.0',
 'packaging>=21.3,<22.0',
 'psutil>=5.6.3,<6.0.0',
 'psycopg2-binary>=2.8.5,<3.0.0',
 'pyhumps>=3.0.0,<4.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'python-gitlab>=3.5.0,<4.0.0',
 'pyyaml>=5.3.1,<6.0.0',
 'requests>=2.23.0,<3.0.0',
 'ruamel.yaml>=0.17.21,<0.18.0',
 'smtpapi>=0.4.1,<0.5.0',
 'snowplow-tracker>=0.10.0,<0.11.0',
 'sqlalchemy>=1.3.19,<2.0.0',
 'structlog>=21.2.0,<22.0.0',
 'tzlocal>=4.2.0,<5.0.0',
 'uvicorn[standard]>=0.17.6,<0.18.0',
 'werkzeug>=2.1,<=2.1.3']

extras_require = \
{'mssql': ['pymssql>=2.2.5,<3.0.0']}

entry_points = \
{'console_scripts': ['meltano = meltano.cli:main']}

setup_kwargs = {
    'name': 'meltano',
    'version': '2.4.0',
    'description': 'Meltano: Your DataOps Platform Infrastructure',
    'long_description': '\n<h1 align="center">Meltano</h1>\n<h3 align="center">Your Open Source DataOps Infrastructure</h3>\n\n---\n\n![Meltano Logo](https://lh4.googleusercontent.com/WHoN-WpacMaVicq-jRuIvCQjCIdPZwYOwBgd38k9JjMpX1Z7THUqowY-oRsTzGUbAvb8F4tcb9BJYyfX9MeA2ECirsWZ7XBHteDZ_y59REMwHjq1AX05U2k8H6mdI4G_olF27gadCfp1Wx7cVQ)\n\n<div align="center">\n<a href="https://docs.meltano.com/">\n<img alt="Docs" src="https://img.shields.io/website?down_color=red&down_message=offline&label=Docs&up_color=blue&up_message=online&url=https%3A%2F%2Fdocs.meltano.com%2F"/>\n</a>\n<a href="https://github.com/meltano/meltano/actions/workflows/test.yml?query=branch%3Amain">\n<img alt="Tests" src="https://github.com/meltano/meltano/actions/workflows/test.yml/badge.svg"/>\n</a>\n<a href="https://codecov.io/github/meltano/meltano">\n<img alt="Codecov" src="https://codecov.io/gh/meltano/meltano/branch/main/graph/badge.svg"/>\n</a>\n<a href="https://libraries.io/pypi/meltano/sourcerank">\n<img alt="Libraries.io SourceRank" src="https://img.shields.io/librariesio/sourcerank/pypi/meltano?label=SourceRank"/>\n</a>\n<a href="https://libraries.io/pypi/meltano">\n<img alt="Libraries.io dependency status for latest release" src="https://img.shields.io/librariesio/release/pypi/meltano?label=Dependencies"/>\n</a>\n</div>\n\n<div align="center">\n<a href="https://github.com/meltano/meltano/graphs/contributors">\n<img alt="GitHub contributors" src="https://img.shields.io/github/contributors/meltano/meltano?label=Contributors"/>\n</a>\n<a href="https://github.com/meltano/meltano/blob/main/LICENSE">\n<img alt="GitHub" src="https://img.shields.io/github/license/meltano/meltano?color=blue&label=License"/>\n</a>\n<a href="https://pypi.org/project/meltano/">\n<img alt="Meltano Python Package Version" src="https://img.shields.io/pypi/v/meltano?label=Version"/>\n</a>\n<a href="https://pypi.org/project/meltano/">\n<img alt="Supported Python Versions" src="https://img.shields.io/pypi/pyversions/meltano?label=Python"/>\n</a>\n<a href="https://pypi.org/project/meltano/">\n<img alt="Monthly PyPI Downloads" src="https://img.shields.io/pypi/dm/meltano?label=PyPI%20Downloads"/>\n</a>\n<a href="https://hub.docker.com/r/meltano/meltano">\n<img alt="Docker Pulls" src="https://img.shields.io/docker/pulls/meltano/meltano?label=Docker%20Pulls"/>\n</a>\n</div>\n\n---\n\nWelcome to your Open Source DataOps Infrastructure to manage and centralize all the data tools in your stack and turn them into your ideal end-to-end data platform. With Meltano, you\'ll be able to collaboratively build and improve your data platform like a software project; spinning up a service or tool (Airflow, dbt, Great Expectations, Snowflake, etc) and easily configuring, deploying and managing it through a single control plane.\n\n![Meltano as a computer chip](https://lh3.googleusercontent.com/1uzR_ETj6Kj1eleSjkbCpi5ZfqxFDm4hd6jzZ7JVxi2ajI9gPyjEyg6bspvha7O8dYpO3s9Y-CN6hfwiY8rvsmh9rsZ4oACh-FhvwfRBJS8oCsE76Twkf_UCHWLSmxEdvSaYyDTIqKVrdpsvsg)\n\nIntegrations\n------------\n\n[MeltanoHub](https://hub.meltano.com/) is the single source of truth to find any Meltano plugins as well as [Singer](https://singer.io/) taps and targets. Users are also able to add more plugins to the Hub and have them immediately discoverable and usable within Meltano. The Hub is lovingly curated by Meltano and the wider Meltano community.\n\nInstallation\n------------\n\nIf you\'re ready to build your ideal data platform and start running data workflows across multiple tools, start by following the [Installation guide](https://docs.meltano.com/guide/installation) to have Meltano up and running in your device.\n\nDocumentation\n-------------\n\nCheck out the ["Getting Started" guide](https://docs.meltano.com/getting-started) or find the full documentation at [https://docs.meltano.com](https://docs.meltano.com/).\n\nContributing\n------------\n\nMeltano is a truly open-source project, built for and by its community. We happily welcome and encourage your contributions. Start by browsing through our [issue tracker](https://github.com/meltano/meltano/issues?q=is%3Aopen+is%3Aissue) to add your ideas to the roadmap. If you\'re still unsure on what to contribute at the moment, you can always check out the list of open issues labeled as "[Accepting Merge Requests](https://github.com/meltano/meltano/issues?q=is%3Aopen+is%3Aissue+label%3A%22accepting+merge+requests%22)".\n\nFor more information on how to contribute to Meltano, refer to our [contribution guidelines](https://docs.meltano.com/contribute/).\n\nCommunity\n---------\n\nWe host weekly online events where you can engage with us directly. Check out more information in our [Community](https://meltano.com/community/) page.\n\nIf you have any questions, want sneak peeks of features or would just like to say hello and network, join our community of over +2,500 data professionals!\n\n👋 [Join us on Slack!](https://meltano.com/slack)\n\nResponsible Disclosure Policy\n-----------------------------\n\nPlease refer to the [responsible disclosure policy](https://docs.meltano.com/the-project/responsible-disclosure) on our website.\n\nLicense\n-------\n\nThis code is distributed under the MIT license, see the [LICENSE](https://github.com/meltano/meltano/blob/main/LICENSE) file.\n',
    'author': 'Meltano',
    'author_email': 'hello@meltano.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/meltano/meltano',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
