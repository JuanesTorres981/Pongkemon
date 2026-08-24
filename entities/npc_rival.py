"""
npc_rival.py
------------
Un rival plantado en el mapa. Cada rival tiene un 'tema' (historia,
reglamentacion, indumentaria, tecnica, arbitraje) que define de qué
banco de preguntas saldrán sus preguntas al enfrentarlo.
"""

import pygame
from config import TILE_SIZE
from core.asset_manager import assets


class NpcRival:
    def __init__(self, col, fila, tema, id_unico):
        self.col = col
        self.fila = fila
        self.tema = tema
        self.id = id_unico  # para saber si ya fue vencido (datos_globales["rivales_vencidos"])
        self.rect = pygame.Rect(col * TILE_SIZE, fila * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def dibujar(self, pantalla, vencido=False):
        sprite = assets.get_image(f"rivals/rival_{self.tema}.png", size=(TILE_SIZE, TILE_SIZE))
        if vencido:
            sprite = sprite.copy()
            sprite.set_alpha(90)  # se ve "apagado" si ya lo venciste
        pantalla.blit(sprite, self.rect)
