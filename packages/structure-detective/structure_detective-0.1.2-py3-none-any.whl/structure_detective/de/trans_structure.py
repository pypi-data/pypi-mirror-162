from spacy.language import Language 
from spacy.tokens import Doc

_de2c = {
  "ep": "主语补足语",
  "svp": "后缀",
  "oa": "第四格补足语",
  "da": "第三格补足语",
  "pd": "表语补足语",
  "ng": "否定词",
  "op": "介词补足语",
  "cvc": "介词短语",
  "og": "第二格补足语",
  "cj": "并列句",
  "ph": "形式主语",
  "rc": "关系从句",
  "rs": "其他",
  "vo": "其他",
  "cc": "其他",
  "app": "其他",
  "dep": "其他",
  "dm": "其他",
  "par": "其他",
  "sbp": "其他",
  "mnr": "其他",
}

trans_tag = {
  "VAFIN": "限定-助动词",
  "VAINF": "不定式-助动词",
  "VAIMP": "命令式-助动词",
  "VAPP": "过去分词-助动词",

  "VVFIN": "限定-动词",
  "VVINF": "不定式-动词",
  "VVIMP": "命令式-动词",
  "VVPP": "过去分词-动词",
  "VVIZU": "带zu不定式-动词",

  "VMFIN": "限定-情态动词",
  "VMINF": "不定式-情态动词",
  "VMPP": "过去分词-情态动词"
}

adp_verbs = {
  "an": ["arbeiten", "beteiligen", "erkennen", "erkranken", "fehlt", "hindern", "leiden", "liegt", "mangelt", "sterben", "teilnehmen", "vorbeikommen", "zweifeln", "denken", "erinnern", "gewöhnen", "glauben", "grenzen", "halten", "schicken", "schreiben", "vermieten", "wenden"],
  "auf": ["achten", "beschränken", "antworten", "aufpassen", "beziehen", "einigen", "freuen", "hoffen", "hören", "konzentrieren", "reagieren", "schätzen", "schießen", "schimpfen", "spezialisieren", "stoßen", "verlassen", "verzichten", "vorbereiten", "warten", "beruhen", "bestehen"],
  "aus": ["aussteigen", "bestehen", "lernen", "machen", "stammen", "übersetzen", "zusammensetzen"],
  "bei": ["bedanken", "beschweren", "entschuldigen", "helfen", "lernen"],
  "durch": ["ersetzen"],
  "für": ["arbeiten", "bedanken", "brauchen", "danken", "einsetzen", "eignen", "eintreten", "engagieren", "entscheiden", "entschuldigen", "halten", "interessieren", "kämpfen", "rächen", "schämen", "sorgen", "stimmen", "vormerken", "werben"],
  "gegen": ["kämpfen", "protestieren", "spielen", "verstoßen", "verteidigen", "wehren", "wenden"],
  "in": ["irren", "bestehen", "einmischen", "einsteigen", "geraten", "verlieben", "verwandeln"],
  "mit": ["anfangen", "aufhören", "auskommen", "beeilen", "befassen", "beginnen", "beschäftigen", "handeln", "kämpfen", "machen", "rechnen", "schimpfen", "telefonieren", "treffen", "verabreden", "verbinden", "vergleichen", "verheiraten", "verloben", "versöhnen", "verstehen", "vertauschen", "vertragen", "verwechseln", "warten", "zögern", "zusammenstoßen"],
  "nach": ["erkundigen", "fragen", "riechen", "schmecken", "sehnen", "suchen", "umhören"],
  "über": ["ärgern", "aufregen", "sagen", "beklagen", "berichten", "beschweren", "diskutieren", "erschrecken", "freuen", "informieren", "klagen", "lachen", "nachdenken", "reden", "schimpfen", "siegen", "sprechen", "staunen", "streiten", "unterhalten", "verfügen", "wissen", "wundern"],
  "um": ["bemühen", "beneiden", "bewerben", "bitten", "geht", "handelt", "kämpfen", "kümmern", "sorgen", "spielen", "streiten", "trauern", "werben"],
  "unter": ["leiden"],
  "von": ["abhängen", "befreien", "berichten", "erholen", "ernähren", "erwarten", "erzählen", "fordern", "halten", "handeln", "hören", "leben", "lernen", "sprechen", "trennen", "träumen", "überzeugen", "unterscheiden", "verabschieden", "verlangen", "wissen"],
  "vor": ["erschrecken", "fliehen", "flüchten", "fürchten", "schützen", "warnen"],
  "zu": ["auffordern", "beitragen", "beglückwünschen", "benutzen", "bringen", "einladen", "entschließen", "ernennen", "führen", "gehören", "gratulieren", "kommt", "passen", "überreden", "raten", "verurteilen", "wählen", "werden", "zwingen"]
}

adp_verbs["ans"] = adp_verbs["am"] = adp_verbs["an"]

adp_verbs["im"] = adp_verbs["ins"] = adp_verbs["in"]

adp_verbs["zum"] = adp_verbs["ins"] = adp_verbs["zu"]

adp_verbs["aufs"] = adp_verbs["auf"]

excluded_cop_adps = ["durch", "außer", "nach", "seit", "von", "wegen", "statt", "trotz", "während", "ab", "für"]
cop_verbs = ["sein", "werden", "bleiben", "belieb"]
aux_verbs = ["sein", "haben", "werden", "habe"]
decoration_advs = ["da", "doch", "bloß", "halt", "mal", "eben", "ja", "eh", "denn", "auch", "bitte"]

def _mo_adp_explanation(doc, ele, structure):
  #roots = [doc[s["element"]] for s in structure if doc[s["element"]].dep_=="ROOT"]
  #assert(len(roots) == 1)
  #root = roots[0]
  #oc = [s for s in structure if doc[s["element"]].dep_=="oc"]
  #deps = [doc[s["element"]].dep_ for s in structure]

  if ele.head.lemma_ in cop_verbs and ele.text.lower() not in excluded_cop_adps: # and all([d not in ["oc"] for d in deps])
    return "表语补足语"
  elif ele.text not in adp_verbs.keys():
    return "其他"
  elif ele.head.lemma_ in adp_verbs[ele.text]:
    return "介词补足语"
  else:
    return "其他"

  #elif len(oc)==0 and ele.head.lemma_ in adp_verbs[ele.text]:
  #  return "介词补足语"
  #elif len(oc)==1 and oc[0]["end"]-oc[0]["start"]==1 and doc[oc[0]["element"]].lemma_ in adp_verbs[ele.text]:
  #  return "介词补足语"

def _get_root_explanation(doc, r, structure):
  ele = doc[r["element"]]
  deps = [doc[s["element"]].dep_ for s in structure]
  explanation = None
  if ele.pos_ not in ["VERB", "AUX", "NOUN"]:
    explanation = None
  elif ele.pos_ == "AUX" and ele.tag_ in ["VMINF", "VMFIN", "VMPP"]:
    explanation = "情态动词"
  elif ele.lemma_ in aux_verbs and any([d in ["oc"] for d in deps]):
    explanation = "助动词"
  elif ele.lemma_ in cop_verbs:
    explanation = "系动词"
  elif ele.pos_ == "VERB": 
    explanation = "限定动词"
  elif ele.pos_ == "AUX":
    explanation = "助动词"
  else:
    explanation = ele.tag_
  return explanation

def _get_mo_explanation(doc, r, structure):
  ele = doc[r["element"]]
  explanation = None
  deps = [doc[s["element"]].dep_ for s in structure]
  if ele.tag_ in ["PWAT", "PWAV", "PWS"]:
    return "疑问词"
  elif ele.pos_ in ["ADP"]:
    return _mo_adp_explanation(doc, ele, structure)
  elif ele.head.lemma_ in ["heißen", "werden"] and ele.pos_ not in ["ADV"]:
    return "第一格补足语"
  elif ele.head.lemma_ in ["nennen", "kosten", "lehren", "schimpfen", "schelten"]:
    return "第四格补足语"
  else:
    return "其他"

def _get_oc_explanation(doc, r, structure):
  ele = doc[r["element"]]
  deps = [s.dep_ for s in ele.children]
  if ele.pos_ in ["AUX", "VERB"] and r["end"]-r["start"]==1:
    if ele.tag_ in trans_tag.keys():
      return trans_tag[ele.tag_]
    else:
      return ele.tag_
  elif ele.pos_ in ["PRON"] and r["end"]-r["start"]==1:
    return "第四格补足语"
  elif "pm" in deps and r["end"]-r["start"]==2:
    return "带zu不定式"
  elif "sb" in deps or "da" in deps or "oa" in deps or "ep" in deps:
    return "第四格补足语"
  elif ele.head.lemma_ in ["heiß", "heißen", "werden"]: # mo pos
    return "第一格补足语"
  else:
    return "其他"

def _get_sb_explanation(doc, t, structure):
  sbs = [s["element"] for s in structure if doc[s["element"]].dep_ == "sb"]
  if len(sbs) == 1:
    return "主语补足语"
  elif doc[t["element"]].pos_ == "PRON":
    return "主语补足语"
  else:
    return "表语补足语"

def _get_cd_explanation(doc, t, structure):
  ele = doc[t["element"]]
  if len(list(ele.children)) > 0:
    return "并列句"
  else:
    return "连词"

def _get_jucp_explanation(doc, t, structure):
  ele = doc[t["element"]]
  if ele.pos_ in ["SCONJ", "CCONJ"]:
    return "连词"
  else:
    return "其他"

def _get_refer(doc, t, structure):
  parent_id = doc[t["element"]].head.i
  parents = [p for p in structure if p["element"]==parent_id]
  assert(len(parents)==1)
  return parents[0]

def _analyze(doc, t, structure):
  dep = doc[t["element"]].dep_
  explanation = None
  if dep == "ROOT":
    explanation = _get_root_explanation(doc, t, structure)  
  elif dep == "mo":
    explanation = _get_mo_explanation(doc, t, structure)
  elif dep == "oc":
    explanation = _get_oc_explanation(doc, t, structure)
  elif dep == "re":
    t_refer = _get_refer(doc, t, structure)
    explanation = _analyze(doc, t_refer, structure)["explanation"]
    if explanation in ["疑问词"]:
      explanation = "其他"
  elif dep == "sb":
    explanation = _get_sb_explanation(doc, t, structure)
  elif dep == "cd":
    explanation = _get_cd_explanation(doc, t, structure)
  elif dep in ["ju", "cp"]:
    explanation = _get_jucp_explanation(doc, t, structure)
  elif dep in _de2c.keys():
    explanation = _de2c[dep]
  elif dep in ["punct"]:
    explanation = None
  else:
    explanation = dep
  t["explanation"] = explanation
  return t

def de_trs(doc, structure):
  structure_with_explanation = []
  for t in structure:
    _t = _analyze(doc, t, structure)
    structure_with_explanation.append(_t)
  return structure_with_explanation
