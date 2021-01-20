import random

def greedy_move(state):
    me = state.get_whose_turn()
    def evaluate(move):
        return state.copy().apply_move(move).get_score(me)
    return max(state.get_moves(), key=evaluate)

def think(state):
    me = state.get_whose_turn()
    def evaluate(move):
        res = state.copy()
        res.apply_move(move)
        while not res.is_terminal():
            mv = greedy_move(res)
            res.apply_move(mv)
        return res.get_score(me) + random.uniform(0,1)
    return max(state.get_moves(), key=evaluate)