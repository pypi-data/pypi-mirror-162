# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['starception']

package_data = \
{'': ['*'], 'starception': ['templates/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0', 'MarkupSafe>=2,<3', 'starlette>=0.19,<0.20']

setup_kwargs = {
    'name': 'starception',
    'version': '0.1.1',
    'description': 'Beautiful debugging page for Starlette apps.',
    'long_description': '# Starception\n\nBeautiful debugging page for Starlette apps implemented as ASGI middleware.\n\n![PyPI](https://img.shields.io/pypi/v/starception)\n![GitHub Workflow Status](https://img.shields.io/github/workflow/status/alex-oleshkevich/starception/Lint)\n![GitHub](https://img.shields.io/github/license/alex-oleshkevich/starception)\n![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/starception)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/starception)\n![GitHub Release Date](https://img.shields.io/github/release-date/alex-oleshkevich/starception)\n![Lines of code](https://img.shields.io/tokei/lines/github/alex-oleshkevich/starception)\n\n## Installation\n\nInstall `starception` using PIP or poetry:\n\n```bash\npip install starception\n# or\npoetry add starception\n```\n\nAdd it as the first middleware in to your app:\n\n```python\napp = Starlette(\n    middleware=[\n        Middleware(StarceptionMiddleware, debug=True),\n        # other middleware here\n    ],\n)\n```\n\nNote, the middleware won\'t handle anything if `debug=False`,\ninstead it will display plain string "Internal Server Error".\nAlso, I would recommend to add it only for local development, as such error page,\nwhen enabled on prod by mistake, can expose sensitive data.\n\n### Usage with FastAPI\n\nAs this is pure ASGI middleware, you can use it with FastAPI. However, you cannot use `app.middleware` decorator\nand add it via `app.add_middleware` instead.\n\n```python\napp = FastAPI()\n\napp.add_middleware(StarceptionMiddleware, debug=True)\n```\n\nSee [FastAPI docs on middleware](https://fastapi.tiangolo.com/advanced/middleware/).\n\n## Screenshot\n\n![image](screenshot.png)\n\n## Features\n\n* secrets masking\n* solution hints\n* code snippets\n* display request info: query, body, headers, cookies\n* session contents\n* request and app state\n* platform information\n* environment variables\n\nThe middleware will automatically mask any value which key contains `key`, `secret`, `token`, `password`.\n\n## Quick start\n\nSee example application in `examples/` directory of this repository.\n\n## Solution hints\n\nIf exception class has `solution` attribute then its content will be used as a solution hint.\n\n```python\nclass WithHintError(Exception):\n    solution = (\n        \'The connection to the database cannot be established. \'\n        \'Either the database server is down or connection credentials are invalid.\'\n    )\n```\n\n![image](hints.png)\n\n## Credentials\n\n* Look and feel inspired by [Phoenix Framework](https://www.phoenixframework.org/).\n',
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
