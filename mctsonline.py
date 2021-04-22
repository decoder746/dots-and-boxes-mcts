from random import choice
from math import *
import time

class MCTS:
    "Monte Carlo tree searcher. First rollout the tree then choose a move."

    def __init__(self, exploration_weight=1):
        #self.Q = 0  # total reward of each node
        #self.N = 0  # total visit count for each node
        self.children = dict()  # children of each node
        self.exploration_weight = exploration_weight

    def choose(self, node):
        "Choose the best successor of node. (Choose a move in the game)"
        if node.is_terminal():
            #raise RuntimeError(f"choose called on terminal node {node}")
            return choice(node.origstate.get_moves())
        """
        if node not in self.children:
            return node.find_random_child()
        """

        def score(n):
            if n.visits == 0:
                return float("-inf")  # avoid unseen moves
            return n.score / n.visits  # average reward

        return max(node.childNodes, key=score)

    def do_rollout(self, node):
        #print("Child Nodes:- "+str(len(node.childNodes)))
        "Make the tree one layer better. (Train for one iteration.)"
        path = self._select(node)
        print("Path: "+str(len(path)))
        leaf = path[-1]
        #self._expand(leaf)
        reward = self._simulate(leaf)
        self._backpropagate(path, reward)
        print("Hello")
        for i in range(0,len(path)):
            print(len(path[i].origstate.box_owners))

    def _select(self, node):
        "Find an unexplored descendent of `node`"
        path = []
        while True:
            path.append(node)
            if node.is_terminal() or node.visits==0:
                # node is either unexplored or terminal
                return path
            if len(node.untriedMoves)>0:
                n = node.find_children()
                path.append(n)
                return path
            node = self._uct_select(node)  # descend a layer deeper

    def _simulate(self, node):
        "Returns the reward for a random simulation (to completion) of `node`"
        state = node.origstate.copy()
        while not state.is_terminal(): 
            state.apply_move(choice(state.get_moves()))
        return state.get_score("blue")

    def _backpropagate(self, path, reward):
        "Send the reward back up to the ancestors of the leaf"
        #print("Path length: "+str(len(path)))
        path.reverse()
        for i in range(0,len(path)-1):
            node = path[i]
            if path[i+1].player == "red":
                reward = -reward
            node.visits += 1
            node.score += reward
            #print(len(node.origstate.box_owners))
            #reward = 1 - reward  # 1 for me is 0 for my enemy, and vice versa
        path[-1].visits += 1

    def _uct_select(self, node):
        "Select a child of node, balancing exploration & exploitation"

        # All children of node should already be expanded:
        assert all(n in self.children for n in self.children[node])

        log_N_vertex = math.log(node.visits)

        def uct(n):
            "Upper confidence bound for trees"
            return n.score / n.visits + self.exploration_weight * math.sqrt(
                log_N_vertex / n.visits
            )

        return max(node.childNodes, key=uct)

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
    hello = rootstate.copy()
    rootnode = Node(state = rootstate) 
    tree = MCTS()
    rollouts= 0
    node = rootnode
    while rollouts < 100:
        tree.do_rollout(node)
        rollouts +=  1
        #print(rollouts)
        print(node.is_terminal())
    selected = tree.choose(node)
    return selected.move 