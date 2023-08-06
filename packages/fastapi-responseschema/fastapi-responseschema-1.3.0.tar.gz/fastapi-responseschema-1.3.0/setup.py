# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_responseschema', 'fastapi_responseschema.integrations']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.66.0']

extras_require = \
{'pagination': ['fastapi-pagination>=0,<1']}

setup_kwargs = {
    'name': 'fastapi-responseschema',
    'version': '1.3.0',
    'description': 'Generic and common response schemas for FastAPI',
    'long_description': '# ☄️ FastAPI Response Schema\n[![PyPI](https://img.shields.io/pypi/v/fastapi-responseschema)](https://pypi.org/project/fastapi-responseschema/) [![PyPI - Downloads](https://img.shields.io/pypi/dd/fastapi-responseschema)](https://pypi.org/project/fastapi-responseschema/) [![Commits](https://img.shields.io/github/last-commit/acwazz/fastapi-responseschema)](https://github.com/acwazz/fastapi-responseschema/commit/master) [![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/acwazz/fastapi-responseschema)](https://github.com/acwazz/fastapi-responseschema/releases) \n\n> FastAPI Response Schema is still **experimental and in active development**. \n> \n> Consider `1.x.x` versions for *Alpha* and *Beta* stages.\n> Stable API functionality and usage will be released from version `2.0.0`.\n\n## Overview\nThis package extends the [FastAPI](https://fastapi.tiangolo.com/) response model schema allowing you to have a common response wrapper via a `fastapi.routing.APIRoute`.\n\nThis library supports Python versions **>=3.8** and FastAPI versions **>=0.66.0**.\n\n\n## Getting started\n\n### Install the package\n```sh\npip install fastapi-responseschema\n```\n\nIf you are planning to use the pagination integration, you can install the package including [fastapi-pagination](https://github.com/uriyyo/fastapi-pagination)\n```sh\npip install fastapi-responseschema[pagination]\n```\n\n### Usage\n\n```py\nfrom typing import Generic, TypeVar, Any, Optional, List\nfrom pydantic import BaseModel\nfrom fastapi import FastAPI\nfrom fastapi_responseschema import AbstractResponseSchema, SchemaAPIRoute, wrap_app_responses\n\n\n# Build your "Response Schema"\nclass ResponseMetadata(BaseModel):\n    error: bool\n    message: Optional[str]\n\n\nT = TypeVar("T")\n\n\nclass ResponseSchema(AbstractResponseSchema[T], Generic[T]):\n    data: T\n    meta: ResponseMetadata\n\n    @classmethod\n    def from_exception(cls, reason, status_code, message: str = "Error", **others):\n        return cls(\n            data=reason,\n            meta=ResponseMetadata(error=status_code >= 400, message=message)\n        )\n\n    @classmethod\n    def from_api_route(\n        cls, content: Any, status_code: int, description: Optional[str] = None, **others\n    ):\n        return cls(\n            data=content,\n            meta=ResponseMetadata(error=status_code >= 400, message=description)\n        )\n\n\n# Create an APIRoute\nclass Route(SchemaAPIRoute):\n    response_schema = ResponseSchema\n\n# Integrate in FastAPI app\napp = FastAPI()\nwrap_app_responses(app, Route)\n\nclass Item(BaseModel):\n    id: int\n    name: str\n\n\n@app.get("/items", response_model=List[Item], description="This is a route")\ndef get_operation():\n    return [Item(id=1, name="ciao"), Item(id=2, name="hola"), Item(id=3, name="hello")]\n```\n\nTe result of `GET /items`:\n```http\nHTTP/1.1 200 OK\ncontent-length: 131\ncontent-type: application/json\n\n{\n    "data": [\n        {\n            "id": 1,\n            "name": "ciao"\n        },\n        {\n            "id": 2,\n            "name": "hola"\n        },\n        {\n            "id": 3,\n            "name": "hello"\n        }\n    ],\n    "meta": {\n        "error": false,\n        "message": "This is a route"\n    }\n}\n```\n\n\n## Contributing\n\nContributions are very welcome!\n\n### How to contribute\nJust open an issue or submit a pull request on [GitHub](https://github.com/acwazz/fastapi-responseschema).\n\nWhile submitting a pull request describe what changes have been made.\n\n',
    'author': 'Emanuele Addis',
    'author_email': 'ustarjem.acwazz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://acwazz.github.io/fastapi-responseschema/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
