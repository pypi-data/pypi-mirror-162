from spacy.language import Language 
from spacy.tokens import Doc
from importlib import import_module

class Structure:

  def __init__(self, nlp: Language): 
    lang = nlp.meta["lang"]
    self.ext_name = "structure"
    self.pkg = 'structure_detective.{}.structure'.format(lang)
    self.nlp = nlp
    
    if not Doc.has_extension(self.ext_name):
      Doc.set_extension(self.ext_name, default={})

  def __call__(self, doc: Doc):
    pkg_module = import_module(self.pkg)    
    fn = getattr(pkg_module, 'get_tree')
    doc._.structure = fn(doc, self.nlp) 
    return doc

def trs(doc, structure: dict, lang: str):
  pkg = 'structure_detective.{}.trans_structure'.format(lang)
  pkg_module = import_module(pkg)    
  fn = getattr(pkg_module, '{}_trs'.format(lang))
  return fn(doc, structure)
