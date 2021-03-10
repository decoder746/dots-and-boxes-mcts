from random import choice
from math import *
import time

class Node:
    def __init__(self, move = None, parent = None, state = None):
        self.move = move
        self.parentNode = parent
        self.childNodes = []
        self.origstate = state
        self.score = 0.0
        self.visits = 0.0
        self.untriedMoves = state.get_moves()
        self.player = state.get_whose_turn()
   
    def UCTSelectChild(self,prune=None):   
        s = sorted(self.childNodes, key = lambda c: float(c.score)/(c.visits) + sqrt(20*log(self.visits)/c.visits))[-1]
        """
        if prune is not None:
            s = sorted(prune, key = lambda c: float(c.score)/(c.visits) + sqrt(2*log(self.visits)/c.visits))[-1]
        """
        return s
    
    def AddChild(self, m, s):
        n = Node(move = m, parent = self, state = s)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n
    
    def Update(self, result):
        self.visits += 1
        self.score += result


def think(rootstate):
    rootnode = Node(state = rootstate) 
    def RewardFunc(me,Gstate):
        reWar = 0.0
        if me == 'blue':
            reWar = Gstate.get_score('blue')
        else:
            reWar = Gstate.get_score('red')    
        return reWar
    rollouts= 0
    prune = []
    num = 20000
    while rollouts < num:
        node = rootnode
        state = rootstate.copy()
        rollouts +=  1
        #Selection
        while len(node.untriedMoves) == 0 and len(node.childNodes) != 0:
            node = node.UCTSelectChild()
            state.apply_move(node.move)
        #Expansion
        if len(node.untriedMoves) != 0: 
            m = choice(node.untriedMoves) #Gives the lines not covered yet
            #m = state.chains(node.untriedMoves)
            state.apply_move(m)
            node = node.AddChild(m,state)
        #Playout 
        while not state.is_terminal(): 
            state.apply_move(choice(state.get_moves()))
            #state.apply_move(state.chains(state.get_moves()))
        #Backpropagation
        while node != None:
            if node.parentNode:
                finalscore = RewardFunc(node.parentNode.player,state)
            else:
                finalscore = 0
            node.Update(finalscore)
            node = node.parentNode

    """
    node = rootnode
    while len(node.untriedMoves) == 0 and len(node.childNodes) !=0:
        for c in node.childNodes:
            print(c.visits)
    """
    #for k in rootnode.childNodes:
        #print(k.visits)
        #print(k.score/k.visits)

    selected = sorted(rootnode.childNodes, key = lambda c: float(c.score)/c.visits)[-1]
    print(selected.score/selected.visits)
    return selected.move 