"""
player.py
---------
El jugador se mueve casilla por casilla (estilo Pokémon clásico), no libre.
El sprite se pide siempre por nombre al asset_manager, así que cuando
llegue el pixel art real solo hay que poner los .png con esos nombres
en assets/sprites/player/.
"""

import pygame
from config import TILE_SIZE
from core.asset_manager import assets


class Player:
    def __init__(self, col, fila):
        self.col = col
        self.fila = fila
        self.direccion = "down"  # down, up, left, right
        self.rect = pygame.Rect(col * TILE_SIZE, fila * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def mover(self, dx, dy, mapa):
        """dx, dy en casillas (-1, 0, 1). Cambia dirección aunque no se mueva."""
        if dx == -1:
            self.direccion = "left"
        elif dx == 1:
            self.direccion = "right"
        elif dy == -1:
            self.direccion = "up"
        elif dy == 1:
            self.direccion = "down"

        nueva_col = self.col + dx
        nueva_fila = self.fila + dy

        if mapa.es_transitable(nueva_col, nueva_fila):
            self.col = nueva_col
            self.fila = nueva_fila
            self.rect.topleft = (self.col * TILE_SIZE, self.fila * TILE_SIZE)
            return True
        return False

    def casilla_frente(self):
        """Devuelve la casilla a la que está mirando el jugador (para detectar rivales)."""
        dx, dy = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
        }[self.direccion]
        return self.col + dx, self.fila + dy

    def dibujar(self, pantalla):
        sprite = assets.get_image(f"player/player_walk_{self.direccion}_0.png",
                                   size=(TILE_SIZE, TILE_SIZE))
        pantalla.blit(sprite, self.rect)
