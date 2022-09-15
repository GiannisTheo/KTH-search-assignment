#!/usr/bin/env python3
import random

from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR

import time
import numpy as np
#import minimax as mx


class PlayerControllerHuman(PlayerController):
    def player_loop(self):
        """
        Function that generates the loop of the game. In each iteration
        the human plays through the keyboard and send
        this to the game through the sender. Then it receives an
        update of the game through receiver, with this it computes the
        next movement.
        :return:
        """

        while True:
            # send message to game that you are ready
            msg = self.receiver()
            if msg["game_over"]:
                return


class PlayerControllerMinimax(PlayerController):

    def __init__(self):
        super(PlayerControllerMinimax, self).__init__()

    def player_loop(self):
        """
        Main loop for the minimax next move search.
        :return:
        """

        # Generate first message (Do not remove this line!)
        first_msg = self.receiver()

        while True:
            msg = self.receiver()

            # Create the root node of the game tree
            node = Node(message=msg, player=0)

            # Possible next moves: "stay", "left", "right", "up", "down"
            best_move = self.search_best_next_move(initial_tree_node=node)

            # Execute next action
            self.sender({"action": best_move, "search_time": None})

    def search_best_next_move(self, initial_tree_node):
        """
        Use minimax (and extensions) to find best possible next move for player 0 (green boat)
        :param initial_tree_node: Initial game tree node
        :type initial_tree_node: game_tree.Node
            (see the Node class in game_tree.py for more information!)
        :return: either "stay", "left", "right", "up" or "down"
        :rtype: str
        """

        # EDIT THIS METHOD TO RETURN BEST NEXT POSSIBLE MODE USING MINIMAX ###

        # NOTE: Don't forget to initialize the children of the current node
        #       with its compute_and_get_children() method!



        def distance2(p1,p2):
            return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])


        def heuristic6(node):
            fishes = node.state.fish_positions
            scores = node.state.fish_scores
            hook_pos = node.state.hook_positions[node.state.player]
            keymax = max(scores, key= lambda x: scores[x])
            if keymax not in fishes.keys(): return np.Inf #means fish is already caught
            d = distance2(hook_pos,fishes[keymax])
            if d == 0: return np.Inf
            else: 
                return 1/distance2(hook_pos,fishes[keymax])

        def minimax_select(node,player,depth):
            D = depth
            global best_child
            best_child = None
            player_to_move = player
            #print('sthn arxh ths malakias paizei o ',player)
            def minimax(node,player,depth,alpha,beta):
                global best_child
                if depth == 0:
                    return(heuristic6(node))
                    
                children = node.compute_and_get_children()
                if not player: #maximizing player's turn because maximizer is zero 
                    value = -np.Inf

                    for child in children:
                        minimax_val = minimax(child,int(not player),depth-1,alpha,beta)
                        #print(value,minimax_val,depth)
                        if depth == D:
                            #print('mpika edw')
                            if minimax_val > value:
                                best_child = child
                                #print('mpika edw 1')
                            

                        value = max(value,minimax_val)
                        if value>= beta:
                            break
                        alpha = max(alpha,value)
                    return value
                
                else:  #minimzing player's turn 
                    value = np.inf

                    for child in children:
                        minimax_val = minimax(child,int(not player),depth-1,alpha,beta)
                        #print('mpika edw')
                        #print(value,minimax_val,depth)
                        
                        if depth == D:
                            #print('mpika edw 1')
                            if minimax_val < value:
                            
                                best_child = child 
                        value = min(value,minimax_val)
                        if value <= alpha:
                            break
                        beta = min(beta,value)
                    return value
                
            minimax(node,player,depth,-np.Inf,np.Inf)
            #print('best child',best_child.state)
            best_move = best_child.move
            return best_move






























        t1 = time.time()
        best_move = minimax_select(initial_tree_node,initial_tree_node.state.player,2)
        t2 = time.time()
        #print(initial_tree_node.state.player_caught)
        #print('move from minimax', best_move,'time passed {}'.format(t2-t1))
        return ACTION_TO_STR[best_move]
        #random_move = random.randrange(5)
        #return ACTION_TO_STR[random_move]
