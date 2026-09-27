"""
ball.py
-------
La pelota del duelo. Se mueve siguiendo una lista de "tramos": cada tramo va
de un punto a otro en cierto tiempo, haciendo un arco (como si subiera y
bajara). Así se arma cualquier jugada, por ejemplo:
    golpe del rival -> bota en tu lado -> llega a tu raqueta

Se dibuja con una sombra en el piso/mesa para que se note la altura.
Es solo estética, no afecta la lógica de puntaje.
"""

import pygame
from core.asset_manager import assets

TAMANO = 20  # pixeles


class Tramo:
    def __init__(self, desde, hasta, duracion, altura_arco):
        self.desde = desde            # (x, y) en la mesa / piso
        self.hasta = hasta
        self.duracion = duracion      # segundos
        self.altura_arco = altura_arco  # qué tanto sube la pelota a mitad del tramo


class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.altura = 0.0  # altura sobre la mesa (solo visual)
        self._tramos = []
        self._t = 0.0
        self.terminado = True
        self.visible = True

    def lanzar(self, tramos):
        """Empieza una jugada nueva. tramos: lista de Tramo, en orden."""
        self._tramos = list(tramos)
        self._t = 0.0
        self.terminado = not self._tramos
        self.visible = True
        if self._tramos:
            self.x, self.y = self._tramos[0].desde
            self.altura = 0.0

    def actualizar(self, dt):
        if self.terminado:
            return
        self._t += dt
        # si se pasó del tramo actual, salta al siguiente (conservando el tiempo sobrante)
        while self._tramos and self._t >= self._tramos[0].duracion:
            self._t -= self._tramos[0].duracion
            self.x, self.y = self._tramos.pop(0).hasta
            self.altura = 0.0
        if not self._tramos:
            self.terminado = True
            return

        tramo = self._tramos[0]
        p = self._t / tramo.duracion  # progreso 0..1 en este tramo
        (x0, y0), (x1, y1) = tramo.desde, tramo.hasta
        self.x = x0 + (x1 - x0) * p
        self.y = y0 + (y1 - y0) * p
        self.altura = tramo.altura_arco * 4 * p * (1 - p)  # parábola: 0 -> máx -> 0

    def dibujar(self, pantalla):
        if not self.visible:
            return
        # sombra: se achica un poco mientras más alta va la pelota
        ancho_sombra = max(6, TAMANO - int(self.altura * 0.15))
        sombra = pygame.Rect(0, 0, ancho_sombra, ancho_sombra // 2)
        sombra.center = (int(self.x), int(self.y) + TAMANO // 2)
        pygame.draw.ellipse(pantalla, (0, 0, 0), sombra)

        centro = (int(self.x), int(self.y - self.altura))
        if assets.existe("ui/ball.png"):
            sprite = assets.get_image("ui/ball.png", size=(TAMANO, TAMANO))
            pantalla.blit(sprite, (centro[0] - TAMANO // 2, centro[1] - TAMANO // 2))
        else:
            # mientras no haya pixel art, una pelota blanca simple se ve mejor que el placeholder
            pygame.draw.circle(pantalla, (245, 245, 245), centro, TAMANO // 2 - 2)
            pygame.draw.circle(pantalla, (0, 0, 0), centro, TAMANO // 2 - 2, 1)
