# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ptorru_matmul']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.4,<2.0.0']

setup_kwargs = {
    'name': 'ptorru-matmul',
    'version': '0.1.6',
    'description': 'Learning how to publish in PyPi through a generic implementation of matrix multiplication',
    'long_description': '# ptorru-matmul\n\nLearning about pipy, distributing a simple matrix multiply example\n\nTo consult how to distribute a package in PyPI take a look at the [publish_notes.md](https://github.com/ptorru/ptorru-matmul/blob/main/publish_notes.md)\n\n# Installing this package\n\nUsing [PyPI](https://pypi.org)\n\n```bash\npip install ptorru-matmul\n```\n\nAlternatively use [poetry](https://python-poetry.org)\n\n```bash\npoetry add ptorru-matmul\n```\n\n# Using this package\n\n```python\nimport numpy as np\nfrom ptorru_matmul import matmul\nsides = 3\na = np.arange(sides*sides).reshape(sides,sides)\nb = np.arange(sides*sides).reshape(sides,sides)\nc = matmul(a,b)\nassert np.array_equal(c, np.matmul(a,b))\nprint(a,b)\nprint(c)\n```\n',
    'author': 'Pedro Torruella',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://azure-brush-f4c.notion.site/ptorru-matmul-f056c93477d646d88f2bec319e12d2a1',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
