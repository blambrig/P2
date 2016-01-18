
from random import choice


def think(state):
    """ Returns a random move. """
    move = choice(state.legal_moves)
    print("Random bot picking " + str(move))
    return move
