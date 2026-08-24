"""
ball.py
-------
Animación simple: la pelota "viaja" del lado del rival hacia el jugador
mientras aparece la pregunta. Es solo estética, no afecta la lógica de puntaje.
"""

import pygame
from core.asset_manager import assets


class Ball:
    def __init__(self, x_inicio, x_final, y):
        self.x_inicio = x_inicio
        self.x_final = x_final
        self.y = y
        self.progreso = 0.0  # de 0.0 a 1.0
        self.velocidad = 0.6  # unidades de progreso por segundo
        self.terminado = False

    def actualizar(self, dt):
        if self.progreso < 1.0:
            self.progreso = min(1.0, self.progreso + self.velocidad * dt)
        else:
            self.terminado = True

    def reiniciar(self):
        self.progreso = 0.0
        self.terminado = False

    def dibujar(self, pantalla):
        x = self.x_inicio + (self.x_final - self.x_inicio) * self.progreso
        # pequeño arco vertical para que se vea como un "lanzamiento"
        arco = -30 * (4 * self.progreso * (1 - self.progreso))
        sprite = assets.get_image("ui/ball.png", size=(20, 20))
        pantalla.blit(sprite, (x - 10, self.y + arco - 10))
