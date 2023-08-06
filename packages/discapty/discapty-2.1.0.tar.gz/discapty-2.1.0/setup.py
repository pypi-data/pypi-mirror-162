# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['discapty', 'discapty.wheezylib']

package_data = \
{'': ['*'], 'discapty': ['fonts/*']}

install_requires = \
['pillow>=8.4.0,<9.0.0', 'pydantic>=1.9.1,<2.0.0']

extras_require = \
{'docs': ['furo>=2022.6.21,<2023.0.0',
          'Sphinx>=4.4.0,<5.0.0',
          'sphinx-copybutton>=0.5.0,<0.6.0']}

setup_kwargs = {
    'name': 'discapty',
    'version': '2.1.0',
    'description': 'DisCapTy help you generate obfuscated images, leaving your code easy.',
    'long_description': '# DisCapTy\n\n![DisCapTy\'s Logo](.github/logo.png#gh-dark-mode-only)![DisCapTy\'s Logo](.github/logo-dark.png#gh-light-mode-only)\n\nDisCapTy is a highly type hinted Python module to generate Captcha images without struggling your mind on how to make your own. Everyone can use it!\n\n**Documentation:** <https://discapty.readthedocs.io/>\n\n<div align="center">\n    <a href="https://pypi.org/project/DisCapTy/">\n        <img src="https://img.shields.io/pypi/v/discapty?style=flat-square" alt="DisCapTy\'s Version" />\n        <img src="https://img.shields.io/pypi/pyversions/discapty?style=flat-square" alt="Python Version Required" />\n        <img src="https://img.shields.io/pypi/dm/discapty?color=blue&style=flat-square" alt="DisCapTy\'s download" />\n    </a>\n    <a href="https://discapty.readthedocs.io/en/latest/?badge=latest">\n        <img src="https://readthedocs.org/projects/discapty/badge/?version=latest&style=flat-square" alt="Documentation Status" />\n    </a>\n</div>\n\n## Installing\n\nDisCapTy is available on PyPi!\n\n```sh\npip3 install discapty\n```\n\nTo use DisCapTy, you need a Python version equal or greater to `3.7` and below `3.11`.\n\n## Clone & Test the project\n\nThis project is dependant of [Poetry](https://python-poetry.org), a dependency management tool. You are most likely going to require this tool to correctly interact with the project & its dependencies, check out [Poetry\'s documentation](https://python-poetry.org/docs) for how to install it.\n\nTo clone the repository: `git clone https://github.com/Predeactor/DisCapTy.git`\n\nTo install dependencies: `poetry install`\n\nTo run tests: `poetry run python -m unittest`\n\n## Creating Captcha\n\nFor DisCapTy, a Captcha is simply a code with any possible objects that can be returned, for example, it is one code (Like "12345") with an image (Usually a `PIL.Image.Image` object)\nThis is because DisCapTy uses the concept of generators that are used to generate a captcha from a given code, and it can return anything.\n\nDisCapTy comes with 3 builtin generators:\n\n- TextGenerator : Text based captcha\n- WheezyGenerator : Image based captcha\n- ImageGenerator : Image based captcha\n\n### Creating Captcha manually\n\n```py\nimport discapty\n\ndef generate_a_captcha(initial_input: str) -> discapty.Captcha:\n    # This generator returns an obfuscated text.\n    captcha_for_user = discapty.TextGenerator().generate(initial_input)\n    # Create a Captcha object, the first argument is the clear code, the second is the obfuscated code. Anything goes.\n    return discapty.Captcha(initial_input, captcha_for_user)\n\n# Generate your Captcha.\ncaptcha = generate_a_captcha("12345")\n\n# Show the obfuscated code. See https://discapty.readthedocs.io for more information on this object.\nshow_captcha_to_user(captcha.captcha)\n```\n\n### Checking user\'s input\n\n```py\nimport discapty\n\n# Generate your Captcha.\ncaptcha: discapty.Captcha = generate_a_captcha("12345")\n\n# This is your user\'s input here\nuser_input: str = \'12345\'\n\nif captcha.check(user_input) is True:\n    # The user input is correct\n    print("Correct!")\nelse:\n    # The user input is incorrect\n    print("Incorrect!")\n```\n\nWhat\'s great with the `.check` method is that you can specify if you need to remove space in the user\'s input and/or check casing.\n\nCreating Captcha manually is not a recommended way, because DisCapTy comes with its opinionated challenge runner & is inefficient anyway.\n\n### Create a Challenge\n\n```py\nimport discapty\n\nchallenge = discapty.Challenge(discapty.TextGenerator(), retries=3)\n\ncaptcha = challenge.begin()\n\n# We cannot provide typehint here, `captcha` is a `typing.Any` and cannot help you, it\'ll be your\n# job to know what you\'ll get as a captcha.\nsend_captcha_to_user(captcha)\nuser_input: str = get_user_input()\n\nis_correct: bool = challenge.check(user_input)\n# If the user\'s input is correct, the challenge ends, if not, `challenge.attempted_tries` will get\n# +1, and if it is greater than the retries that has been set, then an error is raised when using\n# `.check`\n```\n\nPlease see the [documentation](https://discapty.readthedocs.io/) for more information on how the library work.\n\n## Contact\n\nYou can join my Discord server for any help: <https://discord.gg/aPVupKAxxP>\n\nDisCapTy is an open-source project distributed under the MIT license:\n![PyPI - License](https://img.shields.io/pypi/l/discapty?style=flat-square)\n\nDisCapTy uses the [Roboto](https://fonts.google.com/specimen/Roboto) font as default font.\n[This font](https://fonts.google.com/specimen/Roboto) is licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0).\n',
    'author': 'Predeactor',
    'author_email': 'predeactor0@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Predeactor/DisCapTy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
