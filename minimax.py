from cmath import inf, sqrt
from xml.dom import NotFoundErr
import numpy as np
from fishing_game_core.game_tree import State , Node
from time import time 

def color(p):
    if p==0: return 1
    else: return -1


def heuristic(node):
    score = (node.state.player_scores[node.state.player] - node.state.player_scores[int(not node.state.player)])*color(node.state.player)
    return score
    
def distance(p1,p2): # input two points as a tuple
    #print(p1,p2)
    dist = sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
    #print(dist.real)
    return dist.real


def distance2(p1,p2):
    return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])



#implement the eukleidian distance of the closest fish 
def heuristic2(node):
    #print('sto telos tou dentrou paizei o {}'.format(node.state.player))
    fishes = node.state.fish_positions.values()
    if not fishes: return 0
    # print(fishes)
    hook_pos = node.state.hook_positions[node.state.player]

    distances = [distance2(hook_pos,fish) for fish in fishes]
    #print(distances)
    min_distance = min(distances)
    if min_distance == 0: return inf
    return 1/min_distance


def heuristic3(node):

    scores = node.state.fish_scores
    fishes = node.state.fish_positions.values()
    #print(scores)
    if not fishes: return 0
    # print(fishes)
    hook_pos = node.state.hook_positions[node.state.player]
    
    distances = [distance(hook_pos,fish) for fish in fishes]
    #print(distances)
    min_distance = min(distances)
    if min_distance == 0: 
        return np.Inf*color(node.state.player)
        #return 10**5*color(node.state.player) 
    if node.state.player == 1: 
        #print('mpika edw')
        return min_distance
    else:  return (1/min_distance) 
    
def heuristic4(node):
    #print('sto telos tou dentrou paizei o {}'.format(node.state.player))
    fishes = node.state.fish_positions
    scores = node.state.fish_scores
    if not fishes: return 0
    # print(fishes)
    hook_pos = node.state.hook_positions[node.state.player]

    distances = [distance(hook_pos,fish).real for fish in fishes.values()]
    if 0 in distances: return inf
    combined_scores = [scores[key]/distance2(fishes[key],hook_pos) for key in fishes.keys()]
    max_score = max(combined_scores)
    return max_score


def heuristic5(node):
    fishes = node.state.fish_positions
    scores  = node.state.fish_scores
    if not fishes: return 0
    hook_pos = node.state.hook_positions[node.state.player]
    hook_pos_op = node.state.hook_positions[int(not node.state.player)]


    dif_dist = [distance(fishes[key],hook_pos_op) - distance(fishes[key],hook_pos) for key in fishes.keys()]
    return max(dif_dist)

    

def heuristic6(node):
    fishes = node.state.fish_positions
    scores = node.state.fish_scores
    hook_pos = node.state.hook_positions[node.state.player]
    keymax = max(scores, key= lambda x: scores[x])
    if keymax not in fishes.keys(): return inf #means fish is already caught
    d = distance2(hook_pos,fishes[keymax])
    if d == 0: return inf
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


def color(p):
    if p==0: return 1
    else: return -1


def negamax_select(node,depth,player):
    D = depth
    global best_child
    best_child = None
    player_to_move = player    

    def negamax(node,depth,player):
        if depth == 0:
            return heuristic(node)*color(player)
        value = -np.Inf
        children = node.compute_and_get_children()
        for child in children:
            print(child)
        for child in children:
            negamax_value = -negamax(child,depth-1,int(not player))
            if depth == D and player_to_move == player:
                if negamax_value>value:
                    global best_child
                    best_child = child
                    print('found a best child')
            value = max(value,negamax_value)
        return value
    negamax(node,depth,player)
    print('best_child is ',best_child)
    best_move = best_child.move
    return best_move



state_dict = {}

def hashing(node):
    hashed = str(node.state.player) + '/'  #append the playrs turn 
    hashed+= (str(node.state.hook_positions[0])+str(node.state.hook_positions[1]) + '/') #append the positions of the hooks
    
    fishes = node.state.fish_positions       #append the positions of all fishes with their corresponding index before
    for key in sorted(fishes):
        hashed+=(str(key)+str(fishes[key]))    

    hashed+= ('/'+ str(node.state.scores[0])+'-'+ str(node.state.scores[1])) #append the score
    hashed+= ('/' + str(node.state.player_caught[0]) + '-'+  str(node.state.player_caught[1])) #append the fish caught
    return hashed



def alphabeta(node,player,depth,alpha,beta):
    if depth == 0:
        return heuristic(node)


    if node.state.player == 0: #maximizing player
        max_value = -np.Inf

        children = node.compute_and_get_children()
        for child in children:
            minimax_value = alphabeta(child,1,depth-1,alpha,beta)
            max_value = max(max_value,minimax_value)
            alpha = max(max_value,alpha)
            if alpha>=beta: break

    else:                         #minimizers turn to make a move
        min_value = np.Inf
        children = node.compute_and_get_children()
        for child in children:
            minimax_value = alphabeta(child,0,depth-1,alpha,beta)
            min_value = min(min_value,minimax_value)
            beta = min(min_value,beta)
            if alpha>=beta: break

    return minimax_value





    



        
