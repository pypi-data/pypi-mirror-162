# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bologna']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'bologna',
    'version': '0.2.2',
    'description': 'A tiny no-faff dependency injection module for python.',
    'long_description': '# Bologna\nA tiny no-faff dependency injection module for python.\n\nBologna, formerly called tinyDI, is a tiny easy-to-use dependency injection library for python. \nThis project has mainly evolved as a utility library for some\nof my other projects, and is thus very utilitarian in its approach.\nAs the source code is only 100-ish lines, extending it is very easy.\n\n\n\n\n## Usage\n\n- Declare injectable dependencies with the `provide` function:\n\n```python\n\nfrom bologna import provide\nfrom datetime import date\n\nmy_injectable_string = "Hello, DI. Today is"\nmy_injectable_object = date.today()\n\nprovide("greeting", my_injectable_string)\nprovide("thedate", my_injectable_object)\n```\nevery injectable needs a unique name, which will be the function argument names.\n \n- Mark functions that need to have arguments injected by the ´@inject´ annotation:\n\n```python\n\nfrom bologna import inject\n\n\n@inject\ndef print_date(greeting=None, thedate=None):\n    print(f"{greeting}; {thedate}")\n\n\nprint_date()\n# prints \'Hello, DI. Today is; 2022-07-21\'\n```\n\n\n## Features\nWhat is included:\n\n- Async function support\n\n\nWhat is **not** included:\n\n- Lazy evaluation\n- Singletons\n- ...And pretty much any other feature that is included in most full-fledged DI packages.\n\n\n## Building and contributing\nThis project is built with `poetry` on 3.9.\n\nTo build, clone the repo and run `poetry install`. To run the tests, run `poetry run pytest`, to package, run `poetry build`.\n\n\n## License\nMIT license\n```\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files\n(the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge,\npublish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,\nsubject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO\nTHE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF\nCONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER\nDEALINGS IN THE SOFTWARE.\n```\n',
    'author': 'Anton Leagre',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aap007freak/tinydi',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
