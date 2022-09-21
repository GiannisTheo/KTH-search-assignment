from math import sqrt
from xml.dom import NotFoundErr
import numpy as np
from fishing_game_core.game_tree import State , Node
from time import time ,time_ns,perf_counter
import signal 

def color(p):
    if p==0: return 1
    else: return -1

def distance(p1,p2): # input two points as a tuple
    #print(p1,p2)
    dist = sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
    #print(dist.real)
    return dist


def distance2(p1,p2):
    return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])


def heuristic6(node):
    fishes = node.state.fish_positions
    scores = node.state.fish_scores
    hook_pos = node.state.hook_positions[node.state.player]
    keymax = max(scores, key= lambda x: scores[x])
    if keymax not in fishes.keys(): return 0 #means fish is already caught
    d = distance(hook_pos,fishes[keymax])
    return 1/(distance(hook_pos,fishes[keymax])+0.0001)*scores[keymax]

def heuristic20(node):
    p1_score = node.state.player_scores[node.state.player]
    p2_score =  node.state.player_scores[int(not node.state.player)]
    return 3/4*(p1_score-p2_score)+1/4*(heuristic6(node))
    



def alphabeta2(node,depth,alpha,beta,initial_depth,stop_time):
    move_from_parent = None
    if time() >= stop_time:
        print('time expired at the start of minimax at depth ',depth)
        return None,None

    if depth == 0:
        return heuristic20(node),move_from_parent


    if node.state.player == 0: #maximizing player
        max_value = -np.Inf

        children = node.compute_and_get_children()
        if children == []: print('brika adeia paidia')
        for child in children:
            minimax_value , _ = alphabeta2(child,depth-1,alpha,beta,initial_depth,stop_time)
            if time() >= stop_time:
                print('time expired after max call at depth ', depth) 
                return None,None
            if depth == initial_depth and minimax_value >= max_value :
                move_from_parent = child.move
                #print('h kinisi phre timi ',move_from_parent)
            max_value = max(max_value,minimax_value)
            alpha = max(max_value,alpha)
            if alpha>=beta: break

    else:                         #minimizers turn to make a move
        min_value = np.Inf
        children = node.compute_and_get_children()
        for child in children:
            minimax_value , _ = alphabeta2(child,depth-1,alpha,beta,initial_depth,stop_time)
            if time()>=stop_time:
                print('time expired after min call at depth ', depth)
                return None,None
            if depth == initial_depth and minimax_value <= min_value :
                move_from_parent = child.move
                #print('h kinisi phre timi ',move_from_parent)
            min_value = min(min_value,minimax_value)
            beta = min(min_value,beta)
            if alpha>=beta: break

    return minimax_value,move_from_parent


    
def iterative_deepening2(time_per_move,node):
    start_time = time() #time in sec
    stop_time = start_time + time_per_move
    move = None
    for depth in range(2,10,2):
        if time() >= stop_time:
            print('i got timed out from time at depth',depth)
            break
        print('when search starts for depth {} time remaining is {}'.format(depth,stop_time-time()))
        value,returned_move =  alphabeta2(node,depth,-np.Inf,np.Inf,depth,stop_time)    
        if returned_move != None:
            move = returned_move
            print('finshed running for depth=',depth)
        else:
            time_remaining = stop_time - time()
            print('i got timed out because NONE return at depth',depth,'time remaining = {}'.format(time_remaining))
            return move
            break 
    return move

def plain_alphabeta(node,depth,alpha,beta,initial_depth):
    move_from_parent = None
    if depth == 0:
        return heuristic6(node),move_from_parent


    if node.state.player == 0: #maximizing player
        max_value = -np.Inf

        children = node.compute_and_get_children()
        for child in children:
            minimax_value,_ = plain_alphabeta(child,depth-1,alpha,beta,initial_depth)
            if depth == initial_depth and minimax_value >= max_value :
                move_from_parent = child.move
            max_value = max(max_value,minimax_value)
            alpha = max(max_value,alpha)
            if alpha>=beta: break

    else:                         #minimizers turn to make a move
        min_value = np.Inf
        children = node.compute_and_get_children()
        for child in children:
            minimax_value,_ = plain_alphabeta(child,depth-1,alpha,beta,initial_depth)
            if depth == initial_depth and minimax_value <= min_value :
                move_from_parent = child.move
            min_value = min(min_value,minimax_value)
            beta = min(min_value,beta)
            if alpha>=beta: break

    return minimax_value,move_from_parent



def sort_by_score(children,func):
    if children[0].parent.state.player == 0  : reverse = True
    else: reverse = False
    return sorted(children, key = lambda x: func(x),reverse = reverse)

def hashing(node):
    #hashed = str(node.state.player) + '/'  #append the playrs turn 
    hashed = str(node.state.hook_positions[0])+str(node.state.hook_positions[1]) + '/' #append the positions of the hooks
    #hashed = str(node.state.hook_positions[0])+'/'
    fishes = node.state.fish_positions       #append the positions of all fishes with their corresponding index before
    for key in sorted(fishes.keys()):
        hashed+=(str(key)+str(fishes[key]))    

    hashed+= ('/'+ str(node.state.player_scores[0])+'-'+ str(node.state.player_scores[1])) #append the score
    hashed+= ('/' + str(node.state.player_caught[0]) + '-'+  str(node.state.player_caught[1])) #append the fish caught
    return hashed

state_dict ={}

def use_state_dict(child,depth):
    hashed_child = hashing(child)
    if hashed_child in state_dict.keys():
        if state_dict[hashed_child][1]>depth:
            return state_dict[hashed_child][0]
    else:
        return False

def update_state_dict(child,value,depth):
    hashed_child = hashing(child)
    state_dict[hashed_child] = [value,depth]
    return 


def sorted_alphabeta_with_hash(node,depth,alpha,beta,initial_depth):
    move_from_parent = None
    if depth == 0:
        return heuristic20(node),move_from_parent


    if node.state.player == 0: #maximizing player
        max_value = -np.Inf

        children = node.compute_and_get_children()
        children = sort_by_score(children,heuristic20)
        for child in children:
            hash_value = use_state_dict(child,depth-1)
            if hash_value == None:
                minimax_value,_ = sorted_alphabeta_with_hash(child,depth-1,alpha,beta,initial_depth)
                update_state_dict(child,minimax_value,depth-1)
            if depth == initial_depth and minimax_value >= max_value :
                move_from_parent = child.move
            max_value = max(max_value,minimax_value)
            alpha = max(max_value,alpha)
            if alpha>=beta: break

    else:                         #minimizers turn to make a move
        min_value = np.Inf
        children = node.compute_and_get_children()
        children = sort_by_score(children,heuristic20)
        for child in children:
            minimax_value,_ = sorted_alphabeta_with_hash(child,depth-1,alpha,beta,initial_depth)
            if depth == initial_depth and minimax_value <= min_value :
                move_from_parent = child.move
            min_value = min(min_value,minimax_value)
            beta = min(min_value,beta)
            if alpha>=beta: break

    return minimax_value,move_from_parent


