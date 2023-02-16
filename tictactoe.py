# tictactoe.py
# Tic-Tac-Toe game.

import pygame, copy

class Board:

    """A tic-tac-toe game board."""

    def __init__(self, board=[[None, None, None], [None, None, None], [None, None, None]]):

        """Create the board."""

        self.board = board

    def is_set(self, pos):
        
        """Check if a tile has been set."""

        if self.get(pos):
            return True
        return False
 
    def set(self, pos, player):

        """Set a position on the board."""

        self.board[pos[0]][pos[1]] = player

    def get(self, pos):

        """Get a position on the board."""

        return self.board[pos[0]][pos[1]]

    def has_won(self, player):

        """Check if a player has won."""

        # Check for a win along a row.
        for row in range(3):
            if self.board[row] == [player] * 3:
                return True
        
        # Check for a win along a column.
        for col in range(3):
            if self.board[0][col] == player and self.board[1][col] == player and self.board[2][col] == player:
                return True

        # Check for a win along a diagonal.
        if self.board[0][0] == player and self.board[1][1] == player and self.board[2][2] == player:
            return True

        if self.board[0][2] == player and self.board[1][1] == player and self.board[2][0] == player:
            return True

        return False

    def has_tie(self):

        """Check if the board has a tie."""

        for row in range(3):
            for col in range(3):
                if not self.get((row, col)):
                    return False
        return True

    def duplicate(self):

        """Create a copy of the board."""

        return Board(copy.deepcopy(self.board))

class Computer:

    """The computer algorithm."""

    def __init__(self, computer, player):

        """Create the computer player."""

        self.computer = computer
        self.player = player

    def evaluate(self, board, depth):

        """Evaluate a board."""

        if board.has_won(self.computer):
            return 10-depth
        elif board.has_won(self.player):
            return depth-10
        else:
            return 0

    def game_over(self, board):

        """check if a game has ended."""

        if board.has_won(self.computer):
            return True
        elif board.has_won(self.player):
            return True
        elif board.has_tie():
            return True
        return False

    def calculate_move(self, board):

        """Calculate the best move for the computer.."""

        moves = []
        scores = []
        for row in range(3):
            for col in range(3):
                if not board.is_set((row, col)):
                    # Evaluate this move.
                    new_board = board.duplicate()
                    new_board.set((row, col), self.computer)
                    evaluation = self.minimax(new_board, self.player)
                    moves.append((row, col))
                    scores.append(evaluation)

        return moves[scores.index(max(scores))]

    def minimax(self, board, player, depth=0, limit=10):

        """Recursively perform the minimax algorithm on a board, returning the final evaluation."""

        # If it's already game over, we can stop.
        if self.game_over(board):
            evaluation = self.evaluate(board, depth)
            # print(' ' * depth, 'Game ended:', evaluation)
            return evaluation

        if depth == limit:
            # Evaluate the board at this position.
            evaluation = self.evaluate(board, depth)
            # print(' ' * depth, 'Limit reached:', evaluation)
            return evaluation

        if player == self.computer:
            # Our turn. Pick the best move and evaluate it.
            scores = []
            for row in range(3):
                for col in range(3):
                    if not board.is_set((row, col)):
                        # Evaluate this move.
                        new_board = board.duplicate()
                        new_board.set((row, col), self.computer)
                        # print(' ' * depth, 'Move:', (row, col))
                        evaluation = self.minimax(new_board, self.player, depth=depth+1, limit=limit)
                        scores.append(evaluation)

            # print(' ' * depth, 'Computer has chosen:', max(scores, default=-10))
            return max(scores, default=-1)
        elif player == self.player:
            # Player's turn. Pick the worst move (for us) and evaluate it.
            scores = []
            for row in range(3):
                for col in range(3):
                    if not board.is_set((row, col)):
                        # Evaluate this move.
                        new_board = board.duplicate()
                        new_board.set((row, col), self.player)
                        # print(' ' * depth, 'Move:', (row, col))
                        evaluation = self.minimax(new_board, self.computer, depth=depth+1, limit=limit)
                        scores.append(evaluation)
            # print(' ' * depth, 'Player has chosen:', max(scores, default=10))
            return min(scores, default=1)

class Game:

    """The Tic-Tac-Toe game object."""

    def __init__(self, player='X', computer='O'):

        """Create the tic-tac-toe game object."""

        self.board = Board()
        self.turn = 'X'
        self.player = player
        self.computer = computer
        self.ai = Computer(self.computer, self.player)

        self.size = 500
        self.tile_size = self.size // 3
        self.game_over = False
        self.running = False
        self.winner = None

        pygame.init()

    def run_game(self):

        """Run the game."""

        self.screen = pygame.display.set_mode([self.size, self.size])
        pygame.display.set_caption('Tic-Tac-Toe')

        font = pygame.font.Font('freesansbold.ttf', 32)
        self.won_text = None

        self.running = True
        while self.running:
            # Handle events.
            self.handle_events()

            # Draw the screen.
            self.draw_screen()

            # Check if the game is won.
            if not self.game_over:
                if self.board.has_won(self.player):
                    self.game_over = True
                    self.winner = self.player
                    self.won_text = font.render('Player Wins!', True, (0, 0, 0))
                    self.won_rect = self.won_text.get_rect()
                    self.won_rect.center = (self.size // 2, self.size // 2)
                elif self.board.has_won(self.computer):
                    self.game_over = True
                    self.winner = self.computer
                    self.won_text = font.render('Computer Wins!', True, (0, 0, 0))
                    self.won_rect = self.won_text.get_rect()
                    self.won_rect.center = (self.size // 2, self.size // 2)
                if self.board.has_tie():
                    self.game_over = True
                    self.won_text = font.render("It's a tie!", True, (0, 0, 0))
                    self.won_rect = self.won_text.get_rect()
                    self.won_rect.center = (self.size // 2, self.size // 2)
            if not self.game_over:
                if self.turn == self.computer:
                    # Computer turn.
                    self.board.set(self.ai.calculate_move(self.board), self.computer)
                    self.turn = self.player

        pygame.quit()
    
    def handle_events(self):

        """Handle events."""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Player input.
                if self.turn == self.player and not self.game_over:
                    pos = pygame.mouse.get_pos()
                    row = pos[1] // self.tile_size
                    col = pos[0] // self.tile_size

                    if not self.board.is_set((row, col)):
                        self.board.set((row, col), self.player)
                        self.turn = self.computer

    def draw_screen(self):

        """Draw the screen."""

        self.screen.fill((255, 255, 255))

        if self.game_over:
            self.screen.blit(self.won_text, self.won_rect)
            pygame.display.flip()
            return

        # Draw the lines.
        
        pygame.draw.line(self.screen, (0, 0, 0), (0, self.tile_size), (self.size, self.tile_size), 5)
        pygame.draw.line(self.screen, (0, 0, 0), (0, self.tile_size * 2), (self.size, self.tile_size * 2), 5)
        pygame.draw.line(self.screen, (0, 0, 0), (self.tile_size, 0), (self.tile_size, self.size), 5)
        pygame.draw.line(self.screen, (0, 0, 0), (self.tile_size * 2, 0), (self.tile_size * 2, self.size), 5)

        # Draw the tiles.
        tile_padding = 20
        for row in range(3):
            for col in range(3):
                tile = self.board.get((row, col))

                if tile == None:
                    pass
                elif tile == 'X':
                    # Draw an X.
                    pygame.draw.line(self.screen, (0, 0, 0), (self.tile_size * col + tile_padding, self.tile_size * row + tile_padding), (self.tile_size * (col + 1) - tile_padding, self.tile_size * (row + 1) - tile_padding), 5)
                    pygame.draw.line(self.screen, (0, 0, 0), (self.tile_size * col + tile_padding, self.tile_size * (row + 1) - tile_padding), (self.tile_size * (col + 1) - tile_padding, self.tile_size * row + tile_padding), 5)
                elif tile == 'O':
                    # Draw an O.
                    pygame.draw.circle(self.screen, (0, 0, 0), (self.tile_size * col + self.tile_size // 2, self.tile_size * row + self.tile_size // 2), self.tile_size // 2 - tile_padding)
                    pygame.draw.circle(self.screen, (255, 255, 255), (self.tile_size * col + self.tile_size // 2, self.tile_size * row + self.tile_size // 2), self.tile_size // 2 - tile_padding - 5)

        pygame.display.flip()


if __name__ == '__main__':
    game = Game(player='O', computer='X')
    game.run_game()