from random import choice
from math import *
import time
import threading
#import common
import random

class Node:
    def __init__(self, move = None, parent = None, state = None, tree_node = None):
        self.move = move
        self.parentNode = parent
        self.childNodes = []
        self.origstate = state
        self.score = 0.0
        self.visits = 0.0
        self.untriedMoves = state.get_moves()
        self.player = state.get_whose_turn()
        self.tree_node = tree_node
   
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

    def uct_select_child(self, constant, search_node_creator=None):
        """ Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
            exploration versus exploitation.
        """
        assert self.childNodes()        
        creator = search_node_creator if search_node_creator is not None else SearchNode        
        (move, child) = max(self.child_nodes().items(), key=lambda (m, n): n.ucb(self.__tree_node, constant))
        node = creator(move, self, child)
        return node


class TreeNode(Node):
    def __init__(self, state):
        self.__lock = threading.Lock()
        self.__lock.acquire()
        Node.__init__(self, state)
        self.__lock.release()

    def acquire_lock(self):
        self.__lock.acquire()

    def release_lock(self):
        self.__lock.release()
        
    def update(self, result):
        self.__lock.acquire()
        Node.update(self, result)
        self.__lock.release()
        
    def add_child(self, fm, n):
        self.__lock.acquire()
        Node.add_child(self, fm, n)        
        self.__lock.release()

"""
    
class SearchTree(common.SearchTree):
    def __init__(self):
        common.SearchTree.__init__(self)
        self.__lock = threading.Lock()
    
    def get_node(self, state):
        self.__lock.acquire()
        node = common.SearchTree.get_node(self, state, TreeNode)
        self.__lock.release()
        return node

    def clean_sub_tree(self, root_node, ignored_node):
        self.__lock.acquire()
        common.SearchTree.clean_sub_tree(self, root_node, ignored_node)
        self.__lock.release()
"""

class SearchNode(Node):
    def __init__(self, move=None, parent=None, tree_node=None):
        Node.__init__(self, move, parent, tree_node)
        
    def acquire_lock(self):
        self.__tree_node.acquire_lock()

    def release_lock(self):
        self.__tree_node.release_lock()
        
    def uct_select_child(self, constant):
        return Node.uct_select_child(self, constant, SearchNode)


class SearchTree:
    def __init__(self):
        self.__pool = {}
    
    def get_node(self, state, tree_node_creator=None):
        key = str(state)
        
        creator = tree_node_creator if tree_node_creator is not None else TreeNode
        if key not in self.__pool:
            self.__pool[key] = creator(state)
                    
        return self.__pool[key]

    def clean_sub_tree(self, root_node, ignored_node):
        ignore_set = sets.Set()
        ignored_node.traverse(lambda n: ignore_set.add(n))

        for (k, n) in self.__pool.items():
            if n not in ignore_set:
                del self.__pool[k]
        ignore_set.clear()
    
    def size(self):
        return len(self.__pool)

        
class SearchThread (threading.Thread):
    def __init__(self, rootstate, itermax, search_tree):
        threading.Thread.__init__(self)
        self.__rootstate = rootstate
        self.__itermax = itermax
        self.__search_tree = search_tree
        
    def run(self):
        rootnode = Node(state = self.__rootstate)

        for i in range(self.__itermax):
            node = self.__search_tree.get_node(self.__root_state)
            state = self.__rootstate.copy()

            # Select
            while len(node.untriedMoves) == 0 and len(node.childNodes) != 0: # node is fully expanded and non-terminal
                node = node.UCTSelectChild()
                state.apply_move(node.move)

            # Expand
            node.acquire_lock()
            m = random.choice(node.untriedMoves) if node.untriedMoves else None
            node.release_lock()

            if m is not None:  # if we can expand (i.e. state/node is non-terminal)
                state.apply_move(m)
                node = node.add_child(m, self.__search_tree.get_node(state))  # add child and descend tree

            # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
            moves = state.get_moves()
            while moves:  # while state is non-terminal
                state.apply_move(random.choice(moves))
                moves = state.get_moves()

            # Backpropagate
            while node != None:  # backpropagate from the expanded node and work back to the root node
                if node.parentNode:
                    finalscore = RewardFunc(node.parentNode.player,state)
                else:
                    finalscore = 0
                #node.update(state.get_result(node.player_just_moved()))  # state is terminal. update node with result from POV of node.player_just_moved
                node.Update(finalscore)
                node = node.parent_node


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


def think2(rootstate):
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
        
        for i in range(Parallel_Count):
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

def think(rootstate):
    """ Conduct a uct search for __iter_max iterations starting from __root_state.
        Return the best move from the __root_state.
        Assumes 2 alternating players (player 1 starts), with game results in the range [0.0, 1.0]."""

    search_tree = SearchTree()

    iter_max = 20000
    Parallel_Count = 10

    threads = []
    
    for i in range(Parallel_Count):
        threads.append(SearchThread(rootstate, int(iter_max / Parallel_Count), search_tree))
    
    for t in threads:
        t.start()
        
    for t in threads:
        t.join()
    
    rootnode = SearchNode(tree_node=search_tree.get_node(root_state))
    #selected_node = rootnode.uct_select_child(0.0)

    selected = sorted(rootnode.childNodes, key = lambda c: float(c.score)/c.visits)[-1]
    root_node.clean_sub_tree(selected_node, search_tree)
    print(selected.score/selected.visits)
    return selected.move 