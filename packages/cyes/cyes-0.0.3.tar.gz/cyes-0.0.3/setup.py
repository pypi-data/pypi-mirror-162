# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cyes']

package_data = \
{'': ['*']}

install_requires = \
['anytree>=2.8.0,<3.0.0', 'typer[all]>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['cyes = cyes.main:app']}

setup_kwargs = {
    'name': 'cyes',
    'version': '0.0.3',
    'description': 'C Yet Exist Semicolon - C-like without {;}',
    'long_description': '<h1 align="center">\n  <a href="https://github.com/ju-djangun/cyes">\n    <img src="https://user-images.githubusercontent.com/104500082/183290529-92a8b30e-4766-42df-957e-cb3d247a5f5f.svg" alt="Logo" height="300">\n  </a>\n</h1>\n\n<div align="center">\n  Cyes - C without {;}&nbsp;&nbsp;&nbsp; :hammer:\n  <br />\n  <br />\n  <br />\n  <a href="https://github.com/ju-djangun/cyes/issues/new?assignees=&labels=bug&template=01_BUG_REPORT.md&title=bug%3A+">Report a Bug</a>\n  ·\n  <a href="https://github.com/ju-djangun/cyes/issues/new?assignees=&labels=enhancement&template=02_FEATURE_REQUEST.md&title=feat%3A+">Request a Feature</a>\n  .\n  <a href="https://github.com/ju-djangun/cyes/issues/new?assignees=&labels=question&template=04_SUPPORT_QUESTION.md&title=support%3A+">Ask a Question</a>\n</div>\n\n<!-- shields here -->\n<div align="center">\n  <br />\n\n  [![Project license](https://img.shields.io/github/license/ju-djangun/cyes.svg?style=flat-square)](LICENSE)\n</div>\n\n<details open="open">\n<summary>Table of Contents</summary>\n\n- [About](#about)\n  - [Built With](#built-with)\n- [Getting started](#getting-started)\n  - [Prerequisites](#prerequisites)\n- [Motivation](#motivation)\n- [FAQ](#faq)\n- [Contributing](#contributing)\n- [License](#license)\n\n\n\n</details>\n\n----\n\n\n\n## About\n\n\'cyes\' is the transcompiler for Pythonistas who should code with C-like language(C/C++/C#...). \n\nIt is simple, idiot CLI tool that auto semicolons&braces inserting by python-like 4-spacing indent and colons.\n\nFor this project, you can use both \'C-yes\' and \'cy-es\' depending on your preference. \n\n<br />\n<br />\n\n\'cyes\'는 C-like 프로그래밍 언어(C/C++/C#...)를 써야 하는 파이썬 개발자를 위한 트랜스파일러입니다.\n\n간단하고 멍청하게 파이썬처럼 4개 공백문자와 쌍점으로 세미콜론과 중괄호를 자동 삽입하는 CLI 툴입니다.\n\n취향껏 \'C-yes(씨-예스)\'나 \'cy-es(싸이-스)\'로 부르시면 됩니다.\n\n\n### Built With\n\n- python3.6+\n- [typer](https://github.com/tiangolo/typer)\n- [anytree](https://github.com/c0fec0de/anytree)\n- [poetry](https://python-poetry.org/)\n- [amazing-github-template](https://github.com/dec0dOS/amazing-github-template)\n\n\n## Getting started\n\n### Prerequisites\n\n> Python 3.8 or higher\n\n\n## Motivation\n\n1. studying transpiler\n2. My little finger is more important than C language tradition.\n\n<br />\n<br />\n\n1. 트랜스파일러(컴파일러 및 형식 언어) 공부를 위한 토이 프로젝트\n2. 새끼손가락을 아껴 사용합시다.\n\n\n## FAQ\n## Contributing\n\nThanks for taking the time to contribute.\n\n<br />\n<br />\n\n기여에 관심을 가져주셔서 감사합니다.\n\n\n\n\n## License\n\nThis project is licensed under the **MIT license**.\n\nSee [LICENSE](LICENSE) for more information.\n\n<br />\n<br />\n\n이 프로젝트는 MIT 라이선스를 따릅니다.\n\n[LICENSE](LICENSE) 파일에서 전문을 확인하실 수 있습니다.\n\n\n',
    'author': 'ju-djangun',
    'author_email': 'ju@djangun.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
