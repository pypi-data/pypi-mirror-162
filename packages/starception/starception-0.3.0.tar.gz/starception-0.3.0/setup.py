# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['starception']

package_data = \
{'': ['*'], 'starception': ['templates/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0', 'MarkupSafe>=2,<3', 'starlette>=0,<1']

setup_kwargs = {
    'name': 'starception',
    'version': '0.3.0',
    'description': 'Beautiful debugging page for Starlette apps.',
    'long_description': "# Starception\n\nBeautiful exception page for Starlette and FastAPI apps.\n\n![PyPI](https://img.shields.io/pypi/v/starception)\n![GitHub Workflow Status](https://img.shields.io/github/workflow/status/alex-oleshkevich/starception/Lint)\n![GitHub](https://img.shields.io/github/license/alex-oleshkevich/starception)\n![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/starception)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/starception)\n![GitHub Release Date](https://img.shields.io/github/release-date/alex-oleshkevich/starception)\n![Lines of code](https://img.shields.io/tokei/lines/github/alex-oleshkevich/starception)\n\n## Installation\n\nInstall `starception` using PIP or poetry:\n\n```bash\npip install starception\n# or\npoetry add starception\n```\n\n## Screenshot\n\n![image](screenshot.png)\n\n## Features\n\n* secrets masking\n* solution hints\n* code snippets\n* display request info: query, body, headers, cookies\n* session contents\n* request and app state\n* platform information\n* environment variables\n\nThe middleware will automatically mask any value which key contains `key`, `secret`, `token`, `password`.\n\n## Quick start\n\nSee example application in [examples/](examples/) directory of this repository.\n\n## Usage\n\nTo render a beautiful exception page you need to install a `StarceptionMiddleware` middleware to your application.\n\n> The middleware will work only in debug mode so don't forget to set `debug=True` for local development.\n\n> Note, to catch at many exceptions as possible the middleware has to be the first one in the stack.\n\n```python\nimport typing\n\nfrom starlette.applications import Starlette\nfrom starlette.middleware import Middleware\nfrom starlette.requests import Request\nfrom starlette.routing import Route\n\nfrom starception import StarceptionMiddleware\n\n\nasync def index_view(request: Request) -> typing.NoReturn:\n    raise TypeError('Oops, something really went wrong...')\n\n\napp = Starlette(\n    debug=True,\n    routes=[Route('/', index_view)],\n    middleware=[\n        Middleware(StarceptionMiddleware),\n        # other middleware go here\n    ],\n)\n```\n\n### Integration with FastAPI\n\nCreate a FastAPI exception handler and register it with your app:\n\n```python\nimport typing\n\nfrom fastapi import FastAPI, Request\n\nfrom starception import StarceptionMiddleware\n\napp = FastAPI(debug=True)\napp.add_middleware(StarceptionMiddleware)  # must be the first one!\n\n\n@app.route('/')\nasync def index_view(request: Request) -> typing.NoReturn:\n    raise TypeError('Oops, something really went wrong...')\n```\n\n## Solution hints\n\nIf exception class has `solution` attribute then its content will be used as a solution hint.\n\n```python\nclass WithHintError(Exception):\n    solution = (\n        'The connection to the database cannot be established. '\n        'Either the database server is down or connection credentials are invalid.'\n    )\n```\n\n![image](hints.png)\n\n## Credentials\n\n* Look and feel inspired by [Phoenix Framework](https://www.phoenixframework.org/).\n",
    'author': 'Alex Oleshkevich',
    'author_email': 'alex.oleshkevich@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/alex-oleshkevich/starception',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0,<4.0.0',
}


setup(**setup_kwargs)
