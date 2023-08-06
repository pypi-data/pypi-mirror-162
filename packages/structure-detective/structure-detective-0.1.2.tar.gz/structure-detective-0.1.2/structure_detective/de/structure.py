from spacy.language import Language 
from spacy.tokens import Doc
from structure_detective.lib import form_children_info, get_children_except_xs

def _is_verb_like(e):
  return e.pos_ in ["VERB", "AUX"]

def _has_no_subject(e):
  children_deps = [x.dep_ for x in e.children]
  return all([subj not in children_deps for subj in ["sb", "sbp", "pm"]])

def _get_root(doc: Doc):
  print(doc.text)
  roots = [r for r in doc if r.dep_=="ROOT"]
  if len(roots)>=1:
    root = roots[0]
  else:
    root = None
  return root

def _handle_backward_ocs(ocs:list, doc:Doc):
  store = []
  if len(ocs) == 0:
    return store
  else:
    for oc in ocs:
      regular_oc_children = get_children_except_xs(oc, ["oc"])
      store.extend(form_children_info(doc, regular_oc_children))

      start, end = oc.i, oc.i+1
      _info = {
        "start": start,
        "end": end,
        "text": doc[start:end].text,
        "element": oc.i,
        "is_root": False,
      }
      store.append(_info)
 
      oc_children = [occ for occ in oc.children if occ.dep_=="oc"]
      store.extend(_handle_backward_ocs(oc_children, doc))
    return store

def _handle_oc(doc: Doc, nlp: Language):
  store = []
  # append ROOT
  root = _get_root(doc)
  start, end = root.i, root.i+1
  _info = {
    "start": start,
    "end": end,
    "text": doc[start:end].text,
    "element": root.i, 
    "is_root": True,
  }
  store.append(_info)

  # No oc
  ocs =  [t for t in root.children if t.dep_ == "oc"]
  if len(ocs) == 0:
    return store

  oc = ocs[0]
  
  no_need_to_dig = not _is_verb_like(oc) or "sb" in [t.dep_ for t in oc.children] or "ep" in [t.dep_ for t in oc.children]
  if no_need_to_dig:
    # oc IS NOT verb like
    store.extend(form_children_info(doc, [oc]))
    return store
  else:
    # oc IS verb like 
    regular_oc_children = get_children_except_xs(oc, ["pm", "oc"])
    store.extend(form_children_info(doc, regular_oc_children))

    # handle oc node with/without zu
    zu_children = [t for t in oc.children if t.dep_ in ["pm"] and t.text == "zu" and t.i == oc.i-1]
    if len(zu_children) == 1:
      start, end = oc.i-1, oc.i+1 
    else:
      start, end = oc.i, oc.i+1
    _info = {
      "start": start,
      "end": end,
      "text": doc[start:end].text,
      "element": oc.i,
      "is_root": False,
    }
    store.append(_info)

    # handle forward oc
    oc_forward_children = [t for t in oc.children if t.dep_ == "oc" and t.i>oc.i]
    store.extend(form_children_info(doc, oc_forward_children))

    # handle backward oc
    oc_backward_children = [t for t in oc.children if t.dep_ == "oc" and t.i<oc.i]
    store.extend(_handle_backward_ocs(oc_backward_children, doc))
    return store    

def get_tree(doc: Doc, nlp: Language):
  root = _get_root(doc)
  if root == None:
    return []

  if _is_verb_like(root):
    xs = ["oc"]
    children = [r for r in root.children if r.dep_ not in xs]
    store = form_children_info(doc, children)
  
    oc_store = _handle_oc(doc, nlp)
    store.extend(oc_store)
  else:
    store = []

  ordered_store = sorted(store, key=lambda d: d["start"]) 
  return ordered_store 

