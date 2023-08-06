# Installation 

### Install from pip3
``` 
pip3 install --verbose sencore
```

### Install spacy lib
```
python -m spacy download en_core_web_trf
python -m spacy download es_dep_news_trf
```

# Usage

Please refer to [api docs](https://qishe-nlp.github.io/sencore/).

### Executable usage
* Parse sentence into vocabs

  ```
  parse2vocab --lang en --sentence "It is a great day."
  ```

* Parse sentence into phrases

  ```
  parse2phrase --lang en --sentence "It is a great day."
  ```

### Package usage
* Parse sentence into vocabs

  ```
  from sencore import VocabParser 

  def vocab(lang, sentence):
    sentences = {
        "en": "Apple is looking at buying U.K. startup for $1 billion.",
        "es": "En 1941, fue llamado a filas para incorporarse a la Armada.",
        "de": "Für Joachim Löw ist ein Nationalmannschafts-Comeback von Thomas Müller und Mats Hummels nicht mehr kategorisch ausgeschlossen.",
        "fr": "Nos jolis canards vont-ils détrôner les poules, coqueluches des jardiniers ?",
    }

    sen = sentence or sentences[lang]
    print(sen)
    vp = VocabParser(lang)
    vocabs = vp.digest(sen)
    print(vocabs)

  ```

* Parse sentence into phrases

  ```
  from sencore import PhraseParser

  def phrase(lang, sentence):
    sentences = {
        "en": "Apple is looking at buying U.K. startup for $1 billion.",
        "es": "En 1941, fue llamado a filas para incorporarse a la Armada.",
        "de": "Für Joachim Löw ist ein Nationalmannschafts-Comeback von Thomas Müller und Mats Hummels nicht mehr kategorisch ausgeschlossen.",
        "fr": "Nos jolis canards vont-ils détrôner les poules, coqueluches des jardiniers ?",
    }

    sen = sentence or sentences[lang]
    print(sen)
    pp = PhraseParser(lang)
    phrases = pp.digest(sen)
    print(phrases)
  ```

# Development

### Clone project
```
git clone https://github.com/qishe-nlp/sencore.git
```

### Install [poetry](https://python-poetry.org/docs/)

### Install dependencies
```
poetry update
python -m spacy download en_core_web_trf
python -m spacy download es_dep_news_trf
```

### Test
```
poetry run pytest -rP
```
which run tests under `tests/*`


### Execute
```
poetry run parse_to_vocab --help
```

### Create sphinx docs
```
poetry shell
cd apidocs
sphinx-apidoc -f -o source ../sencore
make html
python -m http.server -d build/html
```

### Hose docs on github pages
```
cp -rf apidocs/build/html/* docs/
```

### Build
* Change `version` in `pyproject.toml` and `sencore/__init__.py`
* Build python package by `poetry build`

### Git commit and push

### Publish from local dev env
* Set pypi test environment variables in poetry, refer to [poetry doc](https://python-poetry.org/docs/repositories/)
* Publish to pypi test by `poetry publish -r test`

### Publish through CI 

* Github action build and publish package to [test pypi repo](https://test.pypi.org/)

```
git tag [x.x.x]
git push origin master
```

* Manually publish to [pypi repo](https://pypi.org/) through [github action](https://github.com/qishe-nlp/sencore/actions/workflows/pypi.yml)

