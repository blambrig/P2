
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_faction = 2.

def make_choice(root_node, state, identity):
    return max(root_node.child_nodes.values(), key=lambda n: ucb(n, state, identity))

def my_turn (state, identity):
        return state.player_turn == identity

def ucb (n, state, identity):
    if my_turn(state, identity):
        return n.wins/n.visits + explore_faction * sqrt(2*log(n.parent.visits)/n.visits)
    else:
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
        leaf_node = max(node.child_nodes.values(), key=lambda n: ucb(n, state, identity))
        state.apply_move(leaf_node.parent_action)
        #print('MCTS Bot traversing to' + str(leaf_node.parent_action))
        node = leaf_node
    else:
        #print('Not fully expanded yet')
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
    if node.untried_actions:
        move = choice(node.untried_actions)
        state.apply_move(move)
        new_node = MCTSNode(parent=node, parent_action=move, action_list=state.legal_moves)
        node.untried_actions.remove(move)
        node.child_nodes[move] = new_node
        #print('New node created.')
        return new_node
    # Hint: return new_node

# Rollout
def rollout(state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        state:  The state of the game.

    """
    while not state.is_terminal():
        #print('Rollout!')
        state.apply_move(choice(state.legal_moves))

# Backpropagate
def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    while node:
        #print('Backpropagating...')
        node.visits += 1
        node.wins += won
        node = node.parent

def think(state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    def get_result (sampled_game):
        if sampled_game.winner == identity_of_bot: return 1
        if sampled_game.winner == 'tie': return 0.5
        if sampled_game.winner != identity_of_bot: return -1
        else: return -1

    identity_of_bot = state.player_turn
    root_node = MCTSNode(parent=None, parent_action=None, action_list=state.legal_moves)

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state.copy()

        # Start at root
        node = root_node

        # Do MCTS - This is all you!
        node = traverse_nodes(node, sampled_game, identity_of_bot)
        node = expand_leaf(node, sampled_game)
        rollout(sampled_game)
        backpropagate(node, get_result(sampled_game))

    choice = make_choice(root_node, state, identity_of_bot)
    action = choice.parent_action
    #print("MCTS (modified) bot picking %s with visits = %f and wins %f" % (action, choice.visits, choice.wins))
    return action

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
