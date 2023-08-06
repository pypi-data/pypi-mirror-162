class Parser:
  """Abstract class for VocabParser, PhraseParser

  Attributes:
    lang (str): language abbreviation, e.g. ``en``, ``es``
  """

  def __init__(self, lang="en"):
    """Initialize the language
    """
    self.lang = lang

  def digest(self, sentence):
    """The child classes should handle details. Throw ``Exception`` if calling directly.
    """
    raise Exception("You have to implement method {}!!!".format("digest"))
      
