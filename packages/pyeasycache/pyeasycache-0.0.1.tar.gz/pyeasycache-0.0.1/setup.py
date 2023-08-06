# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyeasycache',
 'pyeasycache.backend',
 'pyeasycache.backend.disk',
 'pyeasycache.backend.redis',
 'pyeasycache.core']

package_data = \
{'': ['*']}

install_requires = \
['diskcache>=5.4.0,<6.0.0', 'pydantic>=1.9.1,<2.0.0']

extras_require = \
{'redis': ['redis>=4.3.4,<5.0.0', 'pottery>=3.0.0,<4.0.0']}

setup_kwargs = {
    'name': 'pyeasycache',
    'version': '0.0.1',
    'description': 'easy python cache',
    'long_description': '# TODO\n* [ ] fully async support\n* [ ] more accurate and clear test \n* [ ] more accurate and clear pyproject.toml(especially dependency)\n* [ ] add backend:memcached\n\n---\n\n# pyeasycache\n\n```bash\npip install pyeasycache\n```\n\nTo create redis-cluster, use `./docker/docker-compose.yaml` if you need',
    'author': 'phi',
    'author_email': 'phi.friday@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
