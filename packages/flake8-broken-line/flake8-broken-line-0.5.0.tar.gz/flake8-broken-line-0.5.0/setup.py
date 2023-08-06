# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['flake8_broken_line']
install_requires = \
['flake8>=3.5,<6']

entry_points = \
{'flake8.extension': ['N4 = flake8_broken_line:check_line_breaks']}

setup_kwargs = {
    'name': 'flake8-broken-line',
    'version': '0.5.0',
    'description': 'Flake8 plugin to forbid backslashes for line breaks',
    'long_description': '# flake8-broken-line\n\n[![wemake.services](https://img.shields.io/badge/-wemake.services-green.svg?label=%20&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC%2FxhBQAAAAFzUkdCAK7OHOkAAAAbUExURQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP%2F%2F%2F5TvxDIAAAAIdFJOUwAjRA8xXANAL%2Bv0SAAAADNJREFUGNNjYCAIOJjRBdBFWMkVQeGzcHAwksJnAPPZGOGAASzPzAEHEGVsLExQwE7YswCb7AFZSF3bbAAAAABJRU5ErkJggg%3D%3D)](https://wemake-services.github.io)\n[![Build Status](https://github.com/wemake-services/flake8-broken-line/workflows/test/badge.svg?branch=master&event=push)](https://github.com/wemake-services/flake8-broken-line/actions?query=workflow%3Atest)\n[![codecov](https://codecov.io/gh/wemake-services/flake8-broken-line/branch/master/graph/badge.svg)](https://codecov.io/gh/wemake-services/flake8-broken-line)\n[![Python Version](https://img.shields.io/pypi/pyversions/flake8-broken-line.svg)](https://pypi.org/project/flake8-broken-line/)\n[![PyPI version](https://badge.fury.io/py/flake8-broken-line.svg)](https://pypi.org/project/flake8-broken-line/) [![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n\nDo not break the line! 🚨\n\n\n## Installation\n\n```bash\npip install flake8-broken-line\n```\n\nIt is also a valuable part of [`wemake-python-styleguide`](https://github.com/wemake-services/wemake-python-styleguide).\n\n\n## Code example\n\nThings we check with this plugin:\n\n```python\n# String line breaks, use `()` or `"""` instead:\n\nsome_string = \'first line\\\nsecond line\'\n\n# Use a single line, `()`, or new variables instead:\n\nif 1 == 1 and \\\n    2 == 2:\n    print(\'Do not do that!\')\n\n# Do not use for method chaining:\nsome_object \\\n  .call_method(param1, param2) \\\n  .call_other(keyword=value) \\\n  .finalize()\n\n# Instead use:\nsome_objects.call_method(\n    param1, param2,\n).call_other(\n    keyword=value\n).finalize()\n\n```\n\n\n## Error codes\n\n| Error code |                   Description                  |\n|:----------:|:----------------------------------------------:|\n|    N400    | Found backslash that is used for line breaking |\n\n\n## License\n\nMIT.\n',
    'author': 'Nikita Sobolev',
    'author_email': 'mail@sobolevn.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wemake-services/flake8-broken-line',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
