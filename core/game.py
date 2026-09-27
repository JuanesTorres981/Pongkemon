"""
game.py
-------
El loop principal del juego. Se encarga de:
- Crear la ventana
- Guardar qué estado está activo (menú, mapa, batalla...)
- Correr el loop: eventos -> actualizar -> dibujar
- Cambiar de un estado a otro (game.cambiar_estado(...))
- Tecla M en cualquier pantalla: silenciar / activar el sonido
"""

import pygame
from config import ANCHO, ALTO, FPS, TITULO, NEGRO
from core.audio import audio


class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)  # buffer chico = efectos sin retraso
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(TITULO)
        self.reloj = pygame.time.Clock()
        self.corriendo = True

        # datos que se comparten entre estados (ej: puntaje total, rivales vencidos)
        self.datos_globales = {}
        self.reiniciar_partida()

        self.estado = None  # se asigna con cambiar_estado() desde main.py

    def reiniciar_partida(self):
        """Borra el progreso (rivales vencidos, aciertos, fallos) para jugar de nuevo."""
        self.datos_globales = {
            "rivales_vencidos": set(),
            "aciertos": 0,
            "fallos": 0,
        }

    def cambiar_estado(self, nuevo_estado):
        """nuevo_estado: una instancia de una clase que hereda de State."""
        self.estado = nuevo_estado
        self.estado.al_entrar()

    def correr(self):
        while self.corriendo:
            dt = self.reloj.tick(FPS) / 1000.0  # delta time en segundos

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.corriendo = False
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_m:
                    audio.alternar_silencio()
                else:
                    self.estado.manejar_evento(evento)

            self.estado.actualizar(dt)

            self.pantalla.fill(NEGRO)
            self.estado.dibujar(self.pantalla)
            pygame.display.flip()

        pygame.quit()
