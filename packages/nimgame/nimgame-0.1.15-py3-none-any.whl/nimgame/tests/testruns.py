"""Run tests of the Nim Game automatically

:func:`play_full_game` plays one full game automatically, doing the moves for
both parties, according to their set error rates in the :class:`Nim` instance

:func:`run_many_games` creates a :class:`Nim` instance and runs several games
automatically
"""


from source.core import Nim
from source.typedefs import ErrorRate, ErrorRate_T


def play_full_game(
        nim: Nim
) -> dict:
    """Play one full game
    
    There is no interaction, both players' moves are calculated by the program.
    We just call the 1st player as Computer and the 2nd as Player.
    
    It creates random heaps first. Then, figures out whether Computer is to
    start.
    This decision is based on the starting nimsum on Computer's favour, but with
    the Computer's error rate. Player and Computer take turns until the game
    ends. Moves are calculated with the same algorithm for the Computer and
    Player, but with different error rates.
    
    Args:
        nim: the :class:`Nim` instance, created with the init arguments, like
            `error_rate`

    Returns:
        The result of the game.
        Keys in the returned dict:
        
            - step_records: a list of statuses at each move
            - computer_won: a bool stating whether the "Computer" won
    """
    #create new random heaps
    nim.setup_heaps()
    #init compturn automatically
    nim.set_start()

    #init the step storage
    step_records = []
    step_records.append(
        nim.get_heapstatus() + f' before {nim.activeplayer}'
    )

    #do moves in a loop, until game end
    while not nim.game_end():
        #make a good decision?
        if nim.make_good_choice():
            #figure out the best move (what heap and how many coins)
            move = nim.figure_out_best_move()
        else:
            #set a random (most probably not good) move
            move = nim.get_random_move()

        #do and record a move
        nim.do_move(move)
        step_records.append(
            nim.get_heapstatus() + f' before {nim.activeplayer}'
        )

    #Computer won if it was its turn after the last coin was taken
    step_records.append(f'{nim.activeplayer} won')

    return dict(
        step_records=step_records,
        computer_won=(nim.activeplayer=='Computer') ^ (not nim.misere)
    )


def run_many_games(
    gamenum: int, 
    error_rate: ErrorRate_T
) -> None:
    """Run several games automatically
    
    This function starts with creating a :class:`Nim` instance with setting the
    required error rates. It then calls :func:`play_full_game` for each game. It
    prints a + when the "Computer" wins, and - when the "Player" wins.
    
    Then it prints the percentage the "Computer" won.
    
    Args:
        gamenum: the number of games to run
        error_rate: the required rate of bad decisions to be made by each player
    """
    #Computer's success
    won_games = 0

    #Computer failure details, in case it's needed
    lost_games = []

    #instantiate Nim
    nim = Nim(
        error_rate=error_rate, 
    )

    #do several games to collect statistics
    for _ in range(gamenum):
        #play one game
        game_result = play_full_game(nim)
        #Computer win?
        if game_result['computer_won']:
            won_games += 1
            print('+',  end='')
        else:
            lost_games.append(game_result['step_records'])
            print('-',  end='')
    print("\n")

    if won_games == gamenum:
        print(f"Computer won all the {gamenum} games, Player had no chance")
    else:
        if isinstance(error_rate, ErrorRate):
            error_rate = error_rate.Computer
        if error_rate:
            print(f"Computer won {won_games/gamenum*100}%")
        else:
            print(
                f"Computer only won {won_games/gamenum*100}%, "
                "in spite its error rate was 0%, WTF?!")
            for lost_game in lost_games:
                print('-'*40)
                for move in lost_game:
                    print(move)
