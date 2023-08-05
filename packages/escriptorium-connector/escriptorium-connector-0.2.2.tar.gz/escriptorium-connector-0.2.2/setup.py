# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['escriptorium_connector',
 'escriptorium_connector.convenience_functions',
 'escriptorium_connector.dtos',
 'escriptorium_connector.utils']

package_data = \
{'': ['*']}

install_requires = \
['alive-progress>=2.1.0,<3.0.0',
 'bs4>=0.0.1,<0.0.2',
 'colorama>=0.4.4,<0.5.0',
 'lxml>=4.6.4,<5.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'requests==2.23.0',
 'websocket-client>=1.2.1,<2.0.0']

setup_kwargs = {
    'name': 'escriptorium-connector',
    'version': '0.2.2',
    'description': 'This simple python package makes it easy to connect to an eScriptorium instance and to work with the data there.',
    'long_description': "![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)\n\n# Escriptorium Connector\n\nThis simple python package makes it easy to connect to [eScriptorium](https://gitlab.com/scripta/escriptorium) and work with the data stored there.\n\n## Installation\n\nAnd the obligatory: `pip install escriptorium-connector`\n## Usage\n\nIf you are working on a public repository, you will probably want to store your user credentials in a hidden `.env` file that does not get distributed with your code. This is pretty easy to accomplish with [python-dotenv](https://pypi.org/project/python-dotenv/). You will need to provide the connector with an eScriptorium instance URL, the API your username, and your password (see below).\n\nThe `EscriptoriumConnector` class provides (or will provide) all the methods needed to interact programmatically with the eScriptorium platform.\n\nExample usage:\n\n```python\nfrom escriptorium_connector import EscriptoriumConnector\nimport os\nfrom dotenv import load_dotenv\n\n\nif __name__ == '__main__':\n    load_dotenv()\n    url = str(os.getenv('ESCRIPTORIUM_URL'))\n    username = str(os.getenv('ESCRIPTORIUM_USERNAME'))\n    password = str(os.getenv('ESCRIPTORIUM_PASSWORD'))\n    escr = EscriptoriumConnector(url, username, password)\n    print(escr.get_documents())\n\n```\n\nAnd your `.env` file should have:\n\n```txt\nESCRIPTORIUM_URL=https://www.escriptorium.fr\nESCRIPTORIUM_USERNAME=your_escriptorium_username\nESCRIPTORIUM_PASSWORD=your_escriptorium_password\n```\n\nSee [this Jupyter notebook](https://gitlab.com/sofer_mahir/escriptorium_python_connector/-/blob/main/example.ipynb) for a longer introduction to the connector.\n\n# Development\n\nWant to contribute? There is a lot to be done here, so we are happy for any PRs and updates.\n\n## Development Environment\n\nThis project uses Poetry. To start development, please pull down the repo from GitLab and run `poetry install`, which will make sure you have all the needed dependencies for the project and that you are using a valid Python version. Please use `poetry add <your-pip-package>` to install any new dependencies to the project so that they will be tracked by poetry.\n\n### Package Structure\n\nThe escriptorium_connector package aims to provide a more or less fool-proof interface to the eScriptorium REST API. The main goal has bee to take the guess work out of what should be sent to the API in POST/PUT requests and to make very clear what one should expect to get back from a GET request. It also aims to ease introduction to the API by providing hard-coded access to all the endpoints the API provides, which might not be immediately accessible by other means.\n\nPart of the user convenience this package provides is a set of data transfer objects (DTOs) mentioned above, which take the guesswork out of API POST/PUT requests. These are available in the `src/escriptorium_connector/dtos` folder, make use of [Pydantic](https://pydantic-docs.helpmanual.io) for (de)serialization, and should all be exposed only from the `dtos` package module `src/escriptorium_connector/dtos/__init__.py` not the root level. A tentative, automated dump of the latest eScriptorium DTOs from the Django DRF is found in the file `./src/escriptorium_connector/dtos/escriptorium_schema.py`, sometimes the info there is helpful, other times it is not.\n\nThe connector itself, `src/escriptorium_connector/connector.py`,provides high level functionality on top of some lower level actions. The class it provides, `EscriptoriumConnector`, takes care of acquiring the needed JWTs and cookies from an eScriptorium web server and needs only to be provided with the server URL, a username, and a password. The `EscriptoriumConnector` creates a special requests `http` instance that takes care of retries on 500 errors and some other niceties for error reporting (see the error classes in `src/escriptorium_connector/connector_errors.py`). It maintains its own HTTP session and uses websockets to listen for the completion of requests that return immediately from the server, but then notify the user later via websocket/email that the requested action has completed.\n\nAny bespoke utility type functions should be placed in the `src/escriptorium_connector/utils` folder. No functionality there should be exposed at the project root.\n\nHigh level functions using the API such as the `copy_documents*` functions, which provide a convenience layer over multiple discrete API transactions, should be placed in the `src/escriptorium_connector/convenience_functions` but should nevertheless be reexported at the root level of the package for easy user access.\n\nAs a final goal, all functionality exposed by the `EscriptoriumConnector` will have clearly typed arguments and return types. All endpoints should be tested at least to some degree (see the `tests` folder) and code coverage can be checked when running `poetry run pytest` with the proper settings in `setup.cfg` (see the notes at the end of that file). The current code coverage can be viewed in the `htmlconv` folder. \n\nThe escriptorium_connector package should be versioned in line with the [eScriptorium](https://gitlab.com/scripta/escriptorium) project, since different versions of eScriptorium will change their API surface and we cannot expect all production servers to be running the same version. Currently the latest version of the eScriptorium server is at version 0.10.2a, so the corresponding connector version should match at 0.10.2a, and any bugfixes to that version should be numbered as 0.10.2a.post1, 0.10.2a.post2, ..., 0.10.2a.postN. This will enable users to quickly verify they are using a connector that is compatible with the server they are accessing. __Note that the package has not yet reached full API coverage for any eScriptorium version, and thus it remains on a non-related version system.__\n\n### Tests\n\nIt would be nice to get as much test covereage as possible in order to detect breaking changes in the eScriptorium API. Tests are found in the `./tests` folder and can be run with `poetry run pytest --cov-config=.coveragerc`, which will generate a nice code coverage report in HTML in the `./htmlcov` folder. Since we will probably support several version of eScriptorium you will need to make sure that the line `registry.gitlab.com/scripta/escriptorium:latest` in `escriptorium_docker/docker-compose.yml` points to the correct escriptorium image (in place of `:latest`).\n\n## Uploading to Pypi\n\nPoetry makes uploading to Pypi very easy. Just confirm that all the package details in `pyproject.toml` are correct, bump the version of the package `poetry version 0.0.15`, and then use `poetry publish --build --username $PYPI_USERNAME --password $PYPI_PASSWORD`, assuming you have set the environment variables `$PYPI_USERNAME` and `$PYPI_PASSWORD` appropriately (if you are using a Pypi token, then `PYPI_USERNAME=__token__` and `$PYPI_PASSWORD=<your-full-pypi-token>`).\n\nYou should create a new git tag and push it after you publish:\n\n    git tag v0.0.15\n    git push --tags\n\n## Docker\n\nThis repo contains a working docker-compose setup in `escriptorium_docker` (go there and run `docker-compose up -d`). The account settings there (see `escriptorium_docker/variables.env`) match those in `.env`. This docker-compose application must be running for the escriptorium tests to run and is generally useful for safe testing of the connector without damaging a production instance of eScriptorium.\n\nThe escriptorium-pgp-setup repository contains WSL oriented instructions on running a local copy of e-scriptorium.\n\n## Version History\n\n* 0.2.2 - Support new escriptorium fields\n        - Deprecation warning on the copy-documents module.\n* 0.2.0 - Add bulk transription operations.\n        - Add a read timeout parameter to the connector\n* 0.1.28 - Increase websocket timeout when downloading large transcriptions\n* 0.1.22 - Add an optional `archived` field to GetAbbreviatedTranscription\n* 0.1.21 - add bulk_update of lines\n         - allow retrieved lines to have no mask\n* 0.1.20 - add support for the move lines endpoint (for reordering lines)\n* 0.1.11 - allow the owner field of the project DTO to be a string (as is with more recent e-scriptoirum versions)\n* 0.1.9 - update the convenience function copy_documents to work with the latest e-scriptorium",
    'author': 'Bronson Brown-deVost',
    'author_email': 'bronsonbdevost@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/sofer_mahir/escriptorium_python_connector',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
