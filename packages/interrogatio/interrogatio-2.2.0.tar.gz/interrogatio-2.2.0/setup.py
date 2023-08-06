# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['interrogatio',
 'interrogatio.core',
 'interrogatio.handlers',
 'interrogatio.shortcuts',
 'interrogatio.themes',
 'interrogatio.validators',
 'interrogatio.widgets']

package_data = \
{'': ['*'], 'interrogatio.themes': ['theme_files/*']}

install_requires = \
['prompt-toolkit>=3.0.29',
 'pytz>=2022.1,<2023.0',
 'tzlocal>=4.1,<5.0',
 'validators>=0.18.2,<0.19.0']

extras_require = \
{'yaml': ['PyYAML>=5']}

entry_points = \
{'console_scripts': ['dialogus = interrogatio.main:main_dialogus',
                     'interrogatio = interrogatio.main:main_interrogatio']}

setup_kwargs = {
    'name': 'interrogatio',
    'version': '2.2.0',
    'description': 'Prompting library for terminals.',
    'long_description': '#\xa0interrogatio\n\n![Python versions](https://img.shields.io/pypi/pyversions/interrogatio.svg) [![PyPi Status](https://img.shields.io/pypi/v/interrogatio.svg)](https://pypi.org/project/interrogatio/) ![Read the Docs](https://img.shields.io/readthedocs/interrogatio) [![Build Status](https://img.shields.io/github/workflow/status/ffaraone/interrogatio/Build%20interrogatio)](https://github.com/ffaraone/interrogatio/actions) [![codecov](https://codecov.io/gh/ffaraone/interrogatio/branch/master/graph/badge.svg)](https://codecov.io/gh/ffaraone/interrogatio)\n\n\nA python library to prompt users for inputs in a terminal application.\n\n\n## What is interrogatio\n\n`interrogatio` is a python 3.8+ library based on the [python-prompt-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) and inspired by [PyInquirer](https://github.com/CITGuru/PyInquirer/) that help CLI developers to ask users for inputs.\n\nQuestions can be rendered onto the terminal prompt or as curses-like dialogs.\n\n\n## Documentation\n\n[`interrogatio` documentation](https://interrogatio.readthedocs.io/en/latest/) is hosted on _Read the Docs_.\n\n\n\n## Getting started\n\n\n### Requirements\n\n`interrogatio` depends on the python-prompt-toolkit library and its dependencies.\n\n### Installation\n\n\n#### Using pip\n\n\n```\n$ pip install interrogatio\n```\n\n\n#### Extra dependencies\n\nIf you want to use the shell command with yml files you can install the yml dependency:\n\n```\n$ pip install interrogatio[yml]\n```\n\n\n### Basic usage\n\n`interrogatio` needs a list of questions to prompt the user for answers.\n\nEach question is a python dictionary with at least the following keys:\n\n* **name**: it has to be unique within the list of questions. It represents the variable name;\n* **type**: the type of question;\n* **message**: the text of the prompt.\n\nOptionally you should specify:\n    \n* a **default**: a default value;\n* a **validators**: a list of children of Validator class\n* a **values**: a list of tuples (value, label) to provide a list of choices \n    for the ``selectone`` or ``selectmany`` question types.\n\n\n`interrogatio` can run into two modes: dialog and prompt.\n\n#### Dialog mode\n\n![Dialog mode showcase](docs/showcase/dialogus.gif)\n\n```\nfrom interrogatio import dialogus\n\nquestions = [\n    {\n        \'name\': \'name\',\n        \'type\': \'input\',\n        \'message\': "What\'s your name ?",\n        \'description\': \'Please enter your full name. This field is required.\',\n        \'validators\': [{\'name\': \'required\'}],\n    },\n    {\n        \'name\': \'birth_date\',\n        \'type\': \'date\',\n        \'message\': "What\'s your birth date ?",\n        \'description\': \'Enter your birth date.\',\n    },\n    {\n        \'name\': \'nationality\',\n        \'type\': \'selectone\',\n        \'message\': "What\'s your nationality ?",\n        \'description\': \'Please choose one from the list.\',\n        \'validators\': [{\'name\': \'required\'}],\n        \'values\': [\n            (\'IT\', \'Italian\'),\n            (\'ES\', \'Spanish\'),\n            (\'US\', \'American\'),\n            (\'UK\', \'English\'),\n        ],\n    },\n    {\n        \'name\': \'languages\',\n        \'type\': \'selectmany\',\n        \'message\': "What are your favorite programming languages ?",\n        \'description\': \'Please choose your favorites from the list.\',\n        \'values\': [\n            (\'py\', \'Python\'),\n            (\'rb\', \'Ruby\'),\n            (\'js\', \'Javascript\'),\n            (\'go\', \'Golang\'),\n            (\'rs\', \'Rust\'),\n            (\'c\', \'C\'),\n            (\'cpp\', \'C++\'),\n            (\'java\', \'Java\'),\n        ],\n    },\n]\n\nintro = """<blue>Welcome to <b><i>interrogatio 2.0</i></b>!\n\nThis is the second major release of interrogatio with nice improvements.</blue>\n\n<b>What\'s new</b>\n<b>----------</b>\n\n* Curses-like dialog experience had been completely rewritten.\n* New questions handlers for dates, date ranges and masked inputs.\n* Validators are now based on the <u>validators</u> library.\n"""\n\n\nanswers = dialogus(questions, \'interrogatio showcase\', intro=intro, summary=True)\n```\n\n#### Prompt mode\n\n![Prompt mode showcase](docs/showcase/interrogatio.gif)\n\n```\nfrom interrogatio import interrogatio\n\nquestions = [\n    {\n        \'name\': \'name\',\n        \'type\': \'input\',\n        \'message\': "What\'s your name ?",\n        \'description\': \'Please enter your full name. This field is required.\',\n        \'validators\': [{\'name\': \'required\'}],\n    },\n    {\n        \'name\': \'birth_date\',\n        \'type\': \'date\',\n        \'message\': "What\'s your birth date ?",\n        \'description\': \'Enter your birth date.\',\n    },\n    {\n        \'name\': \'nationality\',\n        \'type\': \'selectone\',\n        \'message\': "What\'s your nationality ?",\n        \'description\': \'Please choose one from the list.\',\n        \'validators\': [{\'name\': \'required\'}],\n        \'values\': [\n            (\'IT\', \'Italian\'),\n            (\'ES\', \'Spanish\'),\n            (\'US\', \'American\'),\n            (\'UK\', \'English\'),\n        ],\n    },\n    {\n        \'name\': \'languages\',\n        \'type\': \'selectmany\',\n        \'message\': "What are your favorite programming languages ?",\n        \'description\': \'Please choose your favorites from the list.\',\n        \'values\': [\n            (\'py\', \'Python\'),\n            (\'rb\', \'Ruby\'),\n            (\'js\', \'Javascript\'),\n            (\'go\', \'Golang\'),\n            (\'rs\', \'Rust\'),\n            (\'c\', \'C\'),\n            (\'cpp\', \'C++\'),\n            (\'java\', \'Java\'),\n        ],\n    },\n]\n\n\nanswers = interrogatio(questions)\n```\n\n### Contributing\n\nIf you want to contribute to the project, you can submit bugs, feature requests or fork the github repository and submit your pull request.\n\n\n### License\n\n`interrogatio` is released under the [BSD 3-Clause "New" or "Revised" License](https://opensource.org/licenses/BSD-3-Clause>).\n',
    'author': 'Francesco Faraone',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ffaraone/interrogatio',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
