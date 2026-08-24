"""
menu_state.py
-------------
Pantalla de inicio. Presionar ESPACIO para empezar a jugar.
"""

import pygame
from config import ANCHO, ALTO, BLANCO, AMARILLO, TITULO
from core.state import State


class MenuState(State):
    def __init__(self, game):
        super().__init__(game)
        self.fuente_titulo = pygame.font.SysFont("consolas", 30, bold=True)
        self.fuente_ayuda = pygame.font.SysFont("consolas", 18)

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
            from states.overworld_state import OverworldState
            self.game.cambiar_estado(OverworldState(self.game))

    def actualizar(self, dt):
        pass

    def dibujar(self, pantalla):
        titulo = self.fuente_titulo.render(TITULO, True, AMARILLO)
        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, ALTO // 2 - 60))

        ayuda = self.fuente_ayuda.render("Presiona ESPACIO para empezar", True, BLANCO)
        pantalla.blit(ayuda, (ANCHO // 2 - ayuda.get_width() // 2, ALTO // 2))

        controles = self.fuente_ayuda.render(
            "Muévete: flechas / WASD   |   Responder en duelo: teclas 1-4", True, BLANCO
        )
        pantalla.blit(controles, (ANCHO // 2 - controles.get_width() // 2, ALTO // 2 + 40))
