from random import choice
from math import *
import time
import threading
#import common
import random

def RewardFunc(me,Gstate):
        reWar = 0.0
        if me == 'blue':
            reWar = Gstate.get_score('blue')
        else:
            reWar = Gstate.get_score('red')    
        return reWar

class SimulationThread(threading.Thread):
    def __init__(self, state):
        #self.__state = state.clone()
        self.__state = state.copy()
        threading.Thread.__init__(self)
        
    def get_result(self, playerjm):
        #return self.__state.get_result(playerjm)
        return RewardFunc(playerjm,self.__state)        
        
    def run(self):
        moves = self.__state.get_moves()
        while moves and not self.__state.is_terminal():  # while state is non-terminal
            self.__state.apply_move(random.choice(moves))
            moves = self.__state.get_moves()

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


def think1(rootstate):
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


def think(rootstate):
    """ Conduct a uct search for iter_max iterations starting from root_state.
        Return the best move from the root_state.
        Assumes 2 alternating players (player 1 starts), with game results in the range [0.0, 1.0]."""

    max_depth = 0
    rootnode = Node(state = rootstate)
    iter_max = 2000
    Parallel_Count = 10
    
    for i in range(iter_max):
        node = rootnode
        state = rootstate.copy()

        # Select
        while len(node.untriedMoves) == 0 and len(node.childNodes) != 0:  # node is fully expanded and non-terminal
            node = node.UCTSelectChild()
            state.apply_move(node.move)
        
        # Expand
        if len(node.untriedMoves) != 0:  # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(node.untriedMoves)
            state.apply_move(m)
            node = node.AddChild(m,state)
        #max_depth = max(node.depth, max_depth)
        
        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        threads = []
        
        for j in range(Parallel_Count):
            threads.append(SimulationThread(state))
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
       
        # Backpropagate
        while node != None:  # backpropagate from the expanded node and work back to the root node
            if node.parentNode:
                #finalscore = RewardFunc(node.parentNode.player,state)
                finalscore = sum([t.get_result(node.parentNode.player) for t in threads]) / Parallel_Count
            else:
                finalscore = 0
            #result = sum([t.get_result(node.player_just_moved()) for t in threads]) / common.PARALLEL_COUNT
            node.Update(finalscore)  # state is terminal. update node with result from POV of node.player_just_moved
            node = node.parentNode

        del threads[:]
        del threads

    """
    selected_node = root_node.uct_select_child(0.0)

    print "Max search depth:", max_depth
    print "Nodes generated:", str(search_tree.size() - node_count)
    print
    print root_node.children2string()

    root_node.clean_sub_tree(selected_node, search_tree)

    print "Nodes remainning:", str(search_tree.size())
    print
    """

    selected = sorted(rootnode.childNodes, key = lambda c: float(c.score)/c.visits)[-1]
    print(selected.score/selected.visits)
    return selected.move 

    return selected_node.move