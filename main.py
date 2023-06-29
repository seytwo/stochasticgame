import json
import stochasticgame as sg
from valueiteration import ValueIteration
from player import Player
import pokemon as pk
import pokemongame as pkg

def create_pokemons(config):
  pokemons = tuple( tuple( create_pokemon(config, i, j) 
    for j in range(pkg.N_POKEMON ) ) for i in range(sg.N_PLAYER) ) 
  return pokemons
def create_pokemon(config, i, j):
  name = config[i][j]['name']
  types = tuple( pk.NAME_TO_TYPE[type_] for type_ in config[i][j]['types'] )
  attacks = tuple( pk.Attack(type_) for type_ in types )
  pokemon = pk.Pokemon(name, types, attacks)
  return pokemon

def main():

  config = json.load(open('config.json', encoding='utf8'))

  pokemons = create_pokemons(config)
  name_to_pokemon = tuple( { pokemon.name: pokemon 
    for pokemon in pokemons[i] } for i in range(sg.N_PLAYER) )

  n_hp = 2
  game = pkg.PokemonGame(pokemons, n_hp=n_hp)
  game.initialize()
  game.load_result('hp='+str(n_hp)+'.json')

  ValueIteration().solve(game)
  game.save_result('hp='+str(n_hp)+'.json')

  heads = (
    name_to_pokemon[0]['サザンドラ'], 
    name_to_pokemon[1]['ギルガルド']
  )
  hps = ((1, 1, 1), (1, 1, 1))
  key = (heads, hps)
  state = game.key_to_state[key]
  Player().selfplay(game, state)

  return

if __name__ == '__main__':
  main()