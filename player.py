import random
random.seed(0)
import stochasticgame as sg

class Player:
  
  def selfplay(self, game, state):
    print('---\ngame\n'+str(game))
    while not state.is_terminal():
      actions = tuple( self.get_action(state, i) for i in range(sg.N_PLAYER) )
      pair = state.actions_to_pair[actions]
      transition = self.get_transition(pair)
      print('----\nstate\n'+str(state))
      print('-\ntransitions\n'+str(state.transitions(transition)))
      print('-\nmatrix\n'+str(state.matrix(pair)))
      print('-\ntransition\n'+str(transition))
      state = transition.state
    print('---\n'+str(state)+'\n---')
    return 
  def get_action(self, state, i):
    return random.choices(state.actions[i], weights=state.weights_action[i])[0]
  def get_transition(self, pair):
    return random.choices(pair.transitions, weights=pair.weights_transition)[0]
  