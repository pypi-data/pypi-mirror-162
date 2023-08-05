# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['dqg']
install_requires = \
['Django-Polymorphic>=3.1.0,<4.0.0', 'Django>=4.1,<5.0']

setup_kwargs = {
    'name': 'django-query-graph',
    'version': '0.0.0.dev1',
    'description': 'Django Model Query Graph',
    'long_description': '# Django Model Query Graphs\n',
    'author': 'The Vinh LUONG (LƯƠNG Thế Vinh)',
    'author_email': 'TheVinhLuong@gmail.com',
    'maintainer': 'The Vinh LUONG (LƯƠNG Thế Vinh)',
    'maintainer_email': 'TheVinhLuong@gmail.com',
    'url': 'https://GitHub.com/Django-AI/Django-Query-Graph',
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
