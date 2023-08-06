from sencore.parser import Parser
import spacy

class VocabParser(Parser):
  """``VocabParser`` is to detect vocabularies from sentence. Inherit ``Parser``, implements ``digest``.
  """

  _pkgindices = {
    "en": "en_core_web_trf",
    "es": "es_dep_news_trf",
    "de": "de_dep_news_trf",
    "fr": "fr_dep_news_trf",
  }

  def __init__(self, lang):
    """Initialize nlp processor according to language

    Args:
      lang (str): language abbreviation
    """

    super().__init__(lang) 
    self._nlp = spacy.load(self.__class__._pkgindices[lang])

  def digest(self, sentence):
    """Parse sentence into vocabularies with linguistic meta info

    Args:
      sentence (str): sentence to be parsed

    Returns:
      list: element is a dict, with keys ``word`` and ``pos``
    """

    doc = self._nlp(sentence)
    return [{'word': e.text, 'pos': e.pos_} for e in doc]
    
