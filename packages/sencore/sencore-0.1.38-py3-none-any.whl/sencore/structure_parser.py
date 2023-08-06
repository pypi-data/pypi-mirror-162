import spacy
from sencore.parser import Parser
from spacy import Language
from structure_detective import Structure, trs, PKG_INDICES
from sencore.lib import extend_ranges

@Language.factory("structure")
def create_structure_parser(nlp: Language, name: str):
  """Register ``Structure`` into pipeline with component name ``structure``
  """
  return Structure(nlp)

class StructureParser(Parser):
  """``StructureParser`` is to detect structure from sentence. Inherit ``Parser``, implements ``digest``.
  """

  def __init__(self, lang):
    """Initialize nlp processor according to language

    Args:
      lang (str): language abbreviation
    """

    super().__init__(lang) 
    self._nlp = spacy.load(PKG_INDICES[lang])
    self._nlp.add_pipe("structure")

  def digest(self, sentence):
    """Parse sentence into structure with linguistic meta info

    Args:
      sentence (str): sentence to be parsed

    Returns:
      list[dict]:  Keys are in ``start``, ``end``,  ``text``, ``element``, ``is_root``, ``explanation``
    """


    doc = self._nlp(sentence)
    
    return trs(doc, doc._.structure, self.lang)

  def __del__(self):
    self._nlp.remove_pipe("structure")
