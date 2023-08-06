# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['new_dale_chall_readability']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4']

setup_kwargs = {
    'name': 'new-dale-chall-readability',
    'version': '1.0.10',
    'description': 'An implementation of the New Dale-Chall readability formula that closely follows the specification.',
    'long_description': '[![Tests and type-checks](https://github.com/public-law/new-dale-chall-readability/actions/workflows/python-app.yml/badge.svg)](https://github.com/public-law/new-dale-chall-readability/actions/workflows/python-app.yml) [![Maintainability](https://api.codeclimate.com/v1/badges/ef1198fa2d9246aa3c7d/maintainability)](https://codeclimate.com/github/public-law/new-dale-chall-readability/maintainability) [![PyPI version](https://badge.fury.io/py/new-dale-chall-readability.svg)](https://badge.fury.io/py/new-dale-chall-readability)\n\n\n\n# The new Dale-Chall readability formula\n\nI wrote this by ordering a copy of _Readability Revisited: The new Dale-Chall readability formula_. I used the book to code the library from scratch. \n\n\n**Installation:**\n\n```bash\n$ pip install new-dale-chall-readability\n```\n\n**Let\'s try it out:**\n\n```bash\n$ ipython\n```\n\n```python\nIn [1]: from new_dale_chall_readability import cloze_score, reading_level\n\nIn [2]: text = (\n   ...:     \'Latin for "friend of the court." It is advice formally offered \'\n   ...:     \'to the court in a brief filed by an entity interested in, but not \'\n   ...:     \'a party to, the case.\'\n   ...:     )\n\nIn [3]: reading_level(text)\nOut[3]: \'7-8\'\n\nIn [4]: cloze_score(text)\nOut[4]: 36.91\n```\n\n## What\'s a "cloze score" and "reading level"?\n\n**Cloze** is a deletion test invented by Taylor (1953). The **36.91** score, above, means that roughly that 37% of the words could be deleted and the passage could still be understood. So, a\nhigher cloze score is more readable. They "range from 58 and above for the easiest passages to 10-15 and below for the most difficult" (Chall & Dale, p. 75).\n\n**Reading level** is the grade level of the material, in years of education. The scale is from\n**1** to **16+**.\n\nSee the integration test file for text samples from the book, along with their scores. \n\n\n## Why yet another Dale-Chall readability library?\n\nIt\'s 2022 and there are probably a half-dozen implementations on PyPI.\nSo why create another one?\n\n* The existing libraries have issues that made me wonder if the results were accurate. For example:    \n  * From my reading, I saw that **reading levels** are a set of\n    ten "increasingly broad bands" (p. 75). \n    And they have labels like `3` and `7-8`.\n    The existing readability libraries treat these as floating point numbers. \n    But now I believe that an enumeration —\xa0or specifically,\n    a [Literal](https://docs.python.org/3/library/typing.html#typing.Literal) — captures the formula better:\n    `Literal["1", "2", "3", "4", "5-6", "7-8", "9-10", "11-12", "13-15", "16+"]`\n  * I also couldn\'t find a good description of this "new" Dale-Chall formula, and how the\n    existing libraries implement it.\n  * The readability scores are important for my international dictionary app: \n    It shows definitions sorted with the most readable first, to increase comprehension.\n    [The entry for amicus curiae](https://www.public.law/dictionary/entries/amicus-curiae)\n    is a good example.\n    But I was getting odd results on some pages.\n* Use Test-Driven Development to squash bugs and prevent regressions.\n* Turn examples from the book into test cases.\n* Write with modern Python. I\'m no expert, so I\'m learning as I go along. E.g., \n  * It passes Pyright strict-mode type-checking.\n  * It uses recent type enhancements like `Literal`.\n* Present a very easy API to use in any app or library.\n  * No need to instantiate an object and learn its API.\n  * Just import the needed function and call it.\n\n\nThe result is a library that provides, I think, more accurate readability scores.\n\n\n## References\n\nChall, J., & Dale, E. (1995). _Readability revisited: The new Dale-Chall readability formula_.\nBrookline Books.\n\nTaylor, W. (1953). _Cloze procedure: a new tool for measuring readability._ Journalism Quarterly, 33, 42-46.\n',
    'author': 'Robb Shecter',
    'author_email': 'robb@public.law',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/public-law/new-dale-chall-readability',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
