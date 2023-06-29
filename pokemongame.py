import math
from itertools import product
import numpy as np
from tqdm import tqdm
import stochasticgame as sg
from stochasticgame import N_PLAYER
import pokemon as pk
from util import join, align

N_POKEMON = 3

class Heads:
  def __init__(self, data):
    self.data = data # ( x, x )
    return
  def get(self, i):
    return self.data[i]
  def set(self, i, head):
    self.to_list()
    self.data[i] = head
    self.to_tuple()
    return
  def to_list(self):
    self.data = list(self.data)
    return
  def to_tuple(self):
    self.data = tuple(self.data)
    return
  def copy(self):
    data = tuple(self.data)
    return Heads(data)
class HPs:
  def __init__(self, data, pokemons):
    self.data = data # ( (x, x, x), (x, x, x))
    self.pokemons = pokemons
    self.pokemon_to_idx = tuple( { pokemon: idx for (idx, pokemon) in enumerate(pokemons_i) } for pokemons_i in self.pokemons )
    return
  def get(self, i, pokemon):
    idx = self.pokemon_to_idx[i][pokemon]
    return self.data[i][idx]
  def set(self, i, pokemon, hp):
    idx = self.pokemon_to_idx[i][pokemon]
    self.to_list()
    self.data[i][idx] = hp
    self.to_tuple()
    return
  def to_list(self):
    self.data = tuple( list(data_i) for data_i in self.data )
    return
  def to_tuple(self):
    self.data = tuple( tuple(data_i) for data_i in self.data )
    return
  def copy(self):
    data = tuple( tuple(data_i) for data_i in self.data )
    return HPs(data, self.pokemons)

class State(sg.State):
  def __init__(self, heads, hps, is_battle=False, is_select=False, name=None):
    super().__init__((heads.data, hps.data), name=name)
    self.heads = heads
    self.hps = hps
    self._is_battle = is_battle
    self._is_select = is_select
    return
  def __str__(self):
    array = np.full((sg.N_PLAYER*N_POKEMON, 4), '', dtype=object)
    for i in range(sg.N_PLAYER):
      for (j, pokemon) in enumerate(self.hps.pokemons[i]):
        array[i*N_POKEMON+j, 0] = i
        array[i*N_POKEMON+j, 1] = '*' if (self.is_head(i, pokemon)) else ''
        array[i*N_POKEMON+j, 2] = pokemon.name
        array[i*N_POKEMON+j, 3] = self.hps.get(i, pokemon)
    array = align(array)
    array += '\n'+join('value', round(self.value, 2))
    return array
  def is_battle(self):
    return self._is_battle
  def is_select(self):
    return self._is_select
  def is_head(self, i, pokemon):
    return (pokemon is self.heads.get(i))
  def is_available(self, i, pokemon):
    return is_available(self.hps, i, pokemon)
  def transitions(self, transition):
    result = list()
    for action_j0 in self.actions[0]:
      for action_j1 in self.actions[1]:
        pair_j0_j1 = self.actions_to_pair[(action_j0, action_j1)]
        result.append(join(0, self.heads.get(0), pair_j0_j1.actions[0], '/', 1, self.heads.get(1), pair_j0_j1.actions[1]))
        for transition_j0_j1 in pair_j0_j1.transitions:
          selected = '*' if (transition_j0_j1 is transition) else ' '
          result.append(join('  ', selected, 
                transition_j0_j1.name if (transition_j0_j1.name is not None) else '', 
                'value', round(transition_j0_j1.state.value, 2), 
                'weight', round(transition_j0_j1.weight, 2),
                'state', transition_j0_j1.state.hps.data if (not transition_j0_j1.state.is_terminal()) else transition_j0_j1.state.name))
    return '\n'.join(result)
  def matrix(self, pair):
    data = np.full(tuple( len(self.actions[i])+4 for i in range(sg.N_PLAYER) ), '', dtype=object)
    for (j, action) in enumerate(self.actions[0]):
      data[j+4, 0] = '*' if (action is pair.actions[0]) else ''
      data[j+4, 3] = '('+str(round(action.weight, 2))+')'
      if action.is_dummy():
        continue
      if action.is_attack():
        data[j+4, 1] = '攻撃'
      if action.is_change():
        data[j+4, 1] = '交換'
      data[j+4, 2] = action.name if action.name is not None else ''
    for (j, action) in enumerate(self.actions[1]):
      data[0, j+4] = '*' if (action is pair.actions[1]) else ''
      data[3, j+4] = '('+str(round(action.weight, 2))+')'
      if action.is_dummy():
        continue
      if action.is_attack():
        data[1, j+4] = '攻撃'
      if action.is_change():
        data[1, j+4] = '交換'
      data[2, j+4] = action.name if action.name is not None else ''
    A = self.get_matrix()
    for j0 in range(len(self.actions[0])):
      for j1 in range(len(self.actions[1])):
        data[j0+4, j1+4] = round(A[j0, j1], 2)
    return align(data)
class Battle(State):
  def __init__(self, heads, hps, name=None):
    super().__init__(heads, hps, is_battle=True, name=name)
    return
class Select(State):
  def __init__(self, heads, hps, i, name=None):
    super().__init__(heads, hps, is_select=True, name=name)
    self.i = i # プレイヤ
    return

class Action(sg.Action):
  def __init__(self, is_attack=False, is_change=False, name=None):
    super().__init__(name=name)
    self._is_attack = is_attack
    self._is_change = is_change
    return
  def is_attack(self):
    return self._is_attack
  def is_change(self):
    return self._is_change
class Attack(Action):
  def __init__(self, attack):
    super().__init__(is_attack=True, name=attack.name)
    self.attack = attack
    return
  def __str__(self):
    return join('攻撃', self.attack)
class Change(Action):
  def __init__(self, pokemon):
    super().__init__(is_change=True, name=pokemon.name)
    self.pokemon = pokemon
    return
  def __str__(self):
    return join('交換', self.pokemon)

class PokemonGame(sg.StochasticGame):
  def __init__(self, pokemons, n_hp=4, damage_base=1/2):
    super().__init__()
    self.pokemons = pokemons
    self.n_hp = n_hp
    self.damege_base = damage_base
    return
  def __str__(self):
    output = list()
    for i in range(sg.N_PLAYER):
      output.append(join(i, tuple( pokemon.name for pokemon in self.pokemons[i] )))
    output = '\n'.join(output)
    return output
  
  def initialize(self):
    print('state...')
    (states_battle, states_select, states_terminal) = self.set_state()
    print('action...')
    self.set_action(states_battle, states_select)
    print('transition...')
    self.set_transition(states_battle, states_select, states_terminal)
    return

  def set_state(self):

    (n1, n2) = (len(self.pokemons[0]), len(self.pokemons[1]))

    states_battle = {}
    states_select = {}
    for heads in tqdm(product(self.pokemons[0], self.pokemons[1])):
      heads = Heads(heads)
      for hps in tqdm(product(range(self.n_hp+1), repeat=n1+n2), leave=False):
        hps = tuple( hp/self.n_hp for hp in hps )
        hps = (hps[:n1], hps[n1:])
        hps = HPs(hps, self.pokemons)

        if any( is_lose(hps, i) for i in range(N_PLAYER) ):
          continue
        if all( not is_available(hps, i, heads.get(i)) for i in range(N_PLAYER) ):
          continue

        for i in range(N_PLAYER):
          if not is_available(hps, i, heads.get(i)):
            state = Select(heads, hps, i)
            states_select[state.key] = state
            self.add_state(state)
            break
        else:
          state = Battle(heads, hps)
          states_battle[state.key] = state
          self.add_state(state)

    states_terminal = [
      sg.TerminalState(0, value=1, name='player0'),
      sg.TerminalState(1, value=0, name='player1')
    ]
    for state in states_terminal:
      self.add_state(state)

    print(len(states_battle), len(states_select), len(states_terminal), '=', len(self.states))

    return (states_battle, states_select, states_terminal)

  def set_action(self, states_battle, states_select):
    self.set_action_battle(states_battle)
    self.set_action_select(states_select)
    return
  def set_action_battle(self, states_battle):
    for state in states_battle.values():
      for i in range(N_PLAYER):
        self.set_action_attack(state, i)
        self.set_action_change(state, i)
    return
  def set_action_select(self, states_select):
    for state in states_select.values():
      i = state.i
      j = sg.get_opposite(i)
      self.set_action_change(state, i)
      self.set_action_dummy(state, j)
    return
  def set_action_attack(self, state, i):
    for attack in state.heads.get(i).attacks:
      action = Attack(attack)
      state.add_action(i, action)
    return
  def set_action_change(self, state, i):
    for pokemon in state.hps.pokemons[i]:
      if (state.is_head(i, pokemon)):
        continue
      if (not state.is_available(i, pokemon)):
        continue
      action = Change(pokemon)
      state.add_action(i, action)
    return
  def set_action_dummy(self, state, i):
    action = sg.DummyAction()
    state.add_action(i, action)
    return

  def set_transition(self, states_battle, states_select, states_terminal):
    self.set_transition_battle(states_battle, states_select, states_terminal)
    self.set_transition_select(states_battle, states_select)
    return
  def set_transition_battle(self, states_battle, states_select, states_terminal):
    for state in tqdm(states_battle.values()):
      for pair in state.pairs:
        actions = pair.actions
        if actions[0].is_attack() and actions[1].is_attack():
          self.set_transition_attack_attack(states_battle, states_select, states_terminal, state, pair)
        elif actions[0].is_attack() and actions[1].is_change():
          self.set_transition_attack_change(states_battle, states_select, states_terminal, state, pair, 0)
        elif actions[0].is_change() and actions[1].is_attack():
          self.set_transition_attack_change(states_battle, states_select, states_terminal, state, pair, 1)
        elif actions[0].is_change() and actions[1].is_change():
          self.set_transition_change_change(states_battle, state, pair)
        else:
          raise ValueError()
    return
  def set_transition_attack_attack(self, states_battle, states_select, states_terminal, state, pair):

    sequence_weight = self.compute_sequence_weight(state.heads)

    for i in range(N_PLAYER): # 先行プレイヤ
      j = sg.get_opposite(i)
      hps = state.hps.copy()

      memos = list()

      # 先行→後行ダメージ
      self.set_transition_attack_(pair.actions, state.heads, hps, i, memos)

      if is_lose(hps, j): # 後行全滅
        state_next = states_terminal[i]
        memos.append(join(j, '全滅'))
      elif not is_available(hps, j, state.heads.get(j)): # 後行戦闘不能
        state_next = states_select[(state.heads.data, hps.data)]
        memos.append(join(j, state.heads.get(j), '戦闘不能'))
      else:

        # 後行→先行ダメージ
        self.set_transition_attack_(pair.actions, state.heads, hps, j, memos)

        if is_lose(hps, i): # 先行全滅
          state_next = states_terminal[j]
          memos.append(join(i, '全滅'))
        elif not is_available(hps, i, state.heads.get(i)): # 先行戦闘不能
          state_next = states_select[(state.heads.data, hps.data)]
          memos.append(join(j, state.heads.get(i), '戦闘不能'))
        else:
          state_next = states_battle[(state.heads.data, hps.data)]

      pair.add_transition(state_next, sequence_weight[i], name='先行'+str(i), memos=memos)

    return
  def set_transition_attack_change(self, states_battle, states_select, states_terminal, state, pair, i):
    j = sg.get_opposite(i)

    memos = list()

    heads = state.heads.copy()
    hps = state.hps.copy()

    self.set_transition_change_(pair.actions, heads, j, memos)

    self.set_transition_attack_(pair.actions, heads, hps, i, memos)

    if is_lose(hps, j): # 受け手全滅
      state_next = states_terminal[i]
      memos.append(join(j, '全滅'))
    elif not is_available(hps, j, heads.get(j)): # 受け手戦闘不能
      state_next = states_select[(heads.data, hps.data)]
      memos.append(join(j, state.heads.get(j), '戦闘不能'))
    else:
      state_next = states_battle[(heads.data, hps.data)]
    pair.add_transition(state_next, 1, memos=memos)

    return
  def set_transition_change_change(self, states_battle, state, pair):

    memos = list()

    heads = state.heads.copy()

    for i in range(N_PLAYER):
      self.set_transition_change_(pair.actions, heads, i, memos)

    state_next = states_battle[(heads.data, state.hps.data)]
    pair.add_transition(state_next, 1, memos=memos)

    return
  def set_transition_select(self, states_battle, states_select):
    for state in tqdm(states_select.values()):
      for pair in state.pairs:
        self.set_transition_change(states_battle, state, pair)
    return
  def set_transition_change(self, states_battle, state, pair):

    memos = list()

    heads = state.heads.copy()

    self.set_transition_change_(pair.actions, heads, state.i, memos)

    state_next = states_battle[(heads.data, state.hps.data)]
    pair.add_transition(state_next, 1, memos=memos)

    return
  
  def set_transition_attack_(self, actions, heads, hps, i, memos):
    j = sg.get_opposite(i)
    memos.append(join(i, heads.get(i), 'の攻撃'))
    damage = self.compute_damage(heads, actions, i, memos)
    self.add_damage(heads, hps, j, damage, memos)
    return
  def set_transition_change_(self, actions, heads, i, memos):
    head_ = heads.get(i)
    heads.set(i, actions[i].pokemon)
    memos.append(join(i, head_, 'を', heads.get(i), 'に交換'))
    return

  def compute_damage(self, heads, actions, i, memos):
    j = sg.get_opposite(i)
    damage = self.damege_base
    type_i = actions[i].attack.type
    for type_j in heads.get(j).types:
      damage *= pk.TYPE_CHART[type_i][type_j]
    damage = math.ceil(damage*self.n_hp)/self.n_hp
    memos.append(join(
      type_i, '->',
      ' x '.join( join( type_j.name, join('(', pk.TYPE_CHART[type_i][type_j], ')') ) for type_j in heads.get(j).types )
    ))
    return damage
  def add_damage(self, heads, hps, i, damage, memos):
    head = heads.get(i)
    hp_ = hps.get(i, head)
    hp = max(hp_-damage, 0)
    hps.set(i, head, hp)
    memos.append(join(i, heads.get(i), hp_, '-', damage, '->', hp))
    return
  
  def compute_sequence_weight(self, pokemons):
    return (1/sg.N_PLAYER, 1/sg.N_PLAYER)
  
def is_available(hps, i, pokemon):
  return (hps.get(i, pokemon) > 0)
def is_lose(hps, i):
  return all( not is_available(hps, i, pokemon) for pokemon in hps.pokemons[i] )
