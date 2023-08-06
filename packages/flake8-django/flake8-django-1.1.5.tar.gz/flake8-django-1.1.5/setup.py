# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flake8_django', 'flake8_django.checkers']

package_data = \
{'': ['*']}

install_requires = \
['flake8>=3.8.4,<6']

entry_points = \
{'flake8.extension': ['DJ0 = flake8_django:DjangoStyleChecker']}

setup_kwargs = {
    'name': 'flake8-django',
    'version': '1.1.5',
    'description': 'Plugin to catch bad style specific to Django Projects.',
    'long_description': "# flake8-django\n\n[![pypi](https://img.shields.io/pypi/v/flake8-django.svg)](https://pypi.python.org/pypi/flake8-django/)\n![CI](https://github.com/rocioar/flake8-django/workflows/CI/badge.svg)[![Codecov](https://codecov.io/gh/rocioar/flake8-django/branch/master/graph/badge.svg)](https://codecov.io/gh/rocioar/flake8-django)\n[![Downloads](https://pepy.tech/badge/flake8-django)](https://pepy.tech/project/flake8-django)\n\nA flake8 plugin to detect bad practices on Django projects.\n\n## Installation\n\nInstall from pip with:\n\n```\n$ pip install flake8-django\n```\n\n## Testing\n\nflake8-django uses pytest for tests. To run them use:\n\n```\n$ pytest\n````\n\nRun coverage report using:\n\n```\n$ pytest --cov=.\n```\n\n## List of Rules\n\n| Rule | Description |\n| ---- | ----------- |\n| [`DJ01`](https://github.com/rocioar/flake8-django/wiki/%5BDJ01%5D-Avoid-using-null=True-on-string-based-fields-such-as-CharField-and-TextField) | Avoid using null=True on string-based fields such as CharField and TextField |\n| [`DJ03`](https://github.com/rocioar/flake8-django/wiki/%5BDJ03%5D-Avoid-passing-locals()-as-context-to-a-render-function) | Avoid passing locals() as context to a render function |\n| [`DJ06`](https://github.com/rocioar/flake8-django/wiki/%5BDJ06%5D-Do-not-use-exclude-with-ModelForm,-use-fields-instead) | Do not use exclude with ModelForm, use fields instead |\n| [`DJ07`](https://github.com/rocioar/flake8-django/wiki/%5BDJ07%5D-Do-not-set-fields-to-'__all__'-on-ModelForm,-use-fields-instead) | Do not use `__all__` with ModelForm, use fields instead |\n| [`DJ08`](https://github.com/rocioar/flake8-django/wiki/%5BDJ08%5D-Model-does-not-define-__str__-method) | Model does not define `__str__` method |\n| [`DJ12`](https://github.com/rocioar/flake8-django/wiki/%5BDJ12%5D-Order-of-Model's-inner-classes,-methods,-and-fields-does-not-follow-the-Django-Style-Guide) | Order of Model's inner classes, methods, and fields does not follow the [Django Style Guide](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/#model-style) |\n| [`DJ13`](https://github.com/rocioar/flake8-django/wiki/DJ13---@receiver-decorator-must-be-on-top-of-all-the-other-decorators) | @receiver decorator must be on top of all the other decorators |\n\nMore details about each of the Rules can be found on the [wiki page](https://github.com/rocioar/flake8-django/wiki).\n\n## Optional Rules - Disabled by Default\n\n| Rule | Description |\n| ---- | ----------- |\n| [`DJ10`](https://github.com/rocioar/flake8-django/wiki/%5BDJ10%5D-Model-should-define-verbose_name-on-its-Meta-inner-class) | Model should define verbose_name on its Meta inner class |\n| [`DJ11`](https://github.com/rocioar/flake8-django/wiki/%5BDJ11%5D-Model-should-define-verbose_name_plural-on-its-Meta-inner-class) | Model should define verbose_name_plural on its Meta inner class |\n\nTo enable optional rules you can use the `--select` parameter. It's default values are: E,F,W,C90.\n\nFor example, if you wanted to enable `DJ10`, you could call `flake8` in the following way:\n```\nflake8 --select=E,F,W,C90,DJ,DJ10\n```\n\nYou could also add it to your configuration file:\n```\n[flake8]\nmax-line-length = 120\n...\nselect = C,E,F,W,DJ,DJ10\n```\n\n## Licence\n\nGPL\n\n## Thanks\n\n[@stummjr](https://github.com/stummjr) for teaching me AST, and what I could do with it. His [blog](https://stummjr.org/post/building-a-custom-flake8-plugin/) is cool.\n",
    'author': 'Rocio Aramberri Schegel',
    'author_email': 'rocio.aramberri@schegel.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rocioar/flake8-django',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
