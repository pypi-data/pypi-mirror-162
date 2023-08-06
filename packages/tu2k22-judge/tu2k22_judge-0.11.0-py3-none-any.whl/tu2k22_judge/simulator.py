from email import message
from typing import Any, List, Tuple
import json
import logging

import requests
from requests import Timeout
from colorama import Fore, Style
from pydantic import ValidationError

from .schema import Piece, Move, Player, InvalidMovesMessage, BotResponse, PlayerMove
from .custom_exceptions import InvalidMovesException, TimeoutException, MovesExceededException
from .constants import MAX_MOVES_ALLOWED
from .logger_utils import get_logger


class Simulator:
    def __init__(self, move_timeout: int = 4, verbose: bool = True, logging_level: int = logging.WARNING) -> None:
        pieces = ['B', 'b', '_', 'r', 'R']
        self.board = [[pieces[i] for _ in range(5)] for i in range(5)]
        self.RED_PIECES = [Piece.RED_BOMBER, Piece.RED_STINGER]
        self.BLUE_PIECES = [Piece.BLUE_BOMBER, Piece.BLUE_STINGER]
        self.move_timeout = move_timeout
        self.logger = get_logger(__name__, level=logging_level)
        self.verbose = verbose

    def print_board(self):
        """
            Print Board state while testing bots in local development
        """
        if self.verbose:
            print(Fore.BLACK + Style.BRIGHT + "  0 1 2 3 4")
            for index, row in enumerate(self.board):
                print(Fore.BLACK + Style.BRIGHT + str(index) + " ", end="")
                for cell in row:
                    if cell in self.RED_PIECES:
                        print(Fore.RED + cell + " ", end="")
                    elif cell in self.BLUE_PIECES:
                        print(Fore.BLUE + cell + " ", end="")
                    else:
                        print(Fore.WHITE + cell + " ", end="")
                print(Fore.RESET + Style.RESET_ALL)

    @staticmethod
    def validate_direction(move: Move, player: Player):
        """
        Check if player is moving in correct vertical direction, blue should move down the board, red should move up
        """
        sign = 2*player - 1
        absolute_direction = move.dst.row - move.src.row
        if absolute_direction*sign < 0:
            raise InvalidMovesException(
                reason=InvalidMovesMessage.INVALID_DIRECTION, player=player)

    def validate_endpoints(self, move: Move, player: Player) -> None:
        """
        Check if the source and destination endpoints are valid.
        Source should hold a piece of the player and destination should be an empty space
        Raise an exception if this is not followed, return None otherwise

        Parameters
        ----------
        move : Move
        player : Player

        Raises
        ------
        InvalidMovesException
        InvalidMovesException
        """
        if self.board[move.dst.row][move.dst.col] != Piece.EMPTY_SPACE:
            raise InvalidMovesException(reason=InvalidMovesMessage.INVALID_DESTINATION, player=player)
        if (player == player.BLUE and self.board[move.src.row][move.src.col] not in self.BLUE_PIECES) or (
            player == player.RED and self.board[move.src.row][move.src.col] not in self.RED_PIECES
        ):
            raise InvalidMovesException(reason=InvalidMovesMessage.INVALID_SOURCE, player=player)
        return None

    def validate_elimination_move(self, move: Move, player: Player) -> None:

        if move.src.row == move.dst.row == 0 or move.src.row == move.dst.row == 4:
            raise InvalidMovesException(
                reason=InvalidMovesMessage.HOME_ROW_ELIMINATION_FORBIDDEN, player=player)
        eliminated_row = int((move.src.row + move.dst.row) / 2)
        eliminated_col = int((move.src.col + move.dst.col) / 2)
        eliminated_piece = self.board[eliminated_row][eliminated_col]

        if (
            player == Player.RED and eliminated_piece in self.BLUE_PIECES
        ) or (
            player == Player.BLUE and eliminated_piece in self.RED_PIECES
        ):
            return None
        else:
            print(f"{self.BLUE_PIECES}, {self.RED_PIECES}")
            print(f"player {player}, elim_coords {eliminated_row, eliminated_col}, eliminated_piece: {eliminated_piece}")
            raise InvalidMovesException(
                reason=InvalidMovesMessage.INVALID_ELIMINATION_TARGET, player=player)

    def validate_stinger_move(self, move: Move, player: Player):
        if abs(move.src.row - move.dst.row) == abs(move.src.col - move.dst.col) == 1:
            # simply diagonal move (direction in y axis has already been validated)
            return None
        elif (
            # horizontal elimination
            abs(move.src.row - move.dst.row) == 2 and move.src.col == move.dst.col
        ) or (
            # vertical elimination
            abs(move.src.col - move.dst.col) == 2 and move.src.row == move.dst.row
        ):
            self.validate_elimination_move(move, player)
        else:
            # move doesn't fit either simple moves or elimination moves
            raise InvalidMovesException(
                reason=InvalidMovesMessage.INVALID_STINGER_MOVE, player=player)

    def validate_bomber_move(self, move: Move, player: Player):
        if abs(move.src.col - move.dst.col) <= 1 and abs(move.src.row - move.dst.row) <= 1 and move.src != move.dst:
            return  # single move in any direction
        elif (
            # horizontal elimination
            abs(move.src.row - move.dst.row) == 2 and move.src.col == move.dst.col
        ) or (
            # vertical elimination
            abs(move.src.col - move.dst.col) == 2 and move.src.row == move.dst.row
        ):
            self.validate_elimination_move(move, player)
        else:
            raise InvalidMovesException(
                reason=InvalidMovesMessage.INVALID_BOMBER_MOVE, player=player)

    def validate_move(self, move: Move, player: Player) -> None:
        """
        Check if the move is valid for the given board state and given Player
        Raise the required exception if move is invalid, return None otherwise
        Parameters
        ----------
        move : Move
        player : Player
        """
        self.logger.info(f"Validating Player {player} Move")
        if self.verbose:
            if player == Player.BLUE:
                color = Fore.BLUE
            else:
                color = Fore.RED
            print(color + Style.BRIGHT + f"Player {player} move")
            print(color + Style.BRIGHT + str(move))
            print(Fore.RESET + Style.RESET_ALL)
        self.validate_direction(move, player)
        self.validate_endpoints(move, player)
        piece = self.board[move.src.row][move.src.col]
        if piece in [Piece.BLUE_STINGER, Piece.RED_STINGER]:
            self.validate_stinger_move(move, player)
        else:
            self.validate_bomber_move(move, player)

    def make_move(self, move: Move, player: Player):
        """
        Make the given move and Modify the board state accordingly

        Parameters
        ----------
        move : Move
        player : Player
        """
        self.board[move.dst.row][move.dst.col] = self.board[move.src.row][move.src.col]
        self.board[move.src.row][move.src.col] = Piece.EMPTY_SPACE
        if abs(move.src.row - move.dst.row) == 2 or abs(move.src.col - move.dst.col) == 2:
            eliminated_x_coord = int((move.src.row + move.dst.row) / 2)
            eliminated_y_coord = int((move.src.col + move.dst.col) / 2)
            self.board[eliminated_x_coord][eliminated_y_coord] = Piece.EMPTY_SPACE

    def check_if_game_over(self) -> Tuple[bool, Player | None]:
        # RED BOMBER reaches blue home row
        if Piece.RED_BOMBER in self.board[0]:
            return True, Player.RED
        # BLUE BOMBER reaches red home row
        elif Piece.BLUE_BOMBER in self.board[4]:
            return True, Player.BLUE
        return False, None

    def run(self, bot_urls: List[str], bot_data: List[Any], player_moves: List[PlayerMove]):
        player = Player.BLUE
        self.logger.info("STARTING GAME")
        self.print_board()
        while len(player_moves) < MAX_MOVES_ALLOWED:
            bot_input = {"board": self.board, "data": bot_data[player], "player": player}

            response = requests.post(bot_urls[player], json=bot_input, timeout=self.move_timeout, headers={"Content-Type": "application/json"})
            if response.status_code != 200:
                self.logger.error(
                    f"Invalid status code {response.status_code} received from player {player}. Expected: {200}")
                raise InvalidMovesException(InvalidMovesMessage.INVALID_STATUS_CODE, player=player)

            try:
                bot_response = BotResponse.validate(response.json())
                bot_data[player] = bot_response.data
                player_moves.append(PlayerMove(move=bot_response.move, player=player))

                self.validate_move(bot_response.move, player=player)
                self.make_move(bot_response.move, player=player)
                self.print_board()
                game_over, winner = self.check_if_game_over()
                if game_over:
                    if self.verbose:
                        print(f"Player {player} wins")
                    return winner
                if player == Player.BLUE:
                    player = Player.RED
                else:
                    player = Player.BLUE
            except InvalidMovesException as imex:
                self.logger.error(f"Invalid response received from player: {player}. Message: ", imex.message)
                raise InvalidMovesException(reason=imex.reason, player=player)  # append player info to exception
            except Timeout as t:
                self.logger.error(f"Request to player: {player} times out")
                raise TimeoutException(player=player)
            except ValidationError as ve:
                self.logger.error(f"Invalid response received from player: {player}. Message: ", str(ve))
                raise InvalidMovesException(reason=f"Incorrect schema", player=player)
        raise MovesExceededException()
