import random

def think(state):
    me = state.get_whose_turn()
    def evaluate(move):
        return state.copy().apply_move(move).get_score(me)
    return max(state.get_moves(), key=evaluate)