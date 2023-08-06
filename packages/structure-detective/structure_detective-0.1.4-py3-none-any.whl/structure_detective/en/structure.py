from spacy.language import Language 
from spacy.tokens import Doc, Token
from structure_detective.lib import form_children_info #, get_children_except_xs

vp1s = ["come on", "think of", "look for", "meet with", "call upon", "object to", "consist of", "make by", "make for", "look after", "agree to", "look into", "abide by", "abound in"]
vp2s = ["look down on", "look forward to", "look out for", "look out on", "carry on with", "catch up with", "come down on", "come out against", "date back to", "do away with", "face up to", "feel up to"]

def _is_verb_like(e):
  return e.pos_ in ["VERB", "AUX"]

def _has_no_subject(e):
  children_deps = [x.dep_ for x in e.children]
  return all([subj not in children_deps for subj in ["nsubj", "nsubjpass"]])

def _get_root(doc: Doc):
  roots = [r for r in doc if r.dep_=="ROOT"]
  if len(roots)>=1:
    root = roots[0]
  else:
    root = None
  return root

def _extend_root_by_vp_2(doc: Doc, root: Token):
  roots, childrens = [root], []
  if root.i+2>=len(doc):
    childrens = [[t for t in root.children]]
    return roots, childrens
  nt1, nt2 = doc[root.i+1], doc[root.i+2]
  phrase = ""
  validation = all([nt1.dep_ in ["prep", "advmod", "prt"], nt1.head == root, nt2.head in [root, nt1]])
  if validation:
    children = list(nt2.children)
    if len(children)==0 or (len(children) == 1 and children[0].dep_ == "pobj"):
      phrase = " ".join([root.lemma_, nt1.text, nt2.text])
    if phrase in vp2s:
      roots.extend([nt1, nt2])
      childrens = [[t for t in root.children if t not in [nt1, nt2]],[t for t in nt2.children]]
    else:
      childrens = [[t for t in root.children]]
  return roots, childrens

def _extend_root_by_vp_1(doc: Doc, root: Token):
  roots, childrens = [root], []
  if root.i+1>=len(doc):
    childrens = [[t for t in root.children]]
    return roots, childrens
  nt = doc[root.i+1]
  phrase = ""
  if nt.dep_ == "prep" and nt.head == root:
    children = list(nt.children)
    if len(children)==0 or (len(children) == 1 and children[0].dep_ == "pobj"):
      phrase = " ".join([root.lemma_, nt.text])
  if phrase in vp1s:
    roots.append(nt)
    childrens = [[t for t in root.children if t!=nt],[t for t in nt.children]] 
  else:
    childrens = [[t for t in root.children]]
  return roots, childrens

def _extend_root_by_half_have_to(doc: Doc, root: Token):
  roots, childrens = [root], []
  if root.i+1>=len(doc):
    childrens = [[t for t in root.children]]
    return roots, childrens
  nt = doc[root.i+1]
  phrase = " ".join([root.lemma_, nt.text])
  validation = all([phrase=="have to", nt.dep_=="aux", nt.head.dep_=="xcomp", nt.head.head==root])
  if validation:
    xcomp_token = nt.head
    roots.append(xcomp_token)
    childrens = [[t for t in root.children if t!=xcomp_token],[t for t in xcomp_token.children if t!=nt]] 
  else:
    childrens = [[t for t in root.children]]
  return roots, childrens
   

def _extend_root_by_half_have_got_to(doc: Doc, root: Token):
  roots, childrens = [root], []
  if root.i+1>=len(doc):
    childrens = [[t for t in root.children]]
    return roots, childrens
  nt = doc[root.i+1]
  phrase = " ".join([root.text, nt.text])
  aux_token_lemmas = [t.lemma_ for t in root.children if t.dep_=="aux"]
  validation = all([("have" in aux_token_lemmas or "'ve" in aux_token_lemmas) and phrase=="got to", nt.dep_=="aux", nt.head.dep_=="xcomp", nt.head.head==root])
  if validation:
    xcomp_token = nt.head
    roots.append(xcomp_token)
    childrens = [[t for t in root.children if t!=xcomp_token],[t for t in xcomp_token.children if t!=nt], [nt]] 
  else:
    childrens = [[t for t in root.children]]
  return roots, childrens

def _extend_root_by_half_be_going_to(doc: Doc, root: Token):
  roots, childrens = [root], []
  if root.i+1>=len(doc):
    childrens = [[t for t in root.children]]
    return roots, childrens
  nt = doc[root.i+1]
  phrase = " ".join([root.text, nt.text])
  aux_token_lemmas = [t.lemma_ for t in root.children if t.dep_=="aux"]
  validation = all([("be" in aux_token_lemmas) and phrase=="going to", nt.dep_=="aux", nt.head.dep_=="xcomp", nt.head.head==root])
  if validation:
    xcomp_token = nt.head
    roots.append(xcomp_token)
    childrens = [[t for t in root.children if t!=xcomp_token],[t for t in xcomp_token.children if t!=nt], [nt]] 
  else:
    childrens = [[t for t in root.children]]
  return roots, childrens

def _handle_vp_root(doc:Doc, roots: list):
  store = []
  _r_range = range(len(roots))
  for index in _r_range:
    if index < len(roots)-1:
      assert(roots[index].i+1 == roots[index+1].i)
  # append ROOT
  root = roots[0] 
  start, end = root.i, roots[-1].i+1
  _info = {
    "start": start,
    "end": end,
    "text": doc[start:end].text,
    "element": root.i, 
    "is_root": True,
    "semantic_dep": "ROOT"
  }
  store.append(_info)
  return store

def _handle_half_have_to_root(doc:Doc, roots: list):
  store = []
  # append ROOT
  for root in roots:
    start = root.i
    end = root.i+2 if root.dep_== "ROOT" and len(roots)==2 else root.i+1
    _info = {
      "start": start,
      "end": end,
      "text": doc[start:end].text,
      "element": root.i, 
      "is_root": root.dep_=="ROOT",
      "semantic_dep": "ROOT"
    }
    store.append(_info)
  return store

def _handle_half_have_got_to_root(doc:Doc, roots: list):
  store = []
  # append ROOT
  for root in roots:
    start = root.i
    end = root.i+1
    _info = {
      "start": start,
      "end": end,
      "text": doc[start:end].text,
      "element": root.i, 
      "is_root": root.dep_=="ROOT",
      "semantic_dep": "ROOT"
    }
    store.append(_info)
  return store

def _handle_half_be_going_to_root(doc:Doc, roots: list):
  store = []
  # append ROOT
  for root in roots:
    start = root.i
    end = root.i+1
    _info = {
      "start": start,
      "end": end,
      "text": doc[start:end].text,
      "element": root.i, 
      "is_root": root.dep_=="ROOT",
      "semantic_dep": "ROOT"
    }
    store.append(_info)
  return store


def _extend_root(doc: Doc, root: Token):
  # make rules
  if root.lemma_ == "have":
    roots, childrens = _extend_root_by_half_have_to(doc, root)
    store = _handle_half_have_to_root(doc, roots)
  elif root.text == "got":
    roots, childrens = _extend_root_by_half_have_got_to(doc, root)
    store = _handle_half_have_got_to_root(doc, roots)
  elif root.text == "going":
    roots, childrens = _extend_root_by_half_be_going_to(doc, root)
    store = _handle_half_be_going_to_root(doc, roots)
  else:
    roots, childrens = _extend_root_by_vp_2(doc, root)
    if len(roots) < 3:
      roots, childrens = _extend_root_by_vp_1(doc, root)
    store = _handle_vp_root(doc, roots)

  for children in childrens: 
    store.extend(form_children_info(doc, children))
  return store 

def get_tree(doc: Doc, nlp: Language):
  root = _get_root(doc)
  if root == None:
    return []

  store = []
  if _is_verb_like(root):
    store = _extend_root(doc, root) 
  ordered_store = sorted(store, key=lambda d: d["start"]) 
  return ordered_store 

