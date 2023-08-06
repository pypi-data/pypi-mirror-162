# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_ocpi',
 'py_ocpi.cdrs',
 'py_ocpi.cdrs.v_2_2_1',
 'py_ocpi.cdrs.v_2_2_1.api',
 'py_ocpi.commands',
 'py_ocpi.commands.v_2_2_1',
 'py_ocpi.commands.v_2_2_1.api',
 'py_ocpi.core',
 'py_ocpi.credentials',
 'py_ocpi.credentials.v_2_2_1',
 'py_ocpi.credentials.v_2_2_1.api',
 'py_ocpi.locations',
 'py_ocpi.locations.v_2_2_1',
 'py_ocpi.locations.v_2_2_1.api',
 'py_ocpi.sessions',
 'py_ocpi.sessions.v_2_2_1',
 'py_ocpi.sessions.v_2_2_1.api',
 'py_ocpi.tariffs',
 'py_ocpi.tariffs.v_2_2_1',
 'py_ocpi.tariffs.v_2_2_1.api',
 'py_ocpi.tokens',
 'py_ocpi.tokens.v_2_2_1',
 'py_ocpi.tokens.v_2_2_1.api',
 'py_ocpi.versions',
 'py_ocpi.versions.api']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.68.0,<0.69.0']

setup_kwargs = {
    'name': 'py-ocpi',
    'version': '0.1.1',
    'description': 'Python Implementation of OCPI',
    'long_description': '# ocpi\nPython implementation of the Open Charge Point Interface (OCPI)\n\n![Alt text](https://github.com/TECHS-Technological-Solutions/ocpi/blob/master/OCPI.png "feature development roadmap")\n\n\n# How Does it Work?\nModules that communicate with central system will use crud for retrieving required data. the data that is retrieved from central system may\nnot be compatible with OCPI protocol. So the data will be passed to adapter to make it compatible with schemas defined by OCPI. User only needs to\nmodify crud and adapter based on central system architecture.\n\n## License\n\nThis project is licensed under the terms of the MIT license.\n',
    'author': 'HAkhavan71',
    'author_email': 'hakh.27@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/TECHS-Technological-Solutions/ocpi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
