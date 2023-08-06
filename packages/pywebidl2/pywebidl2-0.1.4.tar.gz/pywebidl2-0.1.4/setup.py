# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pywebidl2', 'pywebidl2.generated']

package_data = \
{'': ['*']}

install_requires = \
['antlr4-python3-runtime>=4.10,<5.0',
 'attrs>=22.1.0,<23.0.0',
 'click>=8.1.3,<9.0.0',
 'more-itertools>=8.13.0,<9.0.0',
 'stringcase>=1.2.0,<2.0.0']

setup_kwargs = {
    'name': 'pywebidl2',
    'version': '0.1.4',
    'description': 'WebIDL tool',
    'long_description': '# pywebidl2\n[![Build Status](https://github.com/PrVrSs/pywebidl2/workflows/test/badge.svg?branch=master&event=push)](https://github.com/PrVrSs/pywebidl2/actions?query=workflow%3Atest)\n[![Codecov](https://codecov.io/gh/PrVrSs/pywebidl2/branch/master/graph/badge.svg)](https://codecov.io/gh/PrVrSs/pywebidl2)\n[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/PrVrSs/pywebidl2/blob/master/LICENSE)\n[![Python Version](https://img.shields.io/badge/python-3.10-blue)](https://www.python.org/)\n\n## Description\n\n*This is a tool for the [Web IDL](https://heycam.github.io/webidl/) language.*\n\n## Quick start\n\n```shell script\npip install pywebidl2\n```\n\n## Tests\n\n```shell script\nmake test\n```\n\n## Antlr\n\n### Install\n\n[Getting Started with ANTLR v4](https://github.com/antlr/antlr4/blob/master/doc/getting-started.md)\n\n### Update parser\n```shell script\nantlr4 -o generated -no-listener -visitor -Dlanguage=Python3  WebIDLParser.g4 WebIDLLexer.g4\n```\n\n## Example\n\n### Parser\n\n```\ninterface B {\n  void g([AllowAny] DOMString s);\n};\n```\n\n```json\n[\n    {\n        "type": "interface",\n        "name": "B",\n        "inheritance": null,\n        "members": [\n            {\n                "type": "operation",\n                "name": "g",\n                "idl_type": {\n                    "type": "return-type",\n                    "ext_attrs": [],\n                    "generic": "",\n                    "nullable": false,\n                    "union": false,\n                    "idl_type": "void"\n                },\n                "arguments": [\n                    {\n                        "type": "argument",\n                        "name": "s",\n                        "ext_attrs": [\n                            {\n                                "type": "extended-attribute",\n                                "name": "AllowAny",\n                                "rhs": null,\n                                "arguments": []\n                            }\n                        ],\n                        "idl_type": {\n                            "type": "argument-type",\n                            "ext_attrs": [],\n                            "generic": "",\n                            "nullable": false,\n                            "union": false,\n                            "idl_type": "DOMString"\n                        },\n                        "default": null,\n                        "optional": false,\n                        "variadic": false\n                    }\n                ],\n                "ext_attrs": [],\n                "special": ""\n            }\n        ],\n        "ext_attrs": [],\n        "partial": false\n    }\n]\n```\n\n## Documentation\n\n**See** [original parser](https://github.com/w3c/webidl2.js)\n\n## Contributing\n\nAny help is welcome and appreciated.\n\n## License\n\n*pywebidl2* is licensed under the terms of the MIT License (see the file LICENSE).',
    'author': 'Sergey Reshetnikov',
    'author_email': 'resh.sersh@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/PrVrSs/pywebidl2',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
