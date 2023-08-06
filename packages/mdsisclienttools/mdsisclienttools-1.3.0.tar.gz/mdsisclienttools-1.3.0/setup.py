# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mdsisclienttools', 'mdsisclienttools.auth', 'mdsisclienttools.datastore']

package_data = \
{'': ['*']}

install_requires = \
['cloudpathlib[s3]>=0.9.0,<0.10.0',
 'pydantic>=1.9.1,<2.0.0',
 'python-jose>=3.3.0,<4.0.0',
 'requests>=2.28.1,<3.0.0',
 'types-requests>=2.28.3,<3.0.0']

setup_kwargs = {
    'name': 'mdsisclienttools',
    'version': '1.3.0',
    'description': 'Python package containing client tools to assist in accessing and using the RRAP M&DS IS APIs and services.',
    'long_description': '# mdsisclienttools\n![build](https://github.com/gbrrestoration/mds-is-client-tools/actions/workflows/ci-cd.yml/badge.svg)\n[![codecov](https://codecov.io/gh/gbrrestoration/mds-is-client-tools/branch/main/graph/badge.svg?token=QVMBSUJFEF)](https://codecov.io/gh/gbrrestoration/mds-is-client-tools)\n\nPython package containing client tools to assist in accessing and using the RRAP M&DS IS APIs and services.\n\n## Installation\n\n```bash\n$ pip install mdsisclienttools\n```\n\n## Usage\n\n### Documentation \n[See our read-the-docs documentation here](http://mds-is-client-tools.readthedocs.io/)\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`mdsisclienttools` was created by RRAP. RRAP retains all rights to the source and it may not be reproduced, distributed, or used to create derivative works.\n\n## Credits\n\n`mdsisclienttools` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'RRAP',
    'author_email': 'rrapisdev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
