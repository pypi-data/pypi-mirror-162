"""Play the Game of Nim, interactively or using the API


About
=====

This package implements the game called Nim. The game can be played
interactively in the CLI, or in a web browser. You can install this package and
play the game. Easy::

> pip install nimgame
> nimgame

You can actually TryIt_, before installing anything.

Those, who are more of the developer types, can use the API, after installing
the package. The game can then be embedded in other applications and played
from any other kind of a GUI.

For mathematicians/statisticians, it can also be used for creating statistics
by running multiple games. If you know `combinatorial game theory`_ terms like
`sequential game`_, `perfect information`_, `impartial game`_,
`Sprague–Grundy theorem`_, this API can be useful for you.


Game Rules
===========

For the general description of the Nim and similar games, see the
`Wikipedia page`_.

The game is played with coins arranged in heaps. There may be any number of
heaps and any number of coins in a heap.

Two palyers play the game. The computer can be a player. Players take turns. In
each turn, a player takes coins from one (only 1) heap. There is no upper limit
of taken coins (but the heap size).  At least 1 coin must be taken.

There are 2 types of the game:

- the "normal" game is where the player, who takes the last coin, wins
- the "misère_" game is where the player, who has to take the last coin, loses


API Usage
==========

First, the heaps are to be set up. The starting heaps then can be analysed and
the starting player selected. If it is the Computer, it automatically does the
1\ :sup:`st` move. Then the Player is to do the next move, then the Computer
moves, and so on. When no more coins left, the game ends.

.. code:: python

    import nimgame
    nim = nimgame.Nim(error_rate=10)  # Make the Computer do 10% errors
    nim.setup_heaps()  # Create heaps randomly
    nim.set_start(myturn=True)  # Indicate that the Player wants to start
    nim.do_move(nim.Move('b', 4))  # From heap 'B', remove 4 coins
    ...
    if nim.game_end():
        exit(0)


Available objects in the package
================================

While different objects are defined in the source at different levels (e.g. the
Nim class in the source/core.py module), the necessary ones are made available
at the package level, i.e. after importing nimgame, the `nimgame.Nim` refers to
that class.

Nim
    The main class of the game
playCLI
    A function that interactively plays the game in CLI
playweb
    A function that interactively plays the game in in a local web browser
Move
    A :py:func:`collections.namedtuple` with `heapdesig` and `removecount`
    fields for defining a move, i.e. what heap is to be reduced and by how many
    coins.
    `heapdesig` can be an int (heap numbers start from zero), or a letter (case
    insensitive). E.g. number 1 is the same as "B" or "b".
ErrorRate
    A :py:func:`collections.namedtuple` with `Computer` and `Player` fields for
    defining the required error rates percentage for the players. Only used when
    both of them are simulated.
HeapCoinRange
    A :py:func:`collections.namedtuple` with `min` and `max` fields for defining
    the ranges for numbers of heaps and heap sizes. These ranges are used for
    automatic heap creation.


Main Package content
====================

:mod:`core`
    It provides the :class:`.Nim` class and its public methods

:mod:`calculations`
    A mixin of the :class:`.Nim` class with calculation methods

:mod:`playing.demo`
    Functions to play the game. They can be run to do interactions for executing
    automatic runs or interactive games. The same is executed when
    
    -   the package itself is called, see the "__main__.py" module, e.g.
    
        :command:`python -m nimgame`
        
    -   the :command:`nimgame.exe` (in Scripts) is executed.
        
        NB, the python Scripts dir is usually in the execution path, i.e. the
        nimgame.exe should be available from anywhere in the CLI prompt.

:mod:`tests.testruns`
    You can test the function by running several games automatically and gather
    statistics.


.. _TryIt: http://donno.yet.com
.. _Wikipedia page: https://en.wikipedia.org/wiki/Nim
.. _misère: https://en.wikipedia.org/wiki/Mis%C3%A8re#Mis%C3%A8re_game
.. _combinatorial game theory: https://en.wikipedia.org/wiki/Combinatorial_game_theory
.. _sequential game: https://en.wikipedia.org/wiki/Sequential_game
.. _perfect information: https://en.wikipedia.org/wiki/Perfect_information
.. _impartial game: https://en.wikipedia.org/wiki/Impartial_game
.. _Sprague–Grundy theorem: https://en.wikipedia.org/wiki/Sprague%E2%80%93Grundy_theorem
"""
# Make sure the package base path is in the module import path (e.g. for flit)
import sys, pathlib
basepath = str(pathlib.PurePath(__file__).parent)
if basepath not in sys.path:
    sys.path.insert(0, basepath)

# Version info to be made available globally
from source import version
__version_info__ = version.__version_info__
__version__ = version.__version__

# Make the Nim class available on package level
from source.core import Nim
# Make structures available on package level
from source.typedefs import Move, ErrorRate, HeapCoinRange

# Make the playing functions available on package level
from source.playing.cli.play import playCLI
from source.playing.web.play import playweb

# For using the API in command line (e.g. Jupyter) and import all
__all__ = (
    'Nim', 
    'Move', 'ErrorRate', 'HeapCoinRange', 
    'playCLI', 
    'playweb'
)
