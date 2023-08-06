# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['rororo', 'rororo.openapi']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.1,<7.0',
 'aiohttp-middlewares>=1.2.0,<3',
 'aiohttp>=3.7.0,<4.0.0',
 'attrs>=19.2.0,<23',
 'email-validator>=1.0.5,<2.0.0',
 'environ-config>=20.1,<23',
 'isodate>=0.6.0,<0.7.0',
 'openapi-core>=0.13.4,<0.13.7',
 'pyrsistent>=0.16,<0.19']

extras_require = \
{':python_version < "3.7"': ['contextvars>=2.4,<3.0'],
 ':python_version < "3.8"': ['typing-extensions>=3.7,<5.0']}

setup_kwargs = {
    'name': 'rororo',
    'version': '3.0.0',
    'description': 'aiohttp.web OpenAPI 3 schema first server applications.',
    'long_description': '======\nrororo\n======\n\n.. image:: https://github.com/playpauseandstop/rororo/actions/workflows/ci.yml/badge.svg\n    :target: https://github.com/playpauseandstop/rororo/actions/workflows/ci.yml\n    :alt: CI Workflow\n\n.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n    :target: https://github.com/pre-commit/pre-commit\n    :alt: pre-commit\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n    :alt: black\n\n.. image:: https://img.shields.io/pypi/v/rororo.svg\n    :target: https://pypi.org/project/rororo/\n    :alt: Latest Version\n\n.. image:: https://img.shields.io/pypi/pyversions/rororo.svg\n    :target: https://pypi.org/project/rororo/\n    :alt: Python versions\n\n.. image:: https://img.shields.io/pypi/l/rororo.svg\n    :target: https://github.com/playpauseandstop/rororo/blob/main/LICENSE\n    :alt: BSD License\n\n.. image:: https://coveralls.io/repos/playpauseandstop/rororo/badge.svg?branch=main&service=github\n    :target: https://coveralls.io/github/playpauseandstop/rororo\n    :alt: Coverage\n\n.. image:: https://readthedocs.org/projects/rororo/badge/?version=latest\n    :target: https://rororo.readthedocs.io/\n    :alt: Documentation\n\nImplement `aiohttp.web`_ `OpenAPI 3`_ server applications with schema first\napproach.\n\nAs well as bunch other utilities to build effective server applications with\n`Python`_ 3 & `aiohttp.web`_.\n\n* Works on `Python`_ 3.7+\n* Works with `aiohttp.web`_ 3.7+\n* BSD licensed\n* Source, issues, and pull requests `on GitHub\n  <https://github.com/playpauseandstop/rororo>`_\n\n.. _`OpenAPI 3`: https://spec.openapis.org/oas/v3.0.3\n.. _`aiohttp.web`: https://docs.aiohttp.org/en/stable/web.html\n.. _`Python`: https://www.python.org/\n\nQuick Start\n===========\n\n*rororo* relies on valid OpenAPI 3 schema file (both JSON or YAML formats\nsupported).\n\nExample below, illustrates on how to handle operation ``hello_world`` from\n`openapi.yaml`_ schema file.\n\n.. code-block:: python\n\n    from pathlib import Path\n    from typing import List\n\n    from aiohttp import web\n    from rororo import (\n        openapi_context,\n        OperationTableDef,\n        setup_openapi,\n    )\n\n\n    operations = OperationTableDef()\n\n\n    @operations.register\n    async def hello_world(request: web.Request) -> web.Response:\n        with openapi_context(request) as context:\n            name = context.parameters.query.get("name", "world")\n            email = context.parameters.query.get(\n                "email", "world@example.com"\n            )\n            return web.json_response(\n                {"message": f"Hello, {name}!", "email": email}\n            )\n\n\n    def create_app(argv: List[str] = None) -> web.Application:\n        return setup_openapi(\n            web.Application(),\n            Path(__file__).parent / "openapi.yaml",\n            operations,\n            server_url="/api",\n        )\n\n.. _`openapi.yaml`: https://github.com/playpauseandstop/rororo/blob/main/tests/rororo/openapi.yaml\n\nSchema First Approach\n---------------------\n\nUnlike other popular Python OpenAPI 3 solutions, such as\n`Django REST Framework`_, `FastAPI`_,  `flask-apispec`_, or `aiohttp-apispec`_\n*rororo* **requires** you to provide valid `OpenAPI 3`_ schema first. This\nmakes *rororo* similar to `connexion`_, `pyramid_openapi3`_ and other schema\nfirst libraries.\n\n.. _`Django REST Framework`: https://www.django-rest-framework.org\n.. _`FastAPI`: https://fastapi.tiangolo.com\n.. _`flask-apispec`: https://flask-apispec.readthedocs.io\n.. _`aiohttp-apispec`: https://aiohttp-apispec.readthedocs.io\n.. _`connexion`: https://connexion.readthedocs.io\n.. _`pyramid_openapi3`: https://github.com/Pylons/pyramid_openapi3\n\nClass Based Views\n-----------------\n\n*rororo* supports `class based views`_ as well. `Todo-Backend`_ example\nillustrates how to use class based views for OpenAPI 3 servers.\n\nIn snippet below, *rororo* expects that OpenAPI 3 schema contains operation ID\n``UserView.get``,\n\n.. code-block:: python\n\n    @operations.register\n    class UserView(web.View):\n        async def get(self) -> web.Response:\n            ...\n\n\n.. _`class based views`: https://docs.aiohttp.org/en/stable/web_quickstart.html#aiohttp-web-class-based-views\n.. _`Todo-Backend`: https://github.com/playpauseandstop/rororo/tree/main/examples/todobackend\n\nMore Examples\n-------------\n\nCheck `examples`_ folder to see other examples on how to build aiohttp.web\nOpenAPI 3 server applications.\n\n.. _`examples`: https://github.com/playpauseandstop/rororo/tree/main/examples\n',
    'author': 'Igor Davydenko',
    'author_email': 'iam@igordavydenko.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://igordavydenko.com/projects/#rororo',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
