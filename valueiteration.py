from tqdm import tqdm
from util import join
from matrixgame import matrixgame

class ValueIteration:

  def solve(self, game, n_iteration=100, epsilon=10**(-5)):

    for iteration in tqdm(range(n_iteration)):
      
      weights = { state: None for state in game.states if state.is_terminal() }
      values = { state: state.value for state in game.states }
      for state in tqdm(game.states, leave=False):
        if state.is_terminal():
          continue
        (weights[state], values[state]) = self.solve_state(state)

      diff = max( abs(state.value-values[state]) for state in game.states )
      tqdm.write(join(iteration+1, diff))

      for state in game.states:
        if state.is_terminal():
          continue
        state.value = values[state]
        for (i, actions_i) in enumerate(state.actions):
          for action in actions_i:
            action.weight = weights[state][i][action]

      if diff <= epsilon:
        break

    return
  
  def solve_state(self, state):
    A = state.get_matrix()
    x = [ None, None ]
    (x[0], _) = matrixgame(A)
    (x[1], _) = matrixgame(-A.T)
    v =  x[0].dot(A).dot(x[1])
    x = tuple( { action: x[i][j] for (j, action) in enumerate(actions_i) } for (i, actions_i) in enumerate(state.actions) )
    return (x, v)
  