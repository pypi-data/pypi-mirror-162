"""``sencore`` Package

.. topic:: Parse sentence into vocabularies

  .. code:: python

    from sencore import VocabParser

    def vocab(lang, sen):
      vp = VocabParser(lang)
      vocabs = vp.digest(sen)
      print(vocabs)

.. topic:: Parse sentence into phrases

  .. code:: python

    from sencore import PhraseParser

    def phrase(lang, sen):
      pp = PhraseParser(lang)
      phrases = pp.digest(sen)
      print(phrases)

"""

__version__ = '0.1.37'

#from .parser import Parser
from .vocab_parser import VocabParser
from .phrase_parser import PhraseParser
from .structure_parser import StructureParser
from .kg_parser import KGParser
