"""Demonstrate the features of the package with a small interactive execution

Since this module may be called from anywhere and even the package might not
have been installed yet, the package path is inserted into the sys.path if
missing. From that point on, imports like source.core work fine.

In order to demonstrate the correct usage of the package objects (e.g. the Nim
class), i.e. referring to it as `nimgame.Nim`, regardless of where this class is
actually created in the source, we create simulated namespace, fill it up with
the objects imported from their actual place, and call it nimgame.
"""


import types

# Insert the package into the system path
import sys, os
basepath = os.path.dirname(__file__)
packagepath = os.path.abspath(os.path.join(basepath, '../..'))
if packagepath not in sys.path:
    sys.path.insert(0, packagepath)

# Simulate "import nimgame" (as the package may not be installed yet)
from source.core import Nim as _Nim
from source.typedefs import ErrorRate as _ErrorRate
from source.playing.cli.play import playCLI as _playCLI
from source.playing.web.play import playweb as _playweb
nimgame = types.SimpleNamespace()
nimgame.Nim = _Nim
nimgame.ErrorRate = _ErrorRate
nimgame.playCLI = _playCLI
nimgame.playweb = _playweb

from source.playing.cli import ansi


def run():
    """Run the interactive CLI demo"""
    try:
        while True:
            testtype = input(
                'Press '
                '"m" for running multiple games'
                '; '
                '"p" for playing an interactive game'
                '; '
                '"w" for running the web server'
                '; [p]: '
            ) or 'p'
            ansi.clean_prev_line()

            if testtype=='m':
                #do the test with 1000 games
                gamecount = 1000
                #request 10% Computer and 20% Player error rate
                error_rate = nimgame.ErrorRate(Computer=10, Player=20)
                #run all tests
                from tests import testruns
                testruns.run_many_games(gamecount, error_rate)
                break
            
            elif testtype=='p':
                nimgame.play_CLI()
                break
            
            elif testtype=='w':
                nimgame.playweb()
                break

    except KeyboardInterrupt:
        #Ctrl-C happens when input is waiting, so delete that prompt
        ansi.clean_this_line()
        print('Game terminated by the user pressing Ctrl-C')
        exit(2)
        
    except Exception as e:
        print(e)
        exit(1)

    exit(0)


if __name__ == '__main__':
    run()
