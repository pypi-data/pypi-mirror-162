from typing import List, Dict
import logging

import typer

from .simulator import Simulator
from .custom_exceptions import InvalidMovesException,  TimeoutException, MovesExceededException
from .schema import PlayerMove, Player, GameResult, Position, Move, Piece
from .log_writer import LogWriter
from .logger_utils import get_logger

app = typer.Typer()


@app.command()
def play_game(
    player1: str = typer.Option(
        ..., help="The url of the bot for player 1",
    ),
    player0: str = typer.Option(
        ..., help="The url of the bot for player 0"
    ),
    log_file: str = typer.Option(
        default="game.log", help="The path to which log file should be written"
    ),
    visualize: bool = typer.Option(
        default=False, help="Whether to print out board states and moves when running simulator"
    ),
    log_level: int = typer.Option(
        default=logging.WARNING, help="Logs level for simulator logs", show_default=True
    ),
    context: str = typer.Option(
        default="", help="Context to add in logs when multiple matches are being run simultaneously"
    )
) -> GameResult:
    """
    Judge for the TU game. Enter the endpoints for bots
    let the judge play out the match
    """
    bot_data = [{}, {}]
    player_moves: List[PlayerMove] = []
    print(log_level)
    logger = get_logger(__name__, level=log_level)
    game_simulator = Simulator(
        verbose=visualize, logging_level=log_level)
    try:
        logger.info(
            f"Starting simulation of game for bot1: {player1}, bot2: {player0}")
        winner = game_simulator.run([player1, player0],
                                    bot_data=bot_data, player_moves=player_moves)
        logger.info(
            "Game successfully completed. Writing game moves to log file")
        log_writer = LogWriter(
            path=log_file, player_moves=player_moves, winner=winner)
        log_writer.write()
        result = GameResult.PLAYER1_WINS if winner == Player.BLUE else GameResult.PLAYER0_WINS
        logger.info(f"Game completed. Result: {result}")
        return result
    except (InvalidMovesException, TimeoutException) as ex:
        logger.error(
            f"Invalid move by player {ex.player}. Reason: {ex.message}")
        logger.info(
            "Game completed with errors. Writing game moves to log file")
        log_writer = LogWriter(
            path=log_file, player_moves=player_moves, error_message=ex.message)
        log_writer.write()
        result = GameResult.PLAYER1_WINS if ex.player == Player.RED else GameResult.PLAYER0_WINS
        logger.info(f"Game Completed. Result: {result}")
        return result
    except MovesExceededException as ex:
        logger.error(
            f"{ex.message}")
        logger.info(
            "Game completed with errors. Writing game moves to log file")
        log_writer = LogWriter(
            path=log_file, player_moves=player_moves, error_message=ex.message)
        log_writer.write()
        return GameResult.DRAW
    except Exception as ex:  # just in case
        logger.error(
            "Internal error while simulating game. Invalidating Game result")
        logger.error(ex)
        log_writer = LogWriter(
            path=log_file, player_moves=player_moves, error_message=str(ex))
        log_writer.write()
        return GameResult.INVALID


if __name__ == '__main__':
    app()
