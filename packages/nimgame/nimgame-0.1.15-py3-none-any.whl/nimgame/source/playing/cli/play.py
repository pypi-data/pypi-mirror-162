"""Play an interactive Nim Game in the CLI
"""


from source.core import Nim
from source.typedefs import Move
from source.playing.cli import ansi


def playCLI() -> None:
    """Play one interactive game

    Create random heaps first. Then, get the user to select who to start.
    Player and Computer take turns until the game ends. Computer will make good
    or bad decisions based on the error rate set in the instance attribute.
    """
    #create instance and random heaps, then display them
    nim = Nim()
    nim.setup_heaps()
    print(nim.get_heapstatus())
    
    #by default there is no error in input
    errormsg = ''
    
    #loop on getting the Computer error rate requirement
    while True:
        errorrate = input(
            f'{errormsg}Computer error rate % [10]: '
        ) or '10'
        ansi.clean_prev_line()
        try:
            errorrate = int(errorrate)
            if not (0<=errorrate<=100):
                raise ValueError('Expecting % between 0 and 100')
            #set the error rate
            nim.set_error_rate(errorrate)
        except Exception as e:
            errormsg = str(e) + '; '
        else:
            errormsg = ''
            break
    
    #loop on getting the first move requirement
    while True:
        moveby = input(
            f'{errormsg}First move by? (Auto, Random, Computer, Player) [a]: '
        ) or 'a'
        ansi.clean_prev_line()
        try:
            #init compturn automatically
            nim.set_start(moveby)
        except ValueError as e:
            errormsg = str(e) + '; '
        else:
            errormsg = ''
            break
    
    #initiate the last move string
    lastmovestr = 'a1'
    
    #do moves in a loop, until game end
    while not nim.game_end():
        if nim.activeplayer == 'Computer':
            #make a good decision?
            if nim.make_good_choice():
                #figure out the best move
                move = nim.figure_out_best_move()
            else:
                #set a random (most probably not good) move
                move = nim.get_random_move()
        else:
            while True:
                movestr = input(
                    f'{errormsg}Heap?/Coins? [{lastmovestr}]: '
                ) or lastmovestr
                ansi.clean_prev_line()
                if not len(movestr): continue
                heapletter = movestr[:1]
                try: removecount = int(movestr[1:])
                except ValueError: continue
                if removecount < 0: continue
                move = Move(heapletter, removecount)
                lastmovestr = movestr
                break

        try:
            nim.do_move(move)
            errormsg = ''
        except ValueError as e:
            errormsg = str(e) + '; '
            continue
        print(nim.get_heapstatus())

    #The active player won after the last coin was taken by the opponent
    print(f'{nim.activeplayer} won')
