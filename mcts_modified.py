from mcts_node import MCTSNode
from random import choice
from math import sqrt, log
from timeit import default_timer as time

num_nodes = 1000
explore_faction = 2.

def make_choice(root_node, state, identity):
    """ Choose based on UCB heuristic sorting
    Args:
        root_node: root of tree
        state: current state of game
        identity: Red or blue bot

    Returns: Chosen node

    """
    return max(root_node.child_nodes.values(), key=lambda n: ucb_heuristics(n, state, identity))

def my_turn (state, identity):
    """ Determine if it is AI's turn
    Args:
        state: current game state
        identity: identity of bot

    Returns:

    """
        return state.player_turn == identity

def ucb_heuristics (n, state, identity):
    """ Sorts the child nodes of the root based on
        1) Whether or not a box can be made
        2) How many adjacent edges there are (to prevent making an opening for the opponent
        3) UCB algorithm
    Args:
        n: node
        state: state of the game
        identity: which player's turn it is

    Returns:

    """
    if my_turn(state, identity):
        adjust = 0 # Variable to adjust UCB output

        # If state.box_owners length increases, the parent_action must result in box for player
        copy = state.copy()
        orig_len = len(copy.box_owners)
        copy.apply_move(n.parent_action)
        if len(copy.box_owners) > orig_len: adjust += 9001 # If there is a box to be made, highly preferred
                                                            # Please note that it's over 9000

        # Checks all cells around move, and for each edge already played, makes current move less rewarding
        cell = n.parent_action[1]
        x, y = cell
        for i in range (-1, 2, 1):
            for j in range (-1, 2, 1):
                check = (x+i, y+i)
                if check in state.h_line_owners: adjust -= 100 # The more adjacent lines there are, the more
                if check in state.v_line_owners: adjust -= 100 # Opportunities to opening for opponent
        return (n.wins/n.visits) + adjust + explore_faction * sqrt(2*log(n.parent.visits)/n.visits)
    else:
        # UCB algorithm for opposing player
        return 1 - (n.wins/n.visits) + explore_faction * sqrt(2*log(n.parent.visits)/n.visits)

# Selection
def traverse_nodes(node, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """
    while not node.untried_actions and node.child_nodes:
        leaf_node = max(node.child_nodes.values(), key=lambda n: ucb_heuristics(n, state, identity))
        state.apply_move(leaf_node.parent_action)
        node = leaf_node
    else:
        return node
    # Hint: return leaf_node

# Expansion
def expand_leaf(node, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        state:  The state of the game.

    Returns:    The added child node.

    """
    if node.untried_actions: # While we can expand
        move = choice(node.untried_actions) # Apply random move
        state.apply_move(move)
        new_node = MCTSNode(parent=node, parent_action=move, action_list=state.legal_moves)
        node.untried_actions.remove(move)
        node.child_nodes[move] = new_node
        return new_node
    # Hint: return new_node

# Rollout
def rollout(state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        state:  The state of the game.

    """
    while not state.is_terminal():
        state.apply_move(choice(state.legal_moves))

# Backpropagate
def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    while node:
        node.visits += 1
        node.wins += won
        node = node.parent

def think(state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    #'''
    start = time()
    time_elapsed = 0
    #'''

    def get_result (sampled_game):
        reds, blues = sampled_game.score.get('red', 0), sampled_game.score.get('blue', 0)
        result = reds - blues if identity_of_bot == 'red' else blues - reds
        return result

    identity_of_bot = state.player_turn
    root_node = MCTSNode(parent=None, parent_action=None, action_list=state.legal_moves)

    while time_elapsed < 10:
    #for step in range(num_nodes):

        # Copy the game for sampling a playthrough
        sampled_game = state.copy()

        # Start at root
        node = root_node

        # Do MCTS - This is all you!
        node = traverse_nodes(node, sampled_game, identity_of_bot)
        node = expand_leaf(node, sampled_game)
        rollout(sampled_game)
        backpropagate(node, get_result(sampled_game))
        time_elapsed = time() - start

    # Make choice based on tree
    choice = make_choice(root_node, state, identity_of_bot)
    action = choice.parent_action

    # Write tree to file for time testing (Extra Credit Assignment)
    file = open('mcts_modified.out', 'a')
    file.write(root_node.tree_to_string(horizon=100, indent=1))
    return action

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.