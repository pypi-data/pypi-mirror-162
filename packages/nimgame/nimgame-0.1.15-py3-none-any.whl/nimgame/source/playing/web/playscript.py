"""Functions called from py-script tags of the play.html page

This module is imported by PyScript when reading the <py-script> tag in
environ/frontend/play.html.

Importing the __init__ as nimgame enables functions in this module to use the
package from local sources. This way all public objects of the package (like the
Nim class) becomes accessible, as if the package was imported from PyPi.
"""


import js
import __init__ as nimgame


def main_dynamics():
    """Set up and initiate the game in the web browser"""
    div = js.document.getElementById("results")
    div.innerHTML = 'result2'

    nim = nimgame.Nim()
    nim.setup_heaps()
    nim.get_heapstatus()
    nim.set_start()
    nim.get_heapstatus()
    nim.do_move(nimgame.Move('a',1))
    nim.get_heapstatus()
