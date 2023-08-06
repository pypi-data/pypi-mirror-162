# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['snowpy3']

package_data = \
{'': ['*']}

install_requires = \
['redis>=4.3,<5.0', 'requests>=2.20,<3.0']

setup_kwargs = {
    'name': 'snowpy3',
    'version': '2022.8.10.2',
    'description': 'Python 3 Library to interact with and manage a ServiceNow instance via JSONv2',
    'long_description': '```\n███████╗███╗   ██╗ ██████╗ ██╗    ██╗██████╗ ██╗   ██╗██████╗ \n██╔════╝████╗  ██║██╔═══██╗██║    ██║██╔══██╗╚██╗ ██╔╝╚════██╗\n███████╗██╔██╗ ██║██║   ██║██║ █╗ ██║██████╔╝ ╚████╔╝  █████╔╝\n╚════██║██║╚██╗██║██║   ██║██║███╗██║██╔═══╝   ╚██╔╝   ╚═══██╗\n███████║██║ ╚████║╚██████╔╝╚███╔███╔╝██║        ██║   ██████╔╝\n╚══════╝╚═╝  ╚═══╝ ╚═════╝  ╚══╝╚══╝ ╚═╝        ╚═╝   ╚═════╝\n\n      Python 3 Library for ServiceNow JSONv2 Rest API\n\n\n*---------------------------------------------------------[ NOTE ]-*\n* Based on servicenow 2.1.0 <https://pypi.org/project/servicenow/> *\n* Wrttien by Francisco Freire <francisco.freire@locaweb.com.br>    *\n*------------------------------------------------------------------*\n```\n\n## Installing\n\n```\npip install snowpy3\n```\nCurrent version of SNOWPY3 works with NOW (New York version)\n\n## Dependencies\n\n- python-requests\n- python-redis\n\n\n\n## NOTES\n   Works with the latest version of SNOW (Aug 5, 2022 checks)\n',
    'author': 'TANGONINE',
    'author_email': 'rcb@tangonine.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.tangonine.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
