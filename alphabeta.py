from random import choice
from math import *
import time

inf = float("inf")

def alphabeta(state, depth = 5, alpha = -inf, beta = inf):
    moves = state.get_moves()
    player = state.get_whose_turn()

    if len(moves)==0 or depth==0:
        score = state.get_score('red') - state.get_score('blue')
        if player=='blue':
            score = -score
        return ['X', score]

    if player=='red':
        best_score = -inf
        for move in moves:
            cstate = state.copy()
            cstate.apply_move(move)
            cmove, cscore = alphabeta(cstate, depth-1, alpha, beta)
            if cscore > best_score:
                best_move = move
                best_score = cscore
            alpha = max(best_score, alpha)
            if beta <= alpha:
                break
        return [best_move, best_score]
    else:
        best_score = inf
        for move in moves:
            cstate = state.copy()
            cstate.apply_move(move)
            cmove, cscore = alphabeta(cstate, depth-1, alpha, beta)
            if cscore < best_score:
                best_move = move
                best_score = cscore
            beta = min(best_score, beta)
            if beta <= alpha:
                break
        return [best_move, best_score]

def think(state):
    return alphabeta(state, 7)[0]









