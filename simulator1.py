from dotsandboxes import Game
from collections import defaultdict

import sys
import time
import importlib

assert len(sys.argv) == 3
_, red_module, blue_module = sys.argv


bots = {
  'red': importlib.import_module(red_module),
  'blue': importlib.import_module(blue_module),
}

rounds = 10
wins = defaultdict(int)

game = Game()

if __name__ == '__main__':    
  for i in range(rounds):

    print("")
    print("Round %d, fight!" % i)

    state = game.make_initial_state()
    
    while not state.is_terminal():
      tick = time.time()
      move = bots[state.whose_turn].think(state.copy())
      tock = time.time()
      print(state.whose_turn, "thought for", tock-tick, "seconds")
      state.apply_move(move)

    winner = max(game.players,key=state.get_score)
    print("The %s bot wins this round!" % winner)
    wins[winner] = 1 + wins[winner]

  print("")
  print("Final win counts:", dict(wins))
