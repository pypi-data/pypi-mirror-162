# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nfl_scraper',
 'nfl_scraper.my_fantasy',
 'nfl_scraper.nfl',
 'nfl_scraper.utils']

package_data = \
{'': ['*'],
 'nfl_scraper': ['.pytest_cache/*', '.pytest_cache/v/cache/*', 'dist/*']}

install_requires = \
['bs4>=0.0.1,<0.0.2',
 'html5lib>=1.1,<2.0',
 'jsonpickle>=2.2.0,<3.0.0',
 'prompt-toolkit>=3.0.30,<4.0.0',
 'requests>=2.28.1,<3.0.0',
 'selenium>=4.3.0,<5.0.0']

extras_require = \
{':python_version < "3.10"': ['importlib-metadata>=4.4,<5.0']}

setup_kwargs = {
    'name': 'nfl-scraper',
    'version': '1.0.1',
    'description': 'Creating a scraper for multiple fantasy football sites',
    'long_description': '# fantasy-scraper\nTrying to scrape all data from our fantasy league with NFL.com. Since we are moving to Sleeper. It might end up include myfantasyleague as well\n\n\n## Pipenv and Poetry\n\nSetup\n\n```bash\ncurl -sSL https://instcurl -sSL https://install.python-poetry.org | python3 -\npipenv install --python=/usr/loca/bin/python3.10\npipenv shell\npoetry completions bash >> ~/.bash_completion\n#export PIP_PYTHON_PATH="$VIRTUAL_ENV/bin/python3"\npoetry new nfl_scraper\npoetry new nfl_scraper\n#pipenv install --index=pip\n#pipenv install --index=distutils\npoetry add requests\npoetry add html5lib\npoetry add bs4\n\n\n#pip uninstall -y setuptools\n#exit\n#deactivate \n```\n\n## Running as Non Dev\n\n```shell\npoetry install --without dev --sync\npoetry run python -V\n# Help\npoetry run python main.py -h \n# Sub out the params\npoetry run python main.py -e <email> -p <password> -i <id> -n <name>\n# Test need to beef these up\npoetry run pytest\n```\n\n## Running as Dev\n\n```shell\npoetry check\npoetry build\n#poetry update #gets latest package version\n\n```\n\n## Running in CICD\n\n```shell\npoetry check\n# output version\npoetry version -s\n\npoetry version major|minor|patch --dry-run\n```\n',
    'author': 'DeadlyChambers',
    'author_email': 'shanechambers85@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DeadlyChambers/fantasy-scraper',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
