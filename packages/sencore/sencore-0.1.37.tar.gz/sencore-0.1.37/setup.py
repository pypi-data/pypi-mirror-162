# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sencore']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0',
 'kg-detective>=0.1.4,<0.2.0',
 'phrase-detective>=0.1.32,<0.2.0',
 'spacy>=3.2.0,<4.0.0',
 'structure-detective>=0.1.3,<0.2.0']

entry_points = \
{'console_scripts': ['parse2kg = sencore.entry:kg',
                     'parse2phrase = sencore.entry:phrase',
                     'parse2structure = sencore.entry:structure',
                     'parse2vocab = sencore.entry:vocab',
                     'review_phrase = sencore.train:generate_review_phrases']}

setup_kwargs = {
    'name': 'sencore',
    'version': '0.1.37',
    'description': 'sentence nlp parser for multilingua',
    'long_description': '# Installation \n\n### Install from pip3\n``` \npip3 install --verbose sencore\n```\n\n### Install spacy lib\n```\npython -m spacy download en_core_web_trf\npython -m spacy download es_dep_news_trf\n```\n\n# Usage\n\nPlease refer to [api docs](https://qishe-nlp.github.io/sencore/).\n\n### Executable usage\n* Parse sentence into vocabs\n\n  ```\n  parse2vocab --lang en --sentence "It is a great day."\n  ```\n\n* Parse sentence into phrases\n\n  ```\n  parse2phrase --lang en --sentence "It is a great day."\n  ```\n\n### Package usage\n* Parse sentence into vocabs\n\n  ```\n  from sencore import VocabParser \n\n  def vocab(lang, sentence):\n    sentences = {\n        "en": "Apple is looking at buying U.K. startup for $1 billion.",\n        "es": "En 1941, fue llamado a filas para incorporarse a la Armada.",\n        "de": "Für Joachim Löw ist ein Nationalmannschafts-Comeback von Thomas Müller und Mats Hummels nicht mehr kategorisch ausgeschlossen.",\n        "fr": "Nos jolis canards vont-ils détrôner les poules, coqueluches des jardiniers ?",\n    }\n\n    sen = sentence or sentences[lang]\n    print(sen)\n    vp = VocabParser(lang)\n    vocabs = vp.digest(sen)\n    print(vocabs)\n\n  ```\n\n* Parse sentence into phrases\n\n  ```\n  from sencore import PhraseParser\n\n  def phrase(lang, sentence):\n    sentences = {\n        "en": "Apple is looking at buying U.K. startup for $1 billion.",\n        "es": "En 1941, fue llamado a filas para incorporarse a la Armada.",\n        "de": "Für Joachim Löw ist ein Nationalmannschafts-Comeback von Thomas Müller und Mats Hummels nicht mehr kategorisch ausgeschlossen.",\n        "fr": "Nos jolis canards vont-ils détrôner les poules, coqueluches des jardiniers ?",\n    }\n\n    sen = sentence or sentences[lang]\n    print(sen)\n    pp = PhraseParser(lang)\n    phrases = pp.digest(sen)\n    print(phrases)\n  ```\n\n# Development\n\n### Clone project\n```\ngit clone https://github.com/qishe-nlp/sencore.git\n```\n\n### Install [poetry](https://python-poetry.org/docs/)\n\n### Install dependencies\n```\npoetry update\npython -m spacy download en_core_web_trf\npython -m spacy download es_dep_news_trf\n```\n\n### Test\n```\npoetry run pytest -rP\n```\nwhich run tests under `tests/*`\n\n\n### Execute\n```\npoetry run parse_to_vocab --help\n```\n\n### Create sphinx docs\n```\npoetry shell\ncd apidocs\nsphinx-apidoc -f -o source ../sencore\nmake html\npython -m http.server -d build/html\n```\n\n### Hose docs on github pages\n```\ncp -rf apidocs/build/html/* docs/\n```\n\n### Build\n* Change `version` in `pyproject.toml` and `sencore/__init__.py`\n* Build python package by `poetry build`\n\n### Git commit and push\n\n### Publish from local dev env\n* Set pypi test environment variables in poetry, refer to [poetry doc](https://python-poetry.org/docs/repositories/)\n* Publish to pypi test by `poetry publish -r test`\n\n### Publish through CI \n\n* Github action build and publish package to [test pypi repo](https://test.pypi.org/)\n\n```\ngit tag [x.x.x]\ngit push origin master\n```\n\n* Manually publish to [pypi repo](https://pypi.org/) through [github action](https://github.com/qishe-nlp/sencore/actions/workflows/pypi.yml)\n\n',
    'author': 'Phoenix Grey',
    'author_email': 'phoenix.grey0108@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/qishe-nlp/sencore',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
