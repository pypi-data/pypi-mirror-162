# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['plaintext_analyzer']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'sencore>=0.1.38,<0.2.0', 'x2cdict>=0.1.45,<0.2.0']

entry_points = \
{'console_scripts': ['pta_phrase = plaintext_analyzer.entry:parser_phrase',
                     'pta_structure_kg = '
                     'plaintext_analyzer.entry:parser_structure_kg',
                     'pta_vocab = plaintext_analyzer.entry:parser_vocab']}

setup_kwargs = {
    'name': 'plaintext-analyzer',
    'version': '0.1.12',
    'description': '',
    'long_description': '# Installation from pip3\n\n```shell\npip3 install --verbose plaintext_analyzer \npython -m spacy download en_core_web_trf\npython -m spacy download es_dep_news_trf\n```\n\n# Usage\n\nPlease refer to [api docs](https://qishe-nlp.github.io/plaintext-analyzer/).\n\n### Excutable usage\n\n* Get vocabularies from plaintext file \n\n```shell\npta_vocab --source en_plaintext.txt --stype FILE --lang en  \n``` \n\n* Get vocabularies from text \n\n```shell\npta_vocab --source "The typical Bangladeshi breakfast consists of flour-based flatbreads such as chapati, roti or paratha, served with a curry. Usually the curry can be vegetable, home-fried potatoes, or scrambled eggs. The breakfast varies according to location and the eater\'s income. In villages and rural areas, rice with curry (potato mash, dal ) is mostly preferred by day laborers. In the city, sliced bread with jam or jelly is chosen due to time efficiency. In Bangladesh tea is preferred to coffee and is an essential part of most breakfasts. Having toasted biscuits, bread or puffed rice with tea is also very popular." --stype RAW --lang en  \n``` \n\n* Get vocabularies from plaintext file, and write to csv files \n\n```shell\npta_vocab --source en_plaintext.txt --stype FILE --lang en --dstname en_vocab\n``` \n\n* Get vocabularies from text, and write to csv file \n\n```shell\npta_vocab --source "The typical Bangladeshi breakfast consists of flour-based flatbreads such as chapati, roti or paratha, served with a curry. Usually the curry can be vegetable, home-fried potatoes, or scrambled eggs. The breakfast varies according to location and the eater\'s income. In villages and rural areas, rice with curry (potato mash, dal ) is mostly preferred by day laborers. In the city, sliced bread with jam or jelly is chosen due to time efficiency. In Bangladesh tea is preferred to coffee and is an essential part of most breakfasts. Having toasted biscuits, bread or puffed rice with tea is also very popular." --stype RAW --lang en --dstname en_vocab \n``` \n\n* Get phrases from plaintext file \n\n```shell\npta_phrase --source en_plaintext.txt --stype FILE --lang en  \n``` \n\n* Get phrases from text \n\n```shell\npta_phrase --source "The typical Bangladeshi breakfast consists of flour-based flatbreads such as chapati, roti or paratha, served with a curry. Usually the curry can be vegetable, home-fried potatoes, or scrambled eggs. The breakfast varies according to location and the eater\'s income. In villages and rural areas, rice with curry (potato mash, dal ) is mostly preferred by day laborers. In the city, sliced bread with jam or jelly is chosen due to time efficiency. In Bangladesh tea is preferred to coffee and is an essential part of most breakfasts. Having toasted biscuits, bread or puffed rice with tea is also very popular." --stype RAW --lang en  \n``` \n\n* Get phrases from plaintext file, and write to csv files \n\n```shell\npta_phrase --source en_plaintext.txt --stype FILE --lang en --dstname en_phrase\n``` \n\n* Get phrases from text, and write to csv file \n\n```shell\npta_phrase --source "The typical Bangladeshi breakfast consists of flour-based flatbreads such as chapati, roti or paratha, served with a curry. Usually the curry can be vegetable, home-fried potatoes, or scrambled eggs. The breakfast varies according to location and the eater\'s income. In villages and rural areas, rice with curry (potato mash, dal ) is mostly preferred by day laborers. In the city, sliced bread with jam or jelly is chosen due to time efficiency. In Bangladesh tea is preferred to coffee and is an essential part of most breakfasts. Having toasted biscuits, bread or puffed rice with tea is also very popular." --stype RAW --lang en --dstname en_phrase \n``` \n\n### Package usage\n```\ndef parser_vocab(source, stype, lang):\n\n  sf = PlaintextReader(source, stype, lang)\n  sens = sf.sentences\n\n  analyzer = VocabAnalyzer(lang)\n  exs = analyzer.overview_vocabs(sens)\n\n  print(exs)\n\ndef parser_phrase(source, stype, lang):\n\n  sf = PlaintextReader(source, stype, lang)\n  sens = sf.sentences\n\n  analyzer = PhraseAnalyzer(lang)\n  exs = analyzer.overview_phrases(sens)\n\n  print(exs)\n\n```\n\n# Development\n\n### Clone project\n```\ngit clone https://github.com/qishe-nlp/plaintext-analyzer.git\n```\n\n### Install [poetry](https://python-poetry.org/docs/)\n\n### Install dependencies\n```\npoetry update\n```\n\n### Test\n```\npoetry run pytest -rP\n```\nwhich run tests under `tests/*`\n\n### Execute\n```\npoetry run pta_vocab --help\npoetry run pta_phrase --help\n```\n\n### Create sphinx docs\n```\npoetry shell\ncd apidocs\nsphinx-apidoc -f -o source ../plaintext_analyzer\nmake html\npython -m http.server -d build/html\n```\n\n### Host docs on github pages\n```\ncp -rf apidocs/build/html/* docs/\n```\n\n### Build\n* Change `version` in `pyproject.toml` and `plaintext_analyzer/__init__.py`\n* Build python package by `poetry build`\n\n### Git commit and push\n\n### Publish from local dev env\n\n* Set pypi test environment variables in poetry, refer to [poetry doc](https://python-poetry.org/docs/repositories/)\n* Publish to pypi test by `poetry publish -r test`\n\n### Publish through CI \n\n* Github action build and publish package to [test pypi repo](https://test.pypi.org/)\n\n```\ngit tag [x.x.x]\ngit push origin master\n```\n\n* Manually publish to [pypi repo](https://pypi.org/) through [github action](https://github.com/qishe-nlp/plaintext-analyzer/actions/workflows/pypi.yml)\n\n',
    'author': 'Phoenix Grey',
    'author_email': 'phoenix.grey0108@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/qishe-nlp/plaintext-analyzer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
