# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['computegraph', 'computegraph.draw']

package_data = \
{'': ['*']}

install_requires = \
['networkx>=2.6.2', 'numpy>=1.20.3']

extras_require = \
{':sys_platform == "darwin"': ['jax[cpu]>=0.3.14,<0.4.0'],
 ':sys_platform == "linux"': ['jax[cpu]>=0.3.14,<0.4.0'],
 'plotting': ['matplotlib>=3.5.1', 'plotly>=5.6.0'],
 'plotting:sys_platform == "linux"': ['pygraphviz>=1.8']}

setup_kwargs = {
    'name': 'computegraph',
    'version': '0.2.2',
    'description': 'computegraph is a tool for managing computational graphs using networkx',
    'long_description': '# computegraph\nTools for managing computation graphs based on dictionaries and networkx\n',
    'author': 'David Shipman',
    'author_email': 'dshipman@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/monash-emu/computegraph',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.0,<3.11',
}


setup(**setup_kwargs)
