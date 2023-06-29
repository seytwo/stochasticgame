import numpy as np

class Type:
  def __init__(self, name):
    self.name = name
    return
  def __str__(self):
    return self.name
  
class Attack:
  def __init__(self, type_):
    self.name = type_.name
    self.type = type_
    return
  def __str__(self):
    return self.name
  
class Pokemon:
  def __init__(self, name, types, attacks):
    self.name = name
    self.types = types
    self.attacks = attacks
    return
  def __str__(self):
    return self.name

NAMES_TYPE_SINGLE =(
  'ノーマル',
  '炎',
  '水',
  '電気',
  '草',
  '氷',
  '格闘',
  '毒',
  '地面',
  '飛行',
  'エスパー',
  '虫',
  '岩',
  'ゴースト',
  'ドラゴン',
  '悪',
  '鋼',
  'フェアリー'
)

TYPES_SINGLE = [ Type(name) for name in NAMES_TYPE_SINGLE ]

NAME_TO_TYPE = { type_.name: type_ for type_ in TYPES_SINGLE }

TYPE_CHART_SYMBOL_MATRIX = np.array([
  ['','','','','','','','','','','','','△','×','','','△',''],
  ['','△','△','','〇','〇','','','','','','〇','△','','△','','〇',''],
  ['','〇','△','','△','','','','〇','','','','〇','','△','','',''],
  ['','','〇','△','△','','','','×','〇','','','','','△','','',''],
  ['','△','〇','','△','','','△','〇','△','','△','〇','','△','','△',''],
  ['','△','△','','〇','△','','','〇','〇','','','','','〇','','△',''],
  ['〇','','','','','〇','','△','','△','△','△','〇','×','','〇','〇','△'],
  ['','','','','〇','','','△','△','','','','△','△','','','×','〇'],
  ['','〇','','〇','△','','','〇','','×','','△','〇','','','','〇',''],
  ['','','','△','〇','','〇','','','','','〇','△','','','','△',''],
  ['','','','','','','〇','〇','','','△','','','','','×','△',''],
  ['','△','','','〇','','△','△','','△','〇','','','△','','〇','△','△'],
  ['','〇','','','','〇','△','','△','〇','','〇','','','','','△',''],
  ['×','','','','','','','','','','〇','','','〇','','△','',''],
  ['','','','','','','','','','','','','','','〇','','△','×'],
  ['','','','','','','△','','','','〇','','','〇','','△','','△'],
  ['','△','△','△','','〇','','','','','','','〇','','','','△','〇'],
  ['','△','','','','','〇','△','','','','','','','〇','〇','△','']
])

TYPE_CHART_SYMBOL = { type_i: { type_j: TYPE_CHART_SYMBOL_MATRIX[i, j] 
  for (j, type_j) in enumerate(TYPES_SINGLE) } for (i, type_i) in enumerate(TYPES_SINGLE) }

SYMBOL_TO_VALUE = {
  '〇' : 2.0,
  '' : 1.0,
  '△' : 0.5,
  '×' : 0.0
}

TYPE_CHART = { type_i: { type_j: SYMBOL_TO_VALUE[TYPE_CHART_SYMBOL[type_i][type_j]]
  for type_j in TYPES_SINGLE } for type_i in TYPES_SINGLE }
