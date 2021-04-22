from random import choice
from math import *
import random, queue
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
   
    def UCTSelectChild(self):   
        s = sorted(self.childNodes, key = lambda c: float(c.score)/(50*c.visits) + sqrt(8*log(self.visits)/c.visits))[-1]
        return s
    
    def AddChild(self, m, s):
        n = Node(move = m, parent = self, state = s)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n
    
    def Update(self, result):
        self.visits += 1
        self.score += result

    def find_children(self):
        m = choice(self.untriedMoves)
        state = self.origstate.apply_move(m)
        node = self.AddChild(m,state)
        return node

    def find_all_children(self):
        nodes = []
        for m in self.untriedMoves:
            state = self.origstate.apply_move(m)
            node = Node(move = m, parent = self, state = state)
            nodes.append(node)
        return nodes

    def is_terminal(self):
        return self.origstate.is_terminal()

    def find_random_child(self):
        return choice(self.childNodes)

    def copy(self):
        res = Node(state = self.origstate)
        res.move = self.move
        res.parentNode = self.parentNode
        res.childNodes = self.childNodes
        res.score = self.score
        res.visits = self.visits
        res.untriedMoves = self.untriedMoves
        res.player = self.player
        return res


def think(rootstate):
    """
    Implementation of the UCT variant of the Monte Carlo Tree Search algorithm.
    """
    root = Node(state=rootstate)
    unexplored = queue.Queue()
    unexplored.put(root)

    def RewardFunc(me,Gstate):
        reWar = 0.0
        if me == 'blue':
            reWar = Gstate.get_score('blue')
        else:
            reWar = Gstate.get_score('red')    
        return reWar

    n = 10000
    for i in range(0,n):
        # Quit early if we are out of nodes
        #print(i)
        if unexplored.qsize() == 0:
            break
        # Add the new node to the tree
        current = unexplored.get()
        # Add the newly discovered nodes to the queue
        for action in current.origstate.get_moves():
            state = current.origstate.copy()
            state.apply_move(action)
            node = current.AddChild(action,state)
            unexplored.put(node)
        cstate = current.origstate
        node = current
        # Simulate the rest of the game from the current node
        while not cstate.is_terminal():
            cstate.apply_move(choice(cstate.get_moves()))

        # Back simulation value up to the root
        while node != None:
            if node.parentNode:
                finalscore = RewardFunc(node.parentNode.player,cstate)
            else:
                finalscore = 0
            node.Update(finalscore)
            node = node.parentNode

    selected = sorted(root.childNodes, key = lambda c: float(c.score)/c.visits)[-1]
    return selected.move