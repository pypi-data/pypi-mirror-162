"""The Nim Game calculation functions

This module defines the functions that are needed to calculate moves and
decisions in a :class:`Mixin` for the :class:`.Nim` class.
"""


from __future__ import annotations
import functools
import random
from source.typedefs import Move, ErrorRate


class Mixin:
    """Class to implement the Nim game calculations
    
    This Mixin is used as an ancestor class for :class:`.Nim`, so
    that we can define methods here, in a separate module.
    
    The term "nimsum" (Grundy value or nim-value), used here, is the Nimber_
    that the game is equivalent to. This number represents the current state of
    the game.
    
    The importance of nimsum is whether it is zero or not. If nimsum is not
    zero, it can be changed to zero by the right move of the next player.
    If the nimsum is zero, the next move will change it to non-zero, whatever
    the move is. This way, the player who moves in a way to create zero nimsum
    is the one who drives the game and can win it.
    
    In case of "misère" type of game, there is a point in the course of the game
    where the strategy must reverse, because we want to opponent to take the
    last coin. This point is the beginning of the "end-game". In the end-game,
    all moves alternate the nimsum between 0 and 1. The winning player changes
    the nimsum to 1 and the losing player has no other choise but changing it to
    zero and ultimately taking the last coin.
    
    .. _Nimber: https://en.wikipedia.org/wiki/Nimber
    """
    def make_good_choice(self) -> bool:
        """Figures out whether to make a good decision or make an error

        The required error rate indicates how bad decisions the Computer is to
        make. The higher the error rate percentage the higher the possibility
        that the Computer makes a bad move/decision. If error_rate is 0, this
        function always returns True, i.e. the Computer always makes a good
        decision. If error_rate is 100, the Computer always makes a bad
        decision.

        Returns:
            False forces to make the bad choise
        """
        #figure out the error rate for the current player
        if isinstance(self.error_rate, ErrorRate):
            activeplayer = self.activeplayer
            if activeplayer == 'start':
                activeplayer = 'Computer'
            error_rate = getattr(self.error_rate, activeplayer)
        else:
            error_rate = self.error_rate
        
        #get a random percentage
        randompercentage = random.randint(0, 99)
        
        #return true/false based on the required error rate
        return randompercentage >= error_rate


    def get_nimsum(self) -> int:
        """Calcualte the nimsum of the set of heaps

        It uses the functools.reduce() on the heaps list, with a 0 initializing
        value and uses XOR for the coin counts of the heaps.

        Returns:
            The nimsum of the heap-set
        """
        return functools.reduce(
            lambda a, b: a^b,
            self.heaps,
            0
        )


    def all_one_heaps(self) -> bool:
        """Checks whether all non-zero heaps have 1 single coin

        It uses the functools.reduce() on the heaps list, with a True
        initializing value and keep it true as long as the number of coins is at
        most one.

        Returns:
            Whether all relevant heaps have 1 single coin
        """
        return functools.reduce(
            lambda a,b: a&(b<=1),
            self.heaps,
            True
        )


    def is_winning_for_next(self) -> bool:
        """Is the current status good for the player having the next turn?

        Usually non-zero nimsum is the winning status, so that the player
        can change it to zero nimsum. This way this player can force the other
        player to make non-winning move, i.e. creating non-zero nimsum, which
        this player can change to zero nimsum again, end so on.

        However, in "misère" type game, the strategy changes in the end-game
        moves. When all heaps only have 1 coin left, the winning status is when
        nimsum is zero. I.e. the all-heaps-has-one-coin reverses the bool
        nimsum. The boolean reversal is done with an XOR.
        
        Returns:
            Whether the current status is good for the player having the next
            turn
        """
        if self.misere:
            return bool(self.get_nimsum()) ^ self.all_one_heaps()
        else:
            return bool(self.get_nimsum())


    def get_random_move(self) -> Move:
        """Figure out a random but valid move
        
        This method is used when the algorithm does not care what to move. Just
        figure out a random but valid move.
        
        Returns:
            From which heap and how many coins are to be removed in the coming
            move
        """
        #pick a random index from the active (i.e. non-empty) heaps
        heapnumber = random.choice(
            [i for i in range(len(self.heaps)) if self.heaps[i]]
        )
        #pick a random remove count from the selected random heap
        removecount = random.randint(1, self.heaps[heapnumber])
        return Move(heapnumber, removecount)


    def figure_out_best_move(self) -> Move:
        """Figure out what to move so that we get into a winning position

        First handle the situation when all heaps only have 1 coin. If so,
        there is nothing to think about, just take that 1 coin from a heap
        randomly.

        Then check whether there is only 1 heap with more than 1 coins. This is
        the indicator for the end-game reversal in the "misère" type. The
        winning strategy here is to leave odd numbers of 1-coin heaps for the
        opponent. So, if the number of heaps with 1 coin is odd, take all
        coins from the heap that has more than 1 coin. If it is even, take all
        but 1 coin. Either way, this makes sure that odd number of 1-coin
        heaps are left for the opponent.

        Otherwise, we are in the middle of the game, so figure out the all-heap
        nimsum.
        If it is zero, the player in this current turn is in a losing position,
        because whatever we do we create a non-zero nimsum that the opponent
        can change to zero nimsum again in its turn. So, having no better
        option, we just take a random number of coins from a random heap and
        hope that the opponent makes a mistake.

        If nimsum is not zero, it can be made zero by removing a cretain number
        of coins from the right heap. Check each heap and calculate the "target"
        number of coins, to null the nimsum. E.g. if the nimsum is 7 (binary
        111), we need to remove all 3 binary digits, i.e. the 4, 2 and 1,
        without changing any other binary digits, e.g. the 8. If a given heap
        contains e.g. 9 coins (binary 1001), the "target" would be the
        7 :math:`\oplus` 9::
        
            1001
            0111
            ----
            1110 => decimal 14
        
        As we cannot remove 14 coins from a heap where there are 9 coins, this
        is not a suitable heap to remove coins from. So, go on until finding a
        suitable heap. Theoretically, there must be at least 1 suitable heap.

        Returns:
            From which heap and how many coins are to be removed in the coming
            move
        """
        #active heaps have 1 coin only?
        if self.all_one_heaps():
            #empty one of the 1-coin heaps, does not matter which one
            return self.get_random_move()

        #need to handle the "only 1 heap with more than 1 coin" situation?
        if self.misere:
            #number of bigger heaps
            bigheapcount = 0
            #by default the number of 1-coin heaps is even (NB. zero is even)
            even_singlecoins = True
            #loop on all heaps
            for idx, heapcount in enumerate(self.heaps):
                #big heap?
                if heapcount>1:
                    bigheapcount += 1
                    bigheapcontent = heapcount
                    bigheapidx = idx
                
                elif heapcount==1:
                    even_singlecoins = not even_singlecoins
            
            #entering end-game, i.e. only 1 heap with more than 1 coin?
            if bigheapcount==1:
                #even number of heaps with 1 coin?
                if even_singlecoins:
                    #remove all but 1 coin from the heap which has more coins
                    removecount = bigheapcontent-1
                else:
                    #remove all coins from the heap which has more coins
                    removecount = bigheapcontent
                #remove coins so that odd number of 1-coin heaps remain
                return Move(bigheapidx, removecount)

        #calcualte the nimsum of the set of heaps
        nimsum = self.get_nimsum()

        #not a winning position, i.e. nimsum is zero?
        if not nimsum:
            #cannot do any better but initiate a random move
            return self.get_random_move()

        #look for suitable heap, so that nimsum can be nulled
        for idx, heapcount in enumerate(self.heaps):
            #calculate the wished count of this heap (i.e. so that it causes
            #zero overall nimsum)
            target_count = heapcount ^ nimsum
            #note that the required target count may be more than the heap has
            #altogether. Is this one big enough?
            if target_count < heapcount:
                removecount = heapcount - target_count
                return Move(idx, removecount) 

        #not finding a suitable heap is impossible, I must have screwed up some
        #programming
        raise Exception('Cannot find suitable heap')
