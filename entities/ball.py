"""
ball.py
-------
Animación de la pelota. Se usa en dos momentos distintos del duelo:

1. "Saque": el rival lanza la pelota hacia el jugador mientras aparece
   la pregunta (siempre rival -> jugador, esto no cambia).
2. "Resultado": después de responder, una SEGUNDA pelota anima el punto:
   - Si acertaste: la pelota "regresa" del jugador hacia el rival (tú
     devolviste bien el golpe).
   - Si fallaste: la pelota se va a la red y cae a mitad de cancha, no
     llega al otro lado (representa el error).
   Antes este resultado no existía, por eso siempre se veía la pelota
   yendo "para el mismo lado" sin importar quién ganaba el punto.
"""

import pygame
from core.asset_manager import assets


class Ball:
    def __init__(self, x_inicio, x_final, y, cae_a_mitad=False):
        """
        x_inicio, x_final: posiciones X de origen y destino.
        y: altura base donde se dibuja (se le suma un arco).
        cae_a_mitad: si es True, la pelota NO llega hasta x_final, se
            queda a mitad de camino y "cae" (representa un fallo, como
            si pegara en la red).
        """
        self.x_inicio = x_inicio
        self.x_final = x_final
        self.y = y
        self.cae_a_mitad = cae_a_mitad
        self.progreso = 0.0  
        self.velocidad = 1.1  
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
        if self.cae_a_mitad:

            objetivo_x = self.x_inicio + (self.x_final - self.x_inicio) * 0.45
            x = self.x_inicio + (objetivo_x - self.x_inicio) * self.progreso
            arco = 35 * (self.progreso ** 2)
        else:
            x = self.x_inicio + (self.x_final - self.x_inicio) * self.progreso
            arco = -30 * (4 * self.progreso * (1 - self.progreso))

        sprite = assets.get_image("ui/ball.png", size=(20, 20))
        pantalla.blit(sprite, (x - 10, self.y + arco - 10))
