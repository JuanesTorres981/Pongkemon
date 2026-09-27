"""
decoracion.py
--------------
Todo lo que le da vida al mapa, sin afectar el juego:

- Decoracion: objetos puestos en data/map.csv con una letra
      T = árbol          (no se atraviesa)
      c = cerca          (no se atraviesa)
      S = letrero        (no se atraviesa; al chocarlo muestra un mensaje)
      M = mini mesa      (no se atraviesa; decoración de la zona de un rival)
      f = flores         (se camina encima, se mecen)
      v = pasto alto     (se camina encima, se mece)
- dibujar_zona: la "cancha" de color debajo de cada rival (3x3 casillas).
- Mariposa: revolotean por el mapa.
- Nube: sombras de nubes que pasan lentamente.

Los dibujos están en assets/sprites/deco/ (se generan con
python tools/generar_pixel_art.py) y se pueden reemplazar por otros.
"""

import math
import random
import pygame

from config import TILE_SIZE
from core.asset_manager import assets
from core.ui import dibujar_sombra

# letra del csv -> (dibujo, se puede caminar encima, tiene 2 cuadros de animación)
DECORACIONES = {
    "T": ("deco/arbol.png", False, False),
    "c": ("deco/cerca.png", False, False),
    "S": ("deco/letrero.png", False, False),
    "M": ("deco/mini_mesa.png", False, False),
    "f": ("deco/flores_{}.png", True, True),
    "v": ("deco/matojo_{}.png", True, True),
}
LETRAS_TRANSITABLES = {letra for letra, (_, transitable, _) in DECORACIONES.items() if transitable}


class Decoracion:
    def __init__(self, letra, col, fila):
        self.letra = letra
        self.col = col
        self.fila = fila
        self.sprite, self.transitable, self.animada = DECORACIONES[letra]
        self.base = (col * TILE_SIZE + TILE_SIZE // 2, (fila + 1) * TILE_SIZE)  # centro de los "pies"

    @property
    def pie_y(self):
        """Para ordenar quién se dibuja delante de quién (más abajo = más adelante)."""
        return self.base[1]

    def dibujar(self, pantalla, tiempo):
        ruta = self.sprite
        if self.animada:  # cada mata se mece a su propio ritmo
            ruta = ruta.format(int(tiempo * 2 + self.col * 0.7 + self.fila * 0.3) % 2)
        imagen = assets.get_image(ruta)
        if self.letra == "T":
            dibujar_sombra(pantalla, (self.base[0], self.base[1] - 6), 30, 10)
        pantalla.blit(imagen, imagen.get_rect(midbottom=self.base))


def dibujar_zona(pantalla, rival, color, vencido):
    """Cancha de 3x3 casillas bajo el rival, del color de su tema.
    Si ya lo venciste, el borde se pone dorado."""
    rect = pygame.Rect((rival.col - 1) * TILE_SIZE, (rival.fila - 1) * TILE_SIZE,
                       3 * TILE_SIZE, 3 * TILE_SIZE)
    cancha = pygame.Surface(rect.size, pygame.SRCALPHA)
    cancha.fill((*color, 120))
    pygame.draw.rect(cancha, (0, 0, 0, 80), cancha.get_rect(), 2)
    borde = (248, 200, 48, 230) if vencido else (255, 255, 255, 190)
    pygame.draw.rect(cancha, borde, cancha.get_rect().inflate(-10, -10), 2)
    pygame.draw.line(cancha, (255, 255, 255, 110), (5, rect.h // 2), (rect.w - 6, rect.h // 2), 1)
    pantalla.blit(cancha, rect)


class Mariposa:
    """Revolotea alrededor de un punto combinando senos (se ve 'al azar' pero es suave)."""

    def __init__(self, centro, color):
        self.cx, self.cy = centro
        self.color = color
        self.fases = [random.uniform(0, 6.28) for _ in range(4)]

    def dibujar(self, pantalla, tiempo):
        a, b, c, d = self.fases
        x = self.cx + 70 * math.sin(tiempo * 0.5 + a) + 20 * math.sin(tiempo * 1.7 + b)
        y = self.cy + 35 * math.sin(tiempo * 0.8 + c) + 10 * math.sin(tiempo * 2.3 + d)
        cuadro = int(tiempo * 9 + a) % 2  # aleteo
        imagen = assets.get_image(f"deco/mariposa_{self.color}_{cuadro}.png")
        pantalla.blit(imagen, imagen.get_rect(center=(int(x), int(y))))


class Nube:
    """Sombra de una nube que cruza el mapa de izquierda a derecha."""

    def __init__(self, x, y, escala, velocidad):
        self.x, self.y = x, y
        self.velocidad = velocidad
        w, h = int(220 * escala), int(110 * escala)
        self.imagen = pygame.Surface((w, h), pygame.SRCALPHA)
        for bx, by, bw, bh in [(0.00, 0.35, 0.55, 0.60), (0.25, 0.05, 0.50, 0.75),
                               (0.50, 0.30, 0.50, 0.65)]:  # tres "bolitas" forman la nube
            pygame.draw.ellipse(self.imagen, (10, 20, 40, 255),
                                (int(bx * w), int(by * h), int(bw * w), int(bh * h)))
        # transparencia pareja (si no, donde se cruzan las bolitas queda más oscuro)
        self.imagen.fill((255, 255, 255, 38), special_flags=pygame.BLEND_RGBA_MULT)

    def actualizar(self, dt, ancho_mapa):
        self.x += self.velocidad * dt
        if self.x > ancho_mapa:
            self.x = -self.imagen.get_width()

    def dibujar(self, pantalla):
        pantalla.blit(self.imagen, (int(self.x), int(self.y)))
