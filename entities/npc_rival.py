"""
npc_rival.py
------------
Un rival plantado en el mapa. Cada rival tiene un 'tema' (historia,
reglamentacion, indumentaria, tecnica, arbitraje) que define de qué
banco de preguntas saldrán sus preguntas al enfrentarlo.
"""

import math
import pygame
from config import TILE_SIZE, SPRITE_MAPA, VERDE_OK
from core.asset_manager import assets


def _version_apagada(sprite):
    """Copia del sprite en gris y oscurecida (respeta la transparencia del png)."""
    gris = pygame.transform.grayscale(sprite)
    gris.fill((110, 110, 110, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return gris


class NpcRival:
    def __init__(self, col, fila, tema, id_unico):
        self.col = col
        self.fila = fila
        self.tema = tema
        self.id = id_unico  # para saber si ya fue vencido (datos_globales["rivales_vencidos"])
        self.rect = pygame.Rect(col * TILE_SIZE, fila * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self._sprite_apagado = None  # se genera una sola vez, la primera vez que se necesita

    def dibujar(self, pantalla, vencido=False, tiempo=0.0):
        sprite = assets.get_image(f"rivals/rival_{self.tema}.png", size=(SPRITE_MAPA, SPRITE_MAPA))
        destino = sprite.get_rect(midbottom=self.rect.midbottom)  # pies sobre su casilla
        if not vencido:
            # "respira": se estira y encoge un poquito (cada rival a su propio ritmo)
            estirar = 1 + 0.05 * math.sin(tiempo * 3 + self.col + self.fila)
            vivo = pygame.transform.smoothscale(sprite, (SPRITE_MAPA, int(SPRITE_MAPA * estirar)))
            pantalla.blit(vivo, vivo.get_rect(midbottom=self.rect.midbottom))
            return

        # vencido: en gris oscuro + palomita verde, para que se note bien
        if self._sprite_apagado is None:
            self._sprite_apagado = _version_apagada(sprite)
        pantalla.blit(self._sprite_apagado, destino)

        x, y, t = destino.x, destino.y, SPRITE_MAPA
        puntos = [(x + t * 0.25, y + t * 0.5), (x + t * 0.42, y + t * 0.7), (x + t * 0.78, y + t * 0.28)]
        pygame.draw.lines(pantalla, (0, 0, 0), False, puntos, 6)  # borde negro
        pygame.draw.lines(pantalla, VERDE_OK, False, puntos, 3)
