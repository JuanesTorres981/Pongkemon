"""
main.py
-------
Punto de entrada. Solo arma el Game y arranca en el menú.
No poner lógica de juego aquí, solo el arranque.
"""

from core.game import Game
from states.menu_state import MenuState


def main():
    juego = Game()
    juego.cambiar_estado(MenuState(juego))
    juego.correr()


if __name__ == "__main__":
    main()
