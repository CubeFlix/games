# mancala.py
# Mancala game and algorithm.

class Board:
    
    """The mancala board."""

    def __init__(self, a=0, b=0, holes=None):

        """Create the board."""

        self.a = a
        self.b = b

        self.holes = [4 for i in range(12)] if not holes else holes

    def move(self, hole, turn):

        """Make a move. 'hole' is the hole to move, and 'turn' is 'a' if it is
           a's turn, or 'b' if it is b's turn. Returns True if the player can 
           move again afterwards, and False if the player's turn is over."""

        if not self.holes[hole]:
            return False

        beads = self.holes[hole]
        self.holes[hole] = 0

        # Loop until we are out of beads.
        while beads:
            # Check if we should deposit into the 'a' hole.
            if hole == 11 and turn == 'a':
                # Deposit a bead into the 'a' hole.
                self.a += 1
                beads -= 1

                if beads == 0:
                    # Out of beads.
                    return True

            elif hole == 5 and turn == 'b':
                # Deposit a bead into the 'b' hole.
                self.b += 1
                beads -= 1

                if beads == 0:
                    # Out of beads.
                    return True

            # Move one hole forward.
            hole = hole + 1 if hole < 11 else 0

            # Deposit one bead into the hole.
            self.holes[hole] += 1
            beads -= 1

            # If we are out of beads, check if the current hole has beads to
            # collect.
            if not beads:
                if self.holes[hole] > 1:
                    beads = self.holes[hole]
                    self.holes[hole] = 0
                else:
                    # No more beads, end of turn.
                    return False

    def dup(self):

        """Make a copy of the board."""

        return Board(self.a, self.b, self.holes[:])


class Computer:

    """The mancala algorithm."""

    def __init__(self, player):

        """Create the computer. 'player' determines the player the computer
           should calculate for, can be 'a' or 'b'."""

        self.player = player

    def calculate(self, board, limit=2):

        """Calculate a move, given a board."""

        # Keep track of the final minimax scores.
        scores = {}

        # Check each possible move.
        for move in self.find_all_moves(board):
            # Make the move.
            current_board = board.dup()
            if not current_board.move(move, self.player):
                # Evaluate the new board.
                scores[move] = self.evaluate(current_board, 'b' if self.player == 'a' else 'a', \
                        0, limit)
            else:
                # We get to go again. Evaluate the new board.
                scores[move] = self.evaluate(current_board, self.player, 0, limit)

        print(scores)
        return max(scores.items(), key=lambda x: x[1])[0]

    def evaluate(self, board, to_move, depth, limit):

        """Evaluate a board, returning the final score."""

        # If we hit the limit, get the final scores.
        if depth == limit:
            if self.player == 'a':
                return board.a - board.b
            else:
                return board.b - board.a

        # Keep track of the final minimax scores.
        scores = {}

        # Check each possible move.
        for move in self.find_all_moves(board):
            # Make the move.
            current_board = board.dup()
            if not current_board.move(move, to_move):
                # Evaluate the new board.
                scores[move] = self.evaluate(current_board, 'b' if to_move == 'a' else 'a', \
                        depth+1, limit)
            else:
                # We get to go again. Evaluate the new board.
                scores[move] = self.evaluate(current_board, to_move, depth, limit)
    
        # If we run out of moves, return.
        if scores == {}:
            if self.player == 'a':
                return board.a - board.b
            else:
                return board.b - board.a

        # If we are evaluating for the opponent, pick the best score for them.
        if to_move != self.player:
            return min(scores.values())
        else:
            return max(scores.values())

    def find_all_moves(self, board):

        """Find all moves, given a board."""

        moves = set([(move if hole else None) for move, hole in enumerate(board.holes)])
        moves.discard(None)
        return list(moves)


def print_board(b):

    """Print out a board."""

    # Print the second row, reversed (12 - 6).
    print(' C ' + ''.join([str(hole).rjust(3, ' ') for hole in reversed(b.holes[6:])]) + ' P ')

    # Print the holes for points.
    print(str(b.a).rjust(3, ' ') + '   ' * 6 + str(b.b).rjust(3, ' '))

    # Print the first row (1, 6).
    print('   ' + ''.join([str(hole).rjust(3, ' ') for hole in b.holes[:6]]))

if __name__ == '__main__':
    b = Board()
    c = Computer('a')
    
    while True:
        print_board(b)

        # Make the computer move.
        print("Thinking...")
        computer_move = c.calculate(b)
        print("Computer has moved!")
        b.move(computer_move, 'a')

        print_board(b)

        # Make the player move.
        guess = input("Player move (1 - 12): ")
        while not guess.isdecimal():
            guess = input("Enter a valid move. Player move (1 - 12): ")
        b.move(int(guess)-1, 'b')
