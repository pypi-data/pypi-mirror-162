# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['classopt']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'classopt',
    'version': '0.1.9',
    'description': 'Arguments parser with class for Python, inspired by StructOpt',
    'long_description': '<h1 align="center">Welcome to ClassOpt 👋</h1>\n<p>\n  <img alt="Version" src="https://img.shields.io/pypi/v/classopt" />\n  <a href="https://github.com/moisutsu/classopt/blob/main/LICENSE" target="_blank">\n    <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg" />\n  </a>\n  <a href="https://twitter.com/moisutsu" target="_blank">\n    <img alt="Twitter: moisutsu" src="https://img.shields.io/twitter/follow/moisutsu.svg?style=social" />\n  </a>\n</p>\n\n> Arguments parser with class for Python, inspired by [StructOpt](https://github.com/TeXitoi/structopt)\n\n## Install\n\n```sh\npip install classopt\n```\n\n## Usage\n\n\nImport `classopt` and define the Opt class with decorator.\n\n```python\nfrom classopt import classopt\n\n@classopt(default_long=True)\nclass Opt:\n    file: str\n    count: int = 3\n    numbers: list[int]\n    flag: bool\n\nif __name__ == "__main__":\n    opt = Opt.from_args()\n    print(opt)\n    print(opt.file)\n```\n\nRun with command line arguments.\n\n```bash\n$ python example.py --file example.txt --numbers 1 2 3 --flag\nOpt(file=\'example.txt\', count=3, numbers=[1, 2, 3], flag=True)\nexample.txt\n```\nYou can specify most of the arguments to [argparse.ArgumentParser.add_argument](https://docs.python.org/ja/3/library/argparse.html#argparse.ArgumentParser.add_argument) in `config` (except name_or_flags).\n\n\n```python\nfrom classopt import classopt, config\n\n@classopt\nclass Opt:\n    file: str\n    count: int = config(long=True)\n    numbers: list = config(long=True, short=True, nargs="+", type=int)\n    flag: bool = config(long=True, action="store_false")\n\nif __name__ == "__main__":\n    opt = Opt.from_args()\n    print(opt)\n```\n\n```bash\n$ python example.py example.txt --count 5 -n 1 2 3 --flag\nOpt(file=\'example.txt\', count=5, numbers=[1, 2, 3], flag=False)\n```\n\nSome details\n```python\n# `default_long=True` is equivalent to `config(long=True)\' for all members\n# Similarly, you can do `default_short=True`\n@classopt(default_long=True)\nclass Opt:\n    # `long=False` overrides `default_long=True`\n    file: str = config(long=False)\n\n    # equivalent to `numbers: list = config(nargs="*", type=int)`\n    # and `numbers: typing.List[int]`\n    numbers: list[int]\n\n    # equivalent to `flag: bool = config(action="store_true")`\n    flag: bool\n```\n\n### Other Way\n\nYou can also define an argument parser by inheriting from `ClassOpt`.\n\n```python\nfrom classopt import ClassOpt, config\n\nclass Opt(ClassOpt):\n    file: str\n    count: int = config(long=True)\n    numbers: list[int] = config(long=True, short="-c")\n    flag: bool = config(long=True)\n\nif __name__ == "__main__":\n    opt = Opt.from_args()\n    print(opt)\n    print(opt.file)\n```\n\nRun with command line arguments.\n\n```bash\n$ python example.py example.txt --count 5 -c 1 2 3 --flag\nOpt(file=\'example.txt\', count=5, numbers=[1, 2, 3], flag=True)\nexample.txt\n```\n\nThe inherited method does not support some features and may disappear in the future.\nSo we recommend the decorator method.\n\n## Run tests\n\n```sh\npoetry run pytest\n```\n\n## Author\n\n👤 **moisutsu**\n\n* Twitter: [@moisutsu](https://twitter.com/moisutsu)\n* Github: [@moisutsu](https://github.com/moisutsu)\n\n## Show your support\n\nGive a ⭐️ if this project helped you!\n\n## 📝 License\n\nCopyright © 2021 [moisutsu](https://github.com/moisutsu).<br />\nThis project is [MIT](https://github.com/moisutsu/classopt/blob/main/LICENSE) licensed.\n\n***\n_This README was generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_\n',
    'author': 'moisutsu',
    'author_email': 'moisutsu@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/moisutsu/classopt',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
