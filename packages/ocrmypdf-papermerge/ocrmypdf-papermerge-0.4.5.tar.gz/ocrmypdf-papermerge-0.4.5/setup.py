# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ocrmypdf_papermerge']

package_data = \
{'': ['*'], 'ocrmypdf_papermerge': ['templates/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0', 'lxml>=4.9.0,<5.0.0', 'ocrmypdf>=13.5.0,<14.0.0']

setup_kwargs = {
    'name': 'ocrmypdf-papermerge',
    'version': '0.4.5',
    'description': 'OCRmyPDF plugin to generate SVG files for Papermerge',
    'long_description': '# OCRmyPDF Papermerge Plugin\n\nThis [OCRmyPDF](https://github.com/jbarlow83/OCRmyPDF) plugin is used by [Papermerge](https://github.com/papermerge/papermerge-core) to:\n\n1. generate SVG files with embedded jpeg data and text overlay\n2. generate PDF/TIFF preview images\n\nLearn more about OCRmyPDF plugin system [here](https://ocrmypdf.readthedocs.io/en/latest/plugins.html).\n\n\n## Run Tests\n\n    $ poetry run task test\n\n## Run Linting\n\n    $ poetry run task lint\n',
    'author': 'Eugen Ciur',
    'author_email': 'eugen@papermerge.com',
    'maintainer': 'Eugen Ciur',
    'maintainer_email': 'eugen@papermerge.com',
    'url': 'https://github.com/papermerge/OCRmyPDF_papermerge',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<=3.10.6',
}


setup(**setup_kwargs)
