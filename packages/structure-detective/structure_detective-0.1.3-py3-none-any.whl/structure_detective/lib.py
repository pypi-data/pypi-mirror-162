from spacy.language import Language 
from spacy.tokens import Doc, Token

def has_dep(token:Token, dep:str):
  token_children_deps = [t.dep_ for t in token.children]
  return dep in token_children_deps


def get_children_except_xs(token:Token, xs:list):
  return [t for t in token.children if t.dep_ not in xs] 
  
def get_subtree_except_xs(token:Token, xs:list):
  xs_subtrees = [list(x.subtree) for x in token.children if x.dep_ in xs]

  excluded_subtree = sum(xs_subtrees, [])
  included_subtree = [s for s in token.subtree if s not in excluded_subtree]
  return included_subtree
 
def is_top(t:Token, ts:list):
  return all([t.is_ancestor(x) for x in ts if t!=x])

def form_children_info(doc:Doc, children:list):
  store = []
  #print(doc.text)
  for dc in children:
    dc_ranges = [e.i for e in dc.subtree]
    dc_ranges.sort()
    dc_children_ids = [x.i for x in dc.children]
    #print(dc_children_ids)

    length = len(dc_ranges)
    current = 0
    subtrees = [[dc_ranges[0]]]
    for i in range(length-1):
      a, b = dc_ranges[i], dc_ranges[i+1] 
      if a == b-1:
        subtrees[current].append(b) 
      else:
        current = current + 1
        subtrees.append([b])
    #print(subtrees)
    #print("="*10)
    for t in subtrees: 
      tokens = [doc[x] for x in t]
      
      heads = [h for h in tokens if is_top(h, tokens)]
      assert(len(heads)==1)
      head = heads[0]
        
      start, end = min(t), max(t)+1
      _info = {
        "start": start,
        "end": end,
        "text": doc[start:end].text,
        "element": head.i, 
        "is_root": False,
        "semantic_dep": head.dep_
      }
      store.append(_info)
  return store


