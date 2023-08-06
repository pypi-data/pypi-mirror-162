import sys

def _trans_VerbForm(item):
  key, value = item
  _dict = {
    "Inf": "原形",
    "Fin": None,
    #"Ger": "",
  }
  result = _dict[value] if value in _dict.keys() else "{}={}".format(key, value)
  return  result 

def _trans_Mood(item):
  key, value = item
  _dict = {
    "Ind": "陈述式",
    "Imp": "命令式",
    "Cnd": "条件式",
    "Sub": "虚拟式",
  }
  result = _dict[value] if value in _dict.keys() else "{}={}".format(key, value)
  return  result 

def _trans_Tense(item):
  key, value = item
  _dict = {
    "Pres": "一般现在时",
    "Past": "简单过去时",
    "Fut": "将来时",
    "Imp": "未完成时",
  }
  result = _dict[value] if value in _dict.keys() else "{}={}".format(key, value)
  return  result 


def _trans_Number(item):
  key, value = item
  _dict = {
    "Sing": "单数",
    "Plur": "复数",
  }
  result = _dict[value] if value in _dict.keys() else "{}={}".format(key, value)
  return  result 

def _trans_Person(item):
  key, value = item
  _dict = {
    "1": "第一人称",
    "2": "第二人称",
    "3": "第三人称",
  }
  result = _dict[value] if value in _dict.keys() else "{}={}".format(key, value)
  return  result 

def _trans_PronType(item):
  key, value = item
  _dict = {
    "Prs": "代词",
  }
  result = _dict[value] if value in _dict.keys() else "{}={}".format(key, value)
  return  result 

def _trans_Reflex(item):
  key, value = item
  _dict = {
    "Yes": "自复",
  }
  result = _dict[value] if value in _dict.keys() else "{}={}".format(key, value)
  return  result 

def trans_morph(morph):
  if "Tense=Past" in morph and "VerbForm=Part" in morph:
    return "过去分词"
  morph_dict = morph.to_dict()
  ordered = ["VerbForm", "Mood", "Tense", "Person", "Number", "Reflex", "PronType", "Case"]
  translated = []
  for key in ordered:
    if key in morph_dict.keys():
      current_pkg = sys.modules[__name__] 
      fn_name = "_trans_{}".format(key)
      value = morph_dict[key]
      if hasattr(current_pkg, fn_name):
        fn = getattr(current_pkg, fn_name)
        translated.append(fn((key,value)))
      else:
        translated.append("{}={}".format(key, value))
  return "|".join(list(filter(None, translated)))
