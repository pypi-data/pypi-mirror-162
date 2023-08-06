from spacy.language import Language 
from spacy.tokens import Doc
from .morph_translation import trans_morph

_es2c = {
  "cop": "系动词",
  "obj": "宾语",
  "iobj": "间接宾语",
  "nsubj": "主语",
  "aux": "助动词",
  "advmod": "状语",
  "advcl": "状语",
  "obl": "状语",
  "expl:pv": "自复代词",
  "conj": "并列句",
}


def _get_root_explanation(doc, t, structure):
  ele = doc[t["element"]]
  deps = [s.dep_ for s in ele.children]
 
  if "cop" in deps:
    return "表语"
  if ele.pos_ in ["AUX", "VERB"]:
    return "动词:" + trans_morph(ele.morph)
  else:
    return ele.dep_

def _analyze(doc, t, structure):
  dep = doc[t["element"]].dep_
  explanation = None

  if dep == "ROOT":
    explanation = _get_root_explanation(doc, t, structure)  
  elif dep in _es2c.keys():
    explanation = _es2c[dep]
  elif dep in ["punct", "dep"]:
    explanation = None
  else:
    explanation = dep
  t["explanation"] = explanation
  return t

def es_trs(doc, structure):
  structure_with_explanation = []
  for t in structure:
    _t = _analyze(doc, t, structure)
    structure_with_explanation.append(_t)
  return structure_with_explanation
