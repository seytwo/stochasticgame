import json
import numpy as np
from util import join

N_PLAYER = 2

class BaseState:
  COUNT = 0
  def __init__(self, key, name=None, is_terminal=False, value=0):
    self.id = BaseState.COUNT
    BaseState.COUNT += 1

    self.key = key
    self.name = name
    self._is_terminal = is_terminal
    self.value = value
    return
  def is_terminal(self):
    return self._is_terminal
class State(BaseState):
  def __init__(self, key, name=None):
    super().__init__(key, name=name)
    self.actions = tuple( list() for i in range(N_PLAYER) )
    self.actions_to_pair = dict()
    return
  @property
  def pairs(self):
    return tuple(self.actions_to_pair.values())
  @property
  def weights_action(self):
    return tuple( tuple( action.weight 
      for action in self.actions[i] ) for i in range(N_PLAYER) )
  def add_action(self, i, action):
    self.actions[i].append(action)
    self.add_pair(i, action)
    return
  def add_pair(self, i1, action_i1):
    i2 = get_opposite(i1)
    for action_i2 in self.actions[i2]:
      actions = [ None, None ]
      actions[i1] = action_i1
      actions[i2] = action_i2
      actions = tuple(actions)
      self.actions_to_pair[actions] = Pair(actions)
    return
  def get_matrix(self):
    return np.array(tuple( tuple( self.get_matrix_element(action_i1, action_i2) 
      for action_i2 in self.actions[1] ) for action_i1 in self.actions[0] ))
  def get_matrix_element(self, action_i1, action_i2):
    pair = self.actions_to_pair[(action_i1, action_i2)]
    return sum( transition.weight*transition.state.value for transition in pair.transitions )
class TerminalState(BaseState):
  def __init__(self, key, value, name=None):
    super().__init__(key, name=name, is_terminal=True, value=value)
    return
  def __str__(self):
    player = int(self.value < 0)
    return join(self.name, self.key, '勝利', 'プレイヤー', player, '利得', self.value)

class Action:
  COUNT = 0
  def __init__(self, name=None, is_dummy=False):
    self.id = Action.COUNT
    Action.COUNT += 1

    self.name = name
    self.weight = None
    self._is_dummy = is_dummy
    return
  def __str__(self):
    return str(self.name)
  def is_dummy(self):
    return self._is_dummy
class DummyAction(Action):
  def __init__(self,):
    super().__init__('dummy', is_dummy=True)
    return

class Transition:
  def __init__(self, state, name=None, memos=None):
    self.state = state
    self.weight = 0
    self.name = name
    self.memos = memos if (memos is not None) else list()
    return
  def __str__(self):
    return '\n'.join(self.memos)
  def add_weight(self, weight):
    self.weight += weight
    return
  
class Pair:
  def __init__(self, actions):
    self.actions = actions
    self.state_to_transition = dict()
    return
  @property
  def transitions(self):
    return tuple(self.state_to_transition.values())
  @property
  def states_next(self):
    return tuple( transition.state for transition in self.transitions )
  @property
  def weights_transition(self):
    return tuple( transition.weight for transition in self.transitions )
  def add_transition(self, state, weight, name=None, memos=None):
    self.state_to_transition[state] = self.state_to_transition.get(state, Transition(state, name=name, memos=memos))
    self.state_to_transition[state].add_weight(weight)
    return

class StochasticGame:
  def __init__(self):
    self.key_to_state = dict()
    return
  @property
  def states(self):
    return tuple(self.key_to_state.values())
  
  def add_state(self, state):
    self.key_to_state[state.key] = state
    return
  
  def save_result(self, path):
    result = {
      'values': { state.id: state.value for state in self.states },
      'weights':{ state.id: [ [ action.weight 
        for action in state.actions[i] ] for i in range(N_PLAYER) ] for state in self.states if not state.is_terminal() }
    }
    with open(path, 'w', encoding='utf8') as file:
      json.dump(result, file, ensure_ascii=False, indent=4)
    return result
  def load_result(self, path):
    with open(path, encoding='utf8') as file:
      result = json.load(file)
    values = result['values']
    for state in self.states:
      state.value = values[str(state.id)]
    weights = result['weights']
    for state in self.states:
      if state.is_terminal():
        continue
      for i in range(N_PLAYER):
        for (j, action) in enumerate(state.actions[i]):
          action.weight = weights[str(state.id)][i][j]
    return

def get_opposite(i):
  return (i+1)%2
