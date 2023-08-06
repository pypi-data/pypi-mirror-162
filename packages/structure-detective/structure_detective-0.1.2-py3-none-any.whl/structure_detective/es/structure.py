from spacy.language import Language 
from spacy.tokens import Doc
from structure_detective.lib import get_subtree_except_xs, form_children_info

def _is_verb_like(e):
  return e.pos_ in ["VERB", "AUX"]

def _is_noun_like(e):
  return e.pos_ in ["NOUN", "ADJ", "ADV", "PRON", "DET"]

def _has_no_subject(e):
  children_deps = [x.dep_ for x in e.children]
  return all([subj not in children_deps for subj in ["csubj"]])

def _get_root(doc: Doc):
  roots = [r for r in doc if r.dep_=="ROOT"]
  assert(len(roots)>=1)
  root = roots[0]
  return root

def get_tree(doc: Doc, nlp: Language):
  root = _get_root(doc)
  
  if _is_noun_like(root):
    xs = ["nsubj", "cop", "obl", "punct", "dep", "aux"]
    children = [r for r in root.children if r.dep_ in xs]
    store = form_children_info(doc, children)

    copula_tree = get_subtree_except_xs(root, xs)
    copula_ranges = [e.i for e in copula_tree]
    start, end = min(copula_ranges), max(copula_ranges)+1
    _info = {
      "start": start,
      "end": end,
      "text": doc[start:end].text,
      "element": root.i, 
      "is_root": True,
    }
    store.append(_info)
  elif _is_verb_like(root):
    children = [r for r in root.children]
    store = form_children_info(doc, children)

    start, end = root.i, root.i+1
    _info = {
      "start": start,
      "end": end,
      "text": doc[start:end].text,
      "element": root.i, 
      "is_root": True,
    }
    store.append(_info)
  else:
    store = []

  ordered_store = sorted(store, key=lambda d: d["start"]) 
  return ordered_store 

