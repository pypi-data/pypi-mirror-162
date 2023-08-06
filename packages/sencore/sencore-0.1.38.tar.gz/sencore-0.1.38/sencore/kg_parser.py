import spacy
from sencore.parser import Parser
from spacy import Language
from kg_detective import KG, PKG_INDICES
from sencore.lib import extend_ranges
import kg_detective

@Language.factory("kg", default_config={"labels": [], "rules": []})
def create_kg_parser(nlp: Language, name: str, labels: list, rules: list):
  """Register ``KG`` into pipeline with component name ``kg``
  """
  return KG(nlp, labels=labels, rules=rules)
 
class KGParser(Parser):
  """``KGParser`` is to detect knowledge graph from sentence. Inherit ``Parser``, implements ``digest``.
  """

  def __init__(self, lang: str, labels: list=[], rules: list=[]):
    """Initialize nlp processor according to language

    Args:
      lang (str): language abbreviation
    """

    super().__init__(lang) 
    self._nlp = spacy.load(PKG_INDICES[lang])
    self._nlp.add_pipe("kg", config={"labels": labels, "rules": rules})
    

  def digest(self, sentence):
    """Parse sentence into kg with linguistic meta info

    Args:
      sentence (str): sentence to be parsed

    Returns:
      dict: Keys are keys of ``kg``
    """


    doc = self._nlp(sentence)
    
    return doc._.kg

  def get_translator(self, to_lang):
    _translator = getattr(kg_detective, 'kg_{}_{}'.format(self.lang, to_lang))
    return _translator

  def __del__(self):
    self._nlp.remove_pipe("kg")
