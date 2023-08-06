# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mutablesecurity',
 'mutablesecurity.autodoc',
 'mutablesecurity.cli',
 'mutablesecurity.config',
 'mutablesecurity.helpers',
 'mutablesecurity.leader',
 'mutablesecurity.logger',
 'mutablesecurity.main',
 'mutablesecurity.solutions',
 'mutablesecurity.solutions.base',
 'mutablesecurity.solutions.common.facts',
 'mutablesecurity.solutions.common.operations',
 'mutablesecurity.solutions.implementations',
 'mutablesecurity.solutions.implementations.dummy',
 'mutablesecurity.solutions.implementations.fail2ban',
 'mutablesecurity.solutions.implementations.lets_encrypt',
 'mutablesecurity.solutions.implementations.suricata',
 'mutablesecurity.solutions.implementations.teler',
 'mutablesecurity.solutions_manager',
 'mutablesecurity.visual_proxy']

package_data = \
{'': ['*'],
 'mutablesecurity.solutions.implementations.fail2ban': ['files/*',
                                                        'files/healthcheck/*'],
 'mutablesecurity.solutions.implementations.teler': ['files/*']}

install_requires = \
['Click>=8.0,<9.0',
 'PyYAML==6.0',
 'humanfriendly>=10.0,<11.0',
 'packaging>=21.3,<22.0',
 'pyinfra>=2.2,<3.0',
 'pypattyrn>=1.2,<2.0',
 'requests>=2.27.1,<3.0.0',
 'rich==12.5.1']

entry_points = \
{'console_scripts': ['mutablesecurity = mutablesecurity.cli:main']}

setup_kwargs = {
    'name': 'mutablesecurity',
    'version': '0.3.0',
    'description': 'Seamless deployment and management of cybersecurity solutions',
    'long_description': '<div align="center">\n    <img src="https://raw.githubusercontent.com/MutableSecurity/mutablesecurity/main/others/readme_images/cover.webp" width="600px" alt="Cover">\n    <br/><br/>\n    <img src="https://img.shields.io/github/workflow/status/mutablesecurity/mutablesecurity/Executes%20unit%20testing%20and%20coverage%20reporting?color=brightgreen&label=unit%20tests&logo=github&logoColor=white&style=flat-square" alt="Unit Tests">\n    <a href=\'https://coveralls.io/github/MutableSecurity/mutablesecurity?branch=main\'>\n        <img src="https://img.shields.io/coveralls/github/MutableSecurity/mutablesecurity?color=brightgreen&label=coverage&logo=coveralls&logoColor=white" alt="Coveralls Coverage">\n    </a>\n    <br/>\n    <img src="https://snyk-widget.herokuapp.com/badge/pip/mutablesecurity/badge.svg" alt="Snyk Security Score">\n    <img src="https://deepsource.io/gh/MutableSecurity/mutablesecurity.svg/?label=active+issues&show_trend=true&token=p678jq0qtDRJaOXo_Whya-un" alt="Deepsource active issues">\n    <img src="https://img.shields.io/badge/dependencies%20bumping-enabled-brightgreen?logo=dependabot&style=flat-square&logoColor=white" alt="Dependencies Bumping via Dependabot">\n    <br/>\n    <img src="https://img.shields.io/pypi/dm/mutablesecurity?color=blue&logoColor=white&label=downloads&logo=pypi&style=flat-square" alt="Monthly Downloads on PyPi">\n    <img src="https://img.shields.io/pypi/v/mutablesecurity?color=blue&label=version&logo=pypi&logoColor=white&style=flat-square" alt="Stable Version of PyPi">\n    <img src="https://img.shields.io/github/stars/mutablesecurity/mutablesecurity?color=blue&logoColor=white&label=stars&logo=github&style=flat-square" alt="GitHub Stars">\n    <img src="https://img.shields.io/github/issues-closed/mutablesecurity/mutablesecurity?color=blue&logoColor=white&label=issues&logo=github&style=flat-square" alt="GitHub closed issues">\n    <img src="https://img.shields.io/github/license/mutablesecurity/mutablesecurity?color=lightgray&logoColor=white&label=license&logo=opensourceinitiative&style=flat-square" alt="License">\n    <br/>\n</div>\n\n---\n\n# Description\n\n**MutableSecurity** is a software product for making cybersecurity solution management easier and more accessible, from deployment and configuration to monitoring.\n\nDespite the current lack of complex functionalities, we have a vision in mind that we hope to achieve in the near future. As we must begin somewhere, the first step in our progress is this command line interface for automatic management of cybersecurity solutions.\n\nCome join the MutableSecurity journey!\n\n# Read Further 📎\n\nThis is only an excerpt from the `README.md` hosted on GitHub. To read the full text, please visit our [official repository](https://github.com/MutableSecurity/mutablesecurity) and check our [website and documentation](https://mutablesecurity.io/)!',
    'author': 'MutableSecurity',
    'author_email': 'hello@mutablesecurity.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.mutablesecurity.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
