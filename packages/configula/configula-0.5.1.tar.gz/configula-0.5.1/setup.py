# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['configula']

package_data = \
{'': ['*']}

install_requires = \
['tomlkit>=0.7.2,<0.8.0']

setup_kwargs = {
    'name': 'configula',
    'version': '0.5.1',
    'description': 'Merges configuration from toml file and environment variables',
    'long_description': "# Configula\n\nCreates a single configuration by merging settings defined in:\n    1. in environment variables\n    2. in toml file\n\nValues provided in **environment variables have priority** over values from \ntoml configuration file.\n\nBy default all environment variables are prefixed with 'PAPERMERGE'.\nBy default `__` (two underscores) is used as delimiter in environment variables\nnames. For example, given following toml file:\n\n    [main]\n    secret_key = 1234\n    [ocr]\n    default_language = 'deu'\n\ncorespondent environment variables names are PAPERMERGE__MAIN__SECRET_KEY and\nPAPERMERGE__OCR__DEFAULT_LANGUAGE - notice two underscores separate section name\nfrom prefix and variable name.\nEnvironment variable name format is (all in uppercase):\n\n     <prefix><delimiter><section_name><delimiter><variable_name>\n\n\nAlthough in toml files you can place variable names outside sections, in Papermerge\nall variables **must be placed in sections**.\n\nBy default Configula looks up for following toml file:\n\n- /etc/papermerge/papermerge.toml\n- /etc/papermerge.toml\n- papermerge.toml\n\nIf you have custom location (or custom file name), use ``PAPERMERGE__CONFIG``\n(notice double underscores) environment variable to point to it:\n\n    PAPERMERGE__CONFIG=/app/config/pm.toml\n\n\n## Installation\n\n    $ poetry add configula\n\n## Usage\n\n    from configula import Configula\n \n    config = Configula()\n    \n    default_language = config.get('ocr', 'default_language')\n    secret_key = config.get('main', 'secret_key')\n\nWhere ``papermerge.toml`` has the following content:\n\n    [main]\n    secret_key = 5432\n\n    [ocr]\n    default_language = 'deu'\n\nDefault language can be overwritten by environment\nvariable `PAPERMERGE__OCR__DEFAULT_LANGUAGE` and secret_key can overwritten\nby environment variable `PAPERMERGE__MAIN__SECRET_KEY`\n\nIf you want to read variable from a section use\n`configula.get(section, var_name, default_value)` method.\n",
    'author': 'Eugen Ciur',
    'author_email': 'eugen@papermerge.com',
    'maintainer': 'Eugen Ciur',
    'maintainer_email': 'eugen@papermerge.com',
    'url': 'https://github.com/papermerge/configula',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<=3.10.6',
}


setup(**setup_kwargs)
