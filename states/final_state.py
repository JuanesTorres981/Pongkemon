"""
final_state.py
---------------
Pantalla de victoria: aparece cuando el jugador vence a TODOS los rivales
del mapa. Muestra los temas dominados y el resumen de aciertos/fallos.
- ESPACIO -> vuelve al menú y reinicia la partida
- ESC     -> cierra el juego
"""

import pygame

from config import ANCHO, ALTO, BLANCO, AMARILLO, VERDE_OK, GRIS_CLARO, TEMAS, TEMAS_NOMBRE_VISIBLE
from core.state import State
from core.audio import audio
from core.texto import envolver_texto, dibujar_lineas


class FinalState(State):
    def __init__(self, game):
        super().__init__(game)
        self.fuente_titulo = pygame.font.SysFont("consolas", 34, bold=True)
        self.fuente_sub = pygame.font.SysFont("consolas", 20, bold=True)
        self.fuente_texto = pygame.font.SysFont("consolas", 18)
        self.tiempo = 0.0  # para el parpadeo del texto de ayuda
        self.musica_puesta = False

    def al_entrar(self):
        audio.parar_musica()
        audio.efecto("victoria")

    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return
        if evento.key == pygame.K_SPACE:
            audio.efecto("seleccionar")
            from states.menu_state import MenuState
            self.game.reiniciar_partida()
            self.game.cambiar_estado(MenuState(self.game))
        elif evento.key == pygame.K_ESCAPE:
            self.game.corriendo = False

    def actualizar(self, dt):
        self.tiempo += dt
        if not self.musica_puesta and self.tiempo > 2.5:  # después del jingle de victoria
            audio.musica("musica_mapa")
            self.musica_puesta = True

    def dibujar(self, pantalla):
        pantalla.fill((15, 30, 60))
        datos = self.game.datos_globales

        titulo = self.fuente_titulo.render("¡CAMPEÓN DE TENIS DE MESA!", True, AMARILLO)
        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 50))

        subtitulo = envolver_texto(
            "Venciste a todos los rivales: del ping pong al tenis de mesa.",
            self.fuente_texto, ANCHO - 120,
        )
        y = dibujar_lineas(pantalla, subtitulo, self.fuente_texto, BLANCO,
                           60, 105, centrado=True, ancho_centro=ANCHO - 120)

        # temas dominados
        y += 25
        cab = self.fuente_sub.render("Temas dominados:", True, BLANCO)
        pantalla.blit(cab, (ANCHO // 2 - cab.get_width() // 2, y))
        y += 35
        for tema in TEMAS:
            linea = self.fuente_texto.render(f"[OK]  {TEMAS_NOMBRE_VISIBLE[tema]}", True, VERDE_OK)
            pantalla.blit(linea, (ANCHO // 2 - 170, y))
            y += 28

        # resumen de respuestas
        aciertos = datos["aciertos"]
        fallos = datos["fallos"]
        total = aciertos + fallos
        porcentaje = round(100 * aciertos / total) if total else 0
        y += 20
        resumen = self.fuente_sub.render(
            f"Aciertos: {aciertos}   Fallos: {fallos}   Precisión: {porcentaje}%", True, AMARILLO
        )
        pantalla.blit(resumen, (ANCHO // 2 - resumen.get_width() // 2, y))

        # ayuda parpadeando
        if int(self.tiempo * 2) % 2 == 0:
            ayuda = self.fuente_texto.render(
                "ESPACIO: jugar de nuevo   |   ESC: salir", True, GRIS_CLARO
            )
            pantalla.blit(ayuda, (ANCHO // 2 - ayuda.get_width() // 2, ALTO - 60))
