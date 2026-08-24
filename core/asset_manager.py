"""
asset_manager.py
-----------------
TODA imagen del juego se pide aquí, por nombre. Nadie más en el código
debe escribir pygame.image.load(...) directamente.

Ventaja para el equipo: mientras el pixel art no esté listo, este módulo
genera un placeholder (un rectángulo de color con el nombre escrito) para
que el juego sea jugable YA. El día que suelten el .png real en la carpeta
correcta con el nombre correcto, se usa automáticamente y ya no se dibuja
el placeholder. No hay que tocar nada más del código.

Convención de nombres de archivo (respetar esto al exportar del iPad):
    assets/sprites/player/player_walk_down_0.png
    assets/sprites/player/player_walk_up_0.png
    assets/sprites/player/player_walk_left_0.png
    assets/sprites/player/player_walk_right_0.png
    assets/sprites/rivals/rival_historia.png
    assets/sprites/rivals/rival_reglamentacion.png
    assets/sprites/rivals/rival_indumentaria.png
    assets/sprites/rivals/rival_tecnica.png
    assets/sprites/rivals/rival_arbitraje.png
    assets/sprites/tiles/tile_pasto.png
    assets/sprites/tiles/tile_pared.png
    assets/sprites/tiles/tile_mesa.png
    assets/sprites/ui/ball.png
"""

import os
import hashlib
import pygame

from config import SPRITES_DIR, TILE_SIZE


def _color_desde_nombre(nombre: str):
    """Genera un color estable a partir del nombre, para que cada
    placeholder se vea distinto pero siempre igual entre ejecuciones."""
    h = hashlib.md5(nombre.encode("utf-8")).hexdigest()
    r = int(h[0:2], 16) % 156 + 60
    g = int(h[2:4], 16) % 156 + 60
    b = int(h[4:6], 16) % 156 + 60
    return (r, g, b)


class AssetManager:
    def __init__(self):
        self._cache = {}
        pygame.font.init()
        self._fuente_placeholder = pygame.font.SysFont("consolas", 10)

    def get_image(self, relative_path: str, size=None):
        """
        relative_path: ruta relativa dentro de assets/sprites, ej:
            'rivals/rival_historia.png'
        size: tupla (ancho, alto) opcional para forzar el tamaño.
        """
        key = (relative_path, size)
        if key in self._cache:
            return self._cache[key]

        full_path = os.path.join(SPRITES_DIR, relative_path)
        surface = None

        if os.path.isfile(full_path):
            try:
                surface = pygame.image.load(full_path).convert_alpha()
            except pygame.error:
                surface = None

        if surface is None:
            surface = self._crear_placeholder(relative_path, size)
        elif size is not None:
            surface = pygame.transform.scale(surface, size)

        self._cache[key] = surface
        return surface

    def _crear_placeholder(self, relative_path: str, size):
        ancho, alto = size if size else (TILE_SIZE, TILE_SIZE)
        surface = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        color = _color_desde_nombre(relative_path)
        surface.fill(color)
        pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 1)

        nombre_corto = os.path.basename(relative_path).replace(".png", "")
        etiqueta = self._fuente_placeholder.render(nombre_corto[:10], True, (255, 255, 255))
        surface.blit(etiqueta, (2, alto // 2 - 5))
        return surface


# instancia global única, se importa este objeto desde cualquier parte
assets = AssetManager()
