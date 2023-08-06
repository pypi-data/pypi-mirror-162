"""Type definitions

Users of the API can use the following structure definitions for providing
arguments or checking returns (see detalis below):

- :class:`Move`
- :class:`ErrorRate`
- :class:`HeapCoinRange`

E.g. the user can provide a move for the :meth:`.do_move()`
by :code:`nimgame.Move('A', 3)`.

This module also defines complex types and instance sets.
Unlike the structure definitions above, these types and sets are not published
on package level, because they are hardly ever needed for the API users. Anyway,
this module can be imported, if needed, and the definitions used. See the
source_ for details.

Complex types are used for annotations and they are unions of possible types for
that element. E.g. :attr:`ErrorRate_T` can be a simple :class:`int` or
:attr:`ErrorRate`.

Instance sets are used for validations of input data by :func:`isinstance`.

.. _source: ../_modules/typedefs.html
"""


import collections
from typing import Union, List, Tuple


Move = collections.namedtuple('Move', 'heapdesig removecount')
"""How many coins are to be removed and from what heap"""

# The error rate percentages can be defined for parties separately
ErrorRate = collections.namedtuple('ErrorRate', 'Computer Player')
"""The required error for the parties, separately, when the program is to
calculate the moves for both players"""

HeapCoinRange = collections.namedtuple('HeapCoinRange', 'min max')
"""Heap or coin count ranges for automatic heap setup"""


ErrorRate_T = Union[int, ErrorRate]
"""Can be an int generally, or ErrorRate for separate definition"""
ErrorRateTypes = (
    int, 
    ErrorRate
)

MyTurn_T = Union[str, bool]
"""How the user can indicate its requirement of the starting party"""

HeapCoinRange_T = Union[
    List[int],
    Tuple[int, int],
    HeapCoinRange
]
"""Can be a sequence of int or HeapCoinRange"""
HeapCoinRangeTypes = (
    list, 
    tuple, 
    HeapCoinRange
)

def dummy():
    """dummy, just to force sphinx.ext.viewcode to generate the source html"""
