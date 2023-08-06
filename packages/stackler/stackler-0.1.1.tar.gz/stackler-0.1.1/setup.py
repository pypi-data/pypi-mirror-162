# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stackler']

package_data = \
{'': ['*']}

install_requires = \
['GitPython==3.1.27',
 'click==8.1.3',
 'phabricator==0.9.1',
 'termcolor==1.1.0',
 'typer==0.6.1']

entry_points = \
{'console_scripts': ['stackler = stackler.main:app']}

setup_kwargs = {
    'name': 'stackler',
    'version': '0.1.1',
    'description': '',
    'long_description': '# Stackler\n\nWorking with Phabricator Stack has never been so easy.\n\n# Install\n\n```\npoetry install --no-dev\n```\n\n# Develop\n\n```\npoetry install\npoetry config virtualenvs.in-project true\npoetry shell\n```\n\n',
    'author': 'Modun',
    'author_email': 'modun@xiaohongshu.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
