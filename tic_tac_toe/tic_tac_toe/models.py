from random import shuffle, choice

from django.contrib.auth.models import User
from django.db import models
from django_mysql.models import ListCharField

BOARD_SIZE = 3
X = 'X'
O = 'O'
EMPTY = ' '
STATUS_ACTIVE = 'A'
STATUS_OVER = 'O'
STATUS_INACTIVE = 'I'
STATUS_TIE = 'T'
STATUS_CHOICES = ((STATUS_ACTIVE, 'active'), (STATUS_OVER, 'over'), (STATUS_INACTIVE, 'inactive'), (STATUS_TIE, 'tie'))
COMPUTER = 'Computer'


class Game(models.Model):
    board = ListCharField(base_field=models.CharField(max_length=1), size=BOARD_SIZE * BOARD_SIZE, max_length=BOARD_SIZE * BOARD_SIZE * 2) # plus commas , default=INITIAL_BOARD)
    player_x = models.ForeignKey(User, related_name="game_player_x", on_delete=models.RESTRICT, null=True)
    player_o = models.ForeignKey(User, related_name="game_player_o", on_delete=models.RESTRICT, null=True)
    current_player = models.ForeignKey(User, related_name="game_current_player", on_delete=models.RESTRICT, null=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=1)

    def get_board(self):
        return self.board

    def set_status(self, status):
        self.status = status
        self.save()

    def init_game(self, player_one, player_two=None):
        self.board = self.get_clear_board()
        self.set_players(player_one, player_two)
        self.current_player = self.player_x
        self.status = STATUS_ACTIVE
        self.save()

    @staticmethod
    def get_clear_board():
        return [EMPTY for i in range(BOARD_SIZE * BOARD_SIZE)]

    def set_players(self, player_one, player_two):
        """ Randomly determine players roles. """
        players_order = [player_one, player_two]
        shuffle(players_order)
        self.player_x = players_order[0]
        self.player_o = players_order[1]

    def get_current_player_designation(self):
        if self.current_player == self.player_x:
            return X
        else:
            return O

    def get_game_data(self):
        game_data = {
            'is_over': self.status == STATUS_OVER,
            'is_tie': self.status == STATUS_TIE,
            'board': self.board,
            'player': self.get_player_name()
        }
        print('game data is {}'.format(game_data))

        return game_data

    def is_over(self):
        """ Check if the current board state has a winning. """
        # Winning by row
        for r in range(BOARD_SIZE):
            row = [self.board[r * BOARD_SIZE], self.board[(r * BOARD_SIZE) + 1], self.board[r * BOARD_SIZE + 2]]
            if self.is_winning_path(row):
                return True

        # Winning by col
        for c in range(BOARD_SIZE):
            col = [self.board[c], self.board[(c + BOARD_SIZE)], self.board[c + (2 * BOARD_SIZE)]]
            if self.is_winning_path(col):
                return True

        # Winning by left diagonal
        left_diagonal = [self.board[0], self.board[4], self.board[8]]
        if self.is_winning_path(left_diagonal):
            return True

        # Winning by right diagonal
        right_diagonal = [self.board[2], self.board[4], self.board[6]]
        if self.is_winning_path(right_diagonal):
            return True

        return False
    
    @staticmethod
    def is_winning_path(path):
        return path.count(path[0]) == len(path) and path[0] != EMPTY

    def is_free_cell(self, row, col):
        """ Returns if the cell is occupied. """
        return self.board[self.get_cell_from_position(row, col)] == EMPTY

    def set_move(self, row, col):
        self.board[self.get_cell_from_position(row, col)] = self.get_current_player_designation()
        self.compute_board_status()
        self.save()

    @staticmethod
    def get_cell_from_position(row, col):
        """ A board is represented as an array, this function returns the board's index by row and col. """
        return row * BOARD_SIZE + col

    def switch_current_player(self):
        if self.current_player == self.player_x:
            self.current_player = self.player_o
        else:
            self.current_player = self.player_x

        self.save()

    def get_empty_cells(self):
        return [i for i, cell in enumerate(self.board) if cell == EMPTY]

    def computer_move(self):
        empty_cells = self.get_empty_cells()
        chosen_cell = choice(empty_cells)
        # use div to get the row from the board array, and mod to get the col
        self.set_move(int(chosen_cell / BOARD_SIZE), chosen_cell % BOARD_SIZE)

    def compute_board_status(self):
        if self.is_over():
            # Game is over, we have a winner
            self.set_status(STATUS_OVER)
        elif not self.get_empty_cells():
            # No empty cells, but game hasn't been won yet, so it's a tie
            self.set_status(STATUS_TIE)
        else:
            # No winner and able to add another move, switch players
            self.switch_current_player()

    def get_player_name(self):
        if not self.current_player:
            return COMPUTER

        return self.current_player.first_name

    @staticmethod
    def is_legal_move(row, col):
        """ A move is defined legal, if it's within the range of the board. """
        return 0 <= row <= BOARD_SIZE and 0 <= col <= BOARD_SIZE
