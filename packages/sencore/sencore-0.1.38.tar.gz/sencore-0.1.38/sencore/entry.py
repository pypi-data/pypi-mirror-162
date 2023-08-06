from sencore import VocabParser, PhraseParser, StructureParser, KGParser
from sencore.lib import explain
import click

@click.command()
@click.option("--lang", help="Specify the language", default="en", prompt="Language")
@click.option("--sentence", help="Specify the sentence", default=None)
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


@click.command()
@click.option("--lang", help="Specify the language", default="en", prompt="Language")
@click.option("--sentence", help="Specify the sentence", default=None)
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


@click.command()
@click.option("--lang", help="Specify the language", default="en", prompt="Language")
@click.option("--sentence", help="Specify the sentence", default=None)
def structure(lang, sentence):
  sentences = {
      "en": "Apple is looking at buying U.K. startup for $1 billion.",
      "es": "En 1941, fue llamado a filas para incorporarse a la Armada.",
      "de": "Für Joachim Löw ist ein Nationalmannschafts-Comeback von Thomas Müller und Mats Hummels nicht mehr kategorisch ausgeschlossen.",
      "fr": "Nos jolis canards vont-ils détrôner les poules, coqueluches des jardiniers ?",
  }

  sen = sentence or sentences[lang]
  print(sen)
  sp = StructureParser(lang)
  structures = sp.digest(sen)
  print(structures)

@click.command()
@click.option("--lang", help="Specify the language", default="en", prompt="Language")
@click.option("--sentence", help="Specify the sentence", default=None)
def kg(lang, sentence):
  sentences = {
      "en": "Apple is looking at buying U.K. startup for $1 billion.",
      "es": "En 1941, fue llamado a filas para incorporarse a la Armada.",
      "de": "Für Joachim Löw ist ein Nationalmannschafts-Comeback von Thomas Müller und Mats Hummels nicht mehr kategorisch ausgeschlossen.",
      "fr": "Nos jolis canards vont-ils détrôner les poules, coqueluches des jardiniers ?",
  }

  sen = sentence or sentences[lang]
  print(sen)
  kgp = KGParser(lang, labels=["VERB"])
  translator = kgp.get_translator("cn")
  kgs = kgp.digest(sen)
  result = explain(kgs, translator)
  print(result)

