"""
final_state.py
---------------
Pantalla de victoria: aparece cuando el jugador vence a TODOS los rivales
del mapa. Muestra los temas dominados y el resumen de aciertos/fallos.
- ESPACIO -> vuelve al menú y reinicia la partida
- ESC     -> cierra el juego
"""

import math
import pygame

from config import ANCHO, ALTO, BLANCO, AMARILLO, VERDE_OK, GRIS_CLARO, TEMAS, TEMAS_NOMBRE_VISIBLE
from core.state import State
from core.audio import audio
from core.texto import envolver_texto, dibujar_lineas
from core.asset_manager import assets
from core.ui import dibujar_marco


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
        # fondo: el gimnasio del duelo, oscurecido
        if assets.existe("ui/fondo_duelo.png"):
            pantalla.blit(assets.get_image("ui/fondo_duelo.png", size=(ANCHO, ALTO)), (0, 0))
            velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            velo.fill((0, 0, 20, 140))
            pantalla.blit(velo, (0, 0))
        else:
            pantalla.fill((15, 30, 60))
        datos = self.game.datos_globales

        # trofeo grande dando saltitos
        salto = int(8 * abs(math.sin(self.tiempo * 3)))
        trofeo = assets.get_image("ui/trofeo.png", size=(96, 96))
        pantalla.blit(trofeo, trofeo.get_rect(midtop=(ANCHO // 2, 16 - salto + 8)))

        titulo = self.fuente_titulo.render("¡CAMPEÓN DE TENIS DE MESA!", True, AMARILLO)
        pantalla.blit(titulo, titulo.get_rect(midtop=(ANCHO // 2, 125)))

        subtitulo = envolver_texto(
            "Venciste a todos los rivales: del ping pong al tenis de mesa.",
            self.fuente_texto, ANCHO - 120,
        )
        dibujar_lineas(pantalla, subtitulo, self.fuente_texto, BLANCO,
                       60, 172, centrado=True, ancho_centro=ANCHO - 120)

        # temas dominados, en un marco
        caja = pygame.Rect(0, 0, 420, 50 + 28 * len(TEMAS) + 10)
        caja.midtop = (ANCHO // 2, 208)
        dibujar_marco(pantalla, caja)
        cab = self.fuente_sub.render("Temas dominados", True, BLANCO)
        pantalla.blit(cab, cab.get_rect(midtop=(caja.centerx, caja.y + 16)))
        y = caja.y + 50
        mini_trofeo = assets.get_image("ui/trofeo.png", size=(20, 20))
        for tema in TEMAS:
            pantalla.blit(mini_trofeo, (caja.x + 60, y))
            linea = self.fuente_texto.render(TEMAS_NOMBRE_VISIBLE[tema], True, VERDE_OK)
            pantalla.blit(linea, (caja.x + 92, y + 1))
            y += 28

        # resumen de respuestas
        aciertos = datos["aciertos"]
        fallos = datos["fallos"]
        total = aciertos + fallos
        porcentaje = round(100 * aciertos / total) if total else 0
        resumen = self.fuente_sub.render(
            f"Aciertos: {aciertos}   Fallos: {fallos}   Precisión: {porcentaje}%", True, AMARILLO
        )
        caja_resumen = pygame.Rect(0, 0, resumen.get_width() + 48, 46)
        caja_resumen.midtop = (ANCHO // 2, caja.bottom + 12)
        dibujar_marco(pantalla, caja_resumen)
        pantalla.blit(resumen, resumen.get_rect(center=caja_resumen.center))

        # ayuda parpadeando
        if int(self.tiempo * 2) % 2 == 0:
            ayuda = self.fuente_texto.render(
                "ESPACIO: jugar de nuevo   |   ESC: salir", True, GRIS_CLARO
            )
            pantalla.blit(ayuda, ayuda.get_rect(center=(ANCHO // 2, ALTO - 30)))
