from spacy.language import Language 
from spacy.tokens import Doc

_d2c = {
  "nsubj": "主语",
  "csubj": "主语",
  "nsubjpass": "主语", 
  "advmod": "状语",
  "dative": "间接宾语",
  "pobj": "宾语",
  "intj": "感叹语",
  "aux": "助动词",
  "neg": "否定词",
  "auxpass": "助动词",
  "cc": "连词",
  "preconj": "连词",
  "acomp": "表语",
  "expl": "形式主语",
  "agent": "状语",
  "mark": "连词",
  "prt": "小品词",
  "dep": "其他",
}

verb_tags = {
  "VBZ": "动词第三人称单数",
  "VBN": "动词过去分词",
  "VBG": "动词现在分词",
  "VBD": "动词过去式",
  "VB": "动词原形",
  "VBP": "动词原形",
}

cop_verbs = ["be", "prove", "seem", "remain", "get", "look", "feel", "sound", "turn", "smell", "taste", "become", "appear", "grow", "go", "run", "fall", "stay", "keep", "hold", "rest", "emerge"]

svp_enumeration = ["put forth", "come down", "put down", "put aside", "fall through"]

def _get_root_explanation(doc, r, structure):
  ele = doc[r["element"]]
  #deps = [doc[s["element"]].dep_ for s in structure]
  deps = [t.dep_ for t in ele.children]
  explanation = None
  if ele.pos_ not in ["VERB", "AUX"]:
    explanation = None
  elif ele.lemma_=="have" and doc[r["end"]-1].text=="to":
    explanation = "半助动词"
  elif r["end"]-r["start"] > 1:
    explanation = "动词成语"
  elif "expl" in deps and ele.lemma_ == "be": # There be
    explanation = verb_tags[ele.tag_]
  elif ele.text == "going" and "aux" in deps and doc[ele.i+1].text == "to":
    explanation = verb_tags[ele.tag_]
  elif ele.lemma_ in cop_verbs and any([e in ["attr", "oprd", "acomp", "xcomp", "prep"] for e in deps]):  
    explanation = "系动词"
  elif ele.pos_ == "AUX" and any([e in ["advmod", "ccomp"] for e in deps]):  
    explanation = "系动词"
  elif ele.tag_ in verb_tags.keys():
    explanation = verb_tags[ele.tag_]
  else:
    explanation = ele.tag_ 
  return explanation

def _get_aux_explanation(doc, c, structure):
  ele = doc[c["element"]]
  if ele.text == "to":
    explanation = "介词"
  else:
    explanation = "助动词"
  return explanation
  
def _get_conj_explanation(doc, c, structure):
  explanation = None
  ele = doc[c["element"]]
  if c["end"] - c["start"] == 1 and doc[c["element"]].pos_ in ["VERB", "AUX"] and ele.tag_ in verb_tags.keys():
    explanation = verb_tags[ele.tag_]
  else:
    explanation = "并列连句"
  return explanation

def _get_oprd_explanation(doc, o, structure):
  deps = [doc[s["element"]].dep_ for s in structure]
  explanation = None
  if any([e in ["dobj", "auxpass"] for e in deps]):  
    explanation = "补语"
  else:
    explanation = "表语"
  return explanation

def _get_attr_explanation(doc, o, structure):
  deps = [doc[s["element"]].dep_ for s in structure]
  explanation = None
  if any([e in ["expl"] for e in deps]):  
    explanation = "主语"
  else:
    explanation = "表语"
  return explanation

def _get_npadvmod_explanation(doc, t, structure):
  explanation = None
  if t["end"] - t["start"] == 1 and doc[t["element"]].pos_ in ["PROPN", "NOUN"]:
    explanation = "其他"
  else:
    explanation = "状语"
  return explanation
  
def _get_prep_explanation(doc, t, structure):
  root = doc[t["element"]].head
  explanation = None
  deps = [s.dep_ for s in root.children]
  explanation = None
  if root.lemma_ in cop_verbs and t["end"]-t["start"]==1 and all([e not in ["attr", "oprd", "acomp"] for e in deps]):
    explanation = "表语"
  elif t["end"]-t["start"]==1:
    explanation = "介词"
  else:
    explanation = "状语"
  return explanation

def _get_dobj_explanation(doc, t, structure):
  deps = [doc[s["element"]].dep_ for s in structure]
  explanation = None
  if any([e in ["dative"] for e in deps]):  
    explanation = "直接宾语"
  elif any([e in ["ccomp"] for e in deps]):  
    #explanation = "间接宾语"
    explanation = "宾语" 
  else:
    explanation = "宾语"
  return explanation
 
def _get_xcomp_explanation(doc, t, structure):
  root = doc[t["element"]].head
  deps = [doc[s["element"]].dep_ for s in structure]
  explanation = None
  if root.lemma_ in cop_verbs and t["end"]-t["start"]==1:# and all([e not in ["attr", "oprd", "acomp", "prep"] for e in deps]):
    explanation = "表语"
  elif "dobj" in deps and doc[t["element"]].tag_ in ["VBG"]:
    explanation = "补语"
  elif "dobj" in deps:
    explanation = "直接宾语"
  else:
    explanation = "其他"
  return explanation
 
def _get_ccomp_explanation(doc, t, structure): # TBD
  #deps = [doc[s["element"]].dep_ for s in structure]
  ele  = doc[t["element"]]
  ele_children_deps = [c.dep_ for c in ele.children]
  root = doc[t["element"]].head
  deps = [doc[s["element"]].dep_ for s in structure]
  explanation = None
  if "nsubj" in ele_children_deps and t["element"] < root.i:
    explanation = "并列句"
  elif root.pos_ == "AUX":
    explanation = "表语"
  elif "dobj" in deps:
    explanation = "直接宾语"
  else:
    explanation = "其他"
  return explanation
 
def _get_advcl_explanation(doc, t, structure):
  deps = [doc[s["element"]].dep_ for s in structure]
  root = doc[t["element"]].head
  #cop_deps = ["acomp", "prep", "attr", "oprd"]
  #if root.pos_ == "AUX" and all([d not in deps for d in cop_deps])
  #  explanation = "表语"
  #else:
  explanation = "状语"
  return explanation
 
def _get_advmod_explanation(doc, t, structure):
  deps = [doc[s["element"]].dep_ for s in structure]
  root = doc[t["element"]].head
  cop_deps = ["acomp", "prep", "attr", "oprd"]
  if root.pos_ == "AUX" and all([d not in deps for d in cop_deps]) and doc[t["element"]].pos_ not in ["SCONJ"]:
    explanation = "表语"
  elif t["end"] - t["start"] == 1 and " ".join([root.lemma_, t["text"]]) in svp_enumeration:
    explanation = "小品词"
  else:
    explanation = "状语"
  return explanation
 
def _analyze(doc, t, structure):
  #dep = doc[t["element"]].dep_
  dep = t["semantic_dep"]
  name = "_get_{}_explanation".format(dep.lower()) 
  if dep in ["punct"]:
    explanation = None
  elif name in globals().keys():
    explanation = globals()[name](doc, t, structure)
  elif dep in _d2c.keys():
    explanation = _d2c[dep]
  else:
    explanation = dep
  t["explanation"] = explanation
  return t

def en_trs(doc, structure):
  structure_with_explanation = []
  for t in structure:
    _t = _analyze(doc, t, structure)
    structure_with_explanation.append(_t)
  return structure_with_explanation
