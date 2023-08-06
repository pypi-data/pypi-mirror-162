# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['commands', 'kithon']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=2.11.2,<4.0.0', 'PyYaml>=5.4.0', 'typer>=0.4.0,<0.5.0']

extras_require = \
{':extra == "add-langs" or extra == "all"': ['hy<2.0'],
 ':extra == "pyx" or extra == "all"': ['packed>=0.2,<0.3'],
 'add-langs': ['coconut>=1.6.0,<2.0.0'],
 'all': ['coconut>=1.6.0,<2.0.0',
         'pexpect>=4.8.0,<5.0.0',
         'ptpython>=3.0.20,<4.0.0',
         'watchdog>=2.1.7,<3.0.0'],
 'doc': ['mkdocs>=1.1.2,<2.0.0',
         'mkdocs-material>=8.1.4,<9.0.0',
         'mdx-include>=1.4.1,<2.0.0'],
 'repl': ['pexpect>=4.8.0,<5.0.0', 'ptpython>=3.0.20,<4.0.0'],
 'watch': ['watchdog>=2.1.7,<3.0.0']}

entry_points = \
{'console_scripts': ['kithon = commands:kithon']}

setup_kwargs = {
    'name': 'kithon',
    'version': '0.4.0',
    'description': 'transpiler python into other languages',
    'long_description': '**Kithon** is a project that provides the ability to translate python and python-family language such as\n[hy-lang](https://github.com/hylang/hy) and [coconut](https://github.com/evhub/coconut)\ninto human-readable code in any other programming languages.\n\n**[Try out the web demo](https://alploskov.github.io/kithon-site/demo/)** or install locally: `pip install kithon`. Then you can use generation to `js` or `go` or create custom transpiler.\n\n**Example**\n\n```python\n# main.py\n\ndef main():\n    print(\'Hello, Kithon\')\n\nmain()\n```\n---\n`kithon gen --to js main.py`, output:\n```js\nfunction main() {\n    console.log("Hello, Kithon");\n}\nmain();\n```\n---\n`kithon gen --to go main.py`, output:\n```go\npackage main\nimport (\n\t"fmt"\n)\n\nfunc main() {\n    fmt.Println("Hello, Kithon")\n}\n```\n\nFor what?\n---------\n\nFor use python where we can\'t. For example in browser(js), embedded scripting(mostly lua).\nOr make python program faster by translating to go, c++, rust, nim or julia.\nAlso for supporting program written on in unpopular programming languages (very new or vice versa)\n\nHow it works?\n-------------\n\nKithon uses a dsl based on yaml and jinja to apply the rules described on it to the nodes of the ast tree. \nUsing this dsl you can add new languages or extensions to those already added.\n\nStatus\n------\n\nThe project is under active development.\nNow the ability to add translation of basic python constructs into any other language(in this repo js and go only) is supported.\n\nThere are plans to develop a number of supported languages and expand support for python syntax\n\nSimilar projects\n----------------\n\n* [py2many](https://github.com/adsharma/py2many)\n* [pseudo](https://github.com/pseudo-lang/pseudo)\n',
    'author': 'Aleksey Ploskov',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/alploskov/kithon',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9.0,<3.11',
}


setup(**setup_kwargs)
