"""
player.py
---------
El jugador se mueve casilla por casilla (estilo Pokémon clásico), pero el
dibujo se desliza suave de una casilla a otra, con un saltito y un
balanceo a cada paso (así parece que camina, aunque haya un solo dibujo
por dirección).

La posición "lógica" (col, fila) cambia apenas empieza el paso: todo lo
demás (paredes, rivales) se calcula con esa. La posición en pixeles es
solo para el dibujo.

El sprite se pide siempre por nombre al asset_manager, así que cuando
llegue el pixel art real solo hay que poner los .png con esos nombres
en assets/sprites/player/.
"""

import math
import pygame
from config import TILE_SIZE, SPRITE_MAPA
from core.asset_manager import assets

DURACION_PASO = 0.16   # segundos que tarda en pasar de una casilla a otra
ALTURA_SALTITO = 4     # pixeles que "sube" a mitad de cada paso
ANGULO_BALANCEO = 7    # grados que se inclina hacia cada lado al caminar


class Player:
    def __init__(self, col, fila):
        self.col = col
        self.fila = fila
        self.direccion = "down"  # down, up, left, right
        self.rect = pygame.Rect(col * TILE_SIZE, fila * TILE_SIZE, TILE_SIZE, TILE_SIZE)

        # animación del paso
        self._desde = self.rect.topleft
        self._progreso = 1.0     # 1.0 = quieto en su casilla
        self._pasos_dados = 0    # para alternar el balanceo izquierda / derecha

    @property
    def moviendo(self):
        return self._progreso < 1.0

    def mirar(self, dx, dy):
        self.direccion = {(-1, 0): "left", (1, 0): "right", (0, -1): "up", (0, 1): "down"}[(dx, dy)]

    def mover(self, dx, dy, mapa):
        """dx, dy en casillas (-1, 0, 1). Cambia dirección aunque no se mueva.
        Devuelve True si empezó a caminar, False si había una pared."""
        self.mirar(dx, dy)
        nueva_col = self.col + dx
        nueva_fila = self.fila + dy

        if mapa.es_transitable(nueva_col, nueva_fila):
            self._desde = self.rect.topleft
            self.col = nueva_col
            self.fila = nueva_fila
            self.rect.topleft = (self.col * TILE_SIZE, self.fila * TILE_SIZE)
            self._progreso = 0.0
            self._pasos_dados += 1
            return True
        return False

    def actualizar(self, dt):
        if self.moviendo:
            self._progreso = min(1.0, self._progreso + dt / DURACION_PASO)

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
                                   size=(SPRITE_MAPA, SPRITE_MAPA))

        # posición intermedia entre la casilla de antes y la nueva
        p = self._progreso
        x = self._desde[0] + (self.rect.x - self._desde[0]) * p
        y = self._desde[1] + (self.rect.y - self._desde[1]) * p

        if self.moviendo:
            y -= math.sin(p * math.pi) * ALTURA_SALTITO  # saltito
            lado = 1 if self._pasos_dados % 2 else -1     # un paso a cada lado
            sprite = pygame.transform.rotate(sprite, lado * ANGULO_BALANCEO * math.sin(p * math.pi))

        pies = (int(x) + TILE_SIZE // 2, int(y) + TILE_SIZE)
        pantalla.blit(sprite, sprite.get_rect(midbottom=pies))  # pies sobre su casilla
