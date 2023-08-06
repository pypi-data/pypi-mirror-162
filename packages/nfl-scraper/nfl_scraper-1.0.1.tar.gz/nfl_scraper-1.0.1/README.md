# fantasy-scraper
Trying to scrape all data from our fantasy league with NFL.com. Since we are moving to Sleeper. It might end up include myfantasyleague as well


## Pipenv and Poetry

Setup

```bash
curl -sSL https://instcurl -sSL https://install.python-poetry.org | python3 -
pipenv install --python=/usr/loca/bin/python3.10
pipenv shell
poetry completions bash >> ~/.bash_completion
#export PIP_PYTHON_PATH="$VIRTUAL_ENV/bin/python3"
poetry new nfl_scraper
poetry new nfl_scraper
#pipenv install --index=pip
#pipenv install --index=distutils
poetry add requests
poetry add html5lib
poetry add bs4


#pip uninstall -y setuptools
#exit
#deactivate 
```

## Running as Non Dev

```shell
poetry install --without dev --sync
poetry run python -V
# Help
poetry run python main.py -h 
# Sub out the params
poetry run python main.py -e <email> -p <password> -i <id> -n <name>
# Test need to beef these up
poetry run pytest
```

## Running as Dev

```shell
poetry check
poetry build
#poetry update #gets latest package version

```

## Running in CICD

```shell
poetry check
# output version
poetry version -s

poetry version major|minor|patch --dry-run
```
