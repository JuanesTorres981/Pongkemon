"""
ui.py
-----
Piezas de interfaz que se repiten en varias pantallas.

dibujar_marco(pantalla, rect): caja de texto estilo Pokémon hecha con
assets/sprites/ui/marco.png (12x12). El marco se corta en 9 pedazos:
las 4 esquinas se dibujan tal cual, los bordes se estiran y el centro
rellena, así sirve para cajas de cualquier tamaño.
Si no existe marco.png, dibuja una caja simple (el juego nunca se cae).
"""

import pygame
from core.asset_manager import assets

ESCALA = 2   # cada pixel del marco se ve de 2x2 en pantalla
CORTE = 4    # tamaño (en pixeles del png) de cada esquina

_piezas = None


def _cargar_piezas():
    global _piezas
    marco = assets.get_image("ui/marco.png")
    c = CORTE
    ancho, alto = marco.get_size()
    medio_w, medio_h = ancho - 2 * c, alto - 2 * c

    def pieza(x, y, w, h):
        sub = marco.subsurface((x, y, w, h))
        return pygame.transform.scale(sub, (w * ESCALA, h * ESCALA))

    _piezas = {
        "sup_izq": pieza(0, 0, c, c), "sup_der": pieza(ancho - c, 0, c, c),
        "inf_izq": pieza(0, alto - c, c, c), "inf_der": pieza(ancho - c, alto - c, c, c),
        "sup": marco.subsurface((c, 0, medio_w, c)), "inf": marco.subsurface((c, alto - c, medio_w, c)),
        "izq": marco.subsurface((0, c, c, medio_h)), "der": marco.subsurface((ancho - c, c, c, medio_h)),
        "centro": marco.get_at((ancho // 2, alto // 2)),
    }


def dibujar_marco(pantalla, rect):
    rect = pygame.Rect(rect)
    if not assets.existe("ui/marco.png"):
        pygame.draw.rect(pantalla, (20, 28, 56), rect)
        pygame.draw.rect(pantalla, (240, 240, 240), rect, 2)
        return
    if _piezas is None:
        _cargar_piezas()

    e = CORTE * ESCALA
    interior = rect.inflate(-2 * e, -2 * e)
    pantalla.fill(_piezas["centro"], interior)
    if interior.w > 0:
        pantalla.blit(pygame.transform.scale(_piezas["sup"], (interior.w, e)), (interior.x, rect.y))
        pantalla.blit(pygame.transform.scale(_piezas["inf"], (interior.w, e)), (interior.x, interior.bottom))
    if interior.h > 0:
        pantalla.blit(pygame.transform.scale(_piezas["izq"], (e, interior.h)), (rect.x, interior.y))
        pantalla.blit(pygame.transform.scale(_piezas["der"], (e, interior.h)), (interior.right, interior.y))
    pantalla.blit(_piezas["sup_izq"], rect.topleft)
    pantalla.blit(_piezas["sup_der"], (rect.right - e, rect.y))
    pantalla.blit(_piezas["inf_izq"], (rect.x, rect.bottom - e))
    pantalla.blit(_piezas["inf_der"], (rect.right - e, rect.bottom - e))


def dibujar_sombra(pantalla, centro_pies, ancho, alto=None, opacidad=90):
    """Elipse oscura semitransparente bajo un personaje u objeto."""
    alto = alto or max(4, ancho // 4)
    sombra = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    pygame.draw.ellipse(sombra, (0, 0, 0, opacidad), sombra.get_rect())
    pantalla.blit(sombra, sombra.get_rect(center=centro_pies))
