"""
menu_state.py
-------------
Pantalla de inicio. Presionar ESPACIO para empezar a jugar.
"""

import math
import pygame
from config import ANCHO, ALTO, BLANCO, AMARILLO, MAPA_FONDO
from core.state import State
from core.audio import audio
from core.asset_manager import assets
from core.ui import dibujar_marco, dibujar_sombra


class MenuState(State):
    def __init__(self, game):
        super().__init__(game)
        self.fuente_titulo = pygame.font.SysFont("consolas", 44, bold=True)
        self.fuente_sub = pygame.font.SysFont("consolas", 20, bold=True)
        self.fuente_ayuda = pygame.font.SysFont("consolas", 16)
        self.tiempo = 0.0

    def al_entrar(self):
        audio.musica("musica_mapa")

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
            audio.efecto("seleccionar")
            from states.overworld_state import OverworldState
            self.game.cambiar_estado(OverworldState(self.game))

    def actualizar(self, dt):
        self.tiempo += dt

    def dibujar(self, pantalla):
        # fondo: el mapa del juego, oscurecido
        if assets.existe(MAPA_FONDO):
            pantalla.blit(assets.get_image(MAPA_FONDO, size=(ANCHO, ALTO)), (0, 0))
            velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            velo.fill((0, 0, 20, 150))
            pantalla.blit(velo, (0, 0))

        # título en un marco
        titulo = self.fuente_titulo.render("PING PONG RPG", True, AMARILLO)
        sub = self.fuente_sub.render("Del ping pong al tenis de mesa", True, BLANCO)
        caja = pygame.Rect(0, 0, max(titulo.get_width(), sub.get_width()) + 80, 130)
        caja.midtop = (ANCHO // 2, 50)
        dibujar_marco(pantalla, caja)
        pantalla.blit(titulo, titulo.get_rect(midtop=(caja.centerx, caja.y + 24)))
        pantalla.blit(sub, sub.get_rect(midtop=(caja.centerx, caja.y + 82)))
        pelota = assets.get_image("ui/ball.png", size=(20, 20))
        pantalla.blit(pelota, (caja.x + 18, caja.y + 18))
        pantalla.blit(pelota, (caja.right - 38, caja.y + 18))

        # los personajes: Mew al centro, los rivales a los lados (dando saltitos)
        personajes = [("rivals/rival_historia.png", 190, 0.0),
                      ("player/player_walk_down_0.png", ANCHO // 2, 1.2),
                      ("rivals/rival_tecnica.png", ANCHO - 190, 2.4)]
        for ruta, x, fase in personajes:
            salto = int(10 * abs(math.sin(self.tiempo * 3 + fase)))
            sprite = assets.get_image(ruta, size=(130, 130))
            dibujar_sombra(pantalla, (x, 402), 80, 16)
            pantalla.blit(sprite, sprite.get_rect(midbottom=(x, 405 - salto)))

        # "presiona espacio" parpadeando + controles
        if int(self.tiempo * 2) % 2 == 0:
            ayuda = self.fuente_sub.render("Presiona ESPACIO para empezar", True, BLANCO)
            pantalla.blit(ayuda, ayuda.get_rect(center=(ANCHO // 2, 460)))
        controles = self.fuente_ayuda.render(
            "Muévete: flechas / WASD  |  Responder: 1-4  |  M: sonido", True, (190, 200, 230))
        caja_controles = pygame.Rect(0, 0, controles.get_width() + 40, 44)
        caja_controles.midbottom = (ANCHO // 2, ALTO - 20)
        dibujar_marco(pantalla, caja_controles)
        pantalla.blit(controles, controles.get_rect(center=caja_controles.center))
