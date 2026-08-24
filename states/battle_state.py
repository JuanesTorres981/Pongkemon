"""
battle_state.py
----------------
La pantalla de duelo: el rival "lanza" una pelota junto a una pregunta
de su tema. El jugador responde con las teclas 1-4.
- Correcta -> punto para el jugador
- Incorrecta -> punto para la máquina (el rival)

Usa MatchManager para llevar el marcador con las reglas reales
(11 puntos, diferencia de 2) y QuestionBank para traer las preguntas.
"""

import pygame

from config import ANCHO, ALTO, TILE_SIZE, BLANCO, NEGRO, VERDE_OK, ROJO, AMARILLO, TEMAS_NOMBRE_VISIBLE
from core.state import State
from core.asset_manager import assets
from entities.ball import Ball
from battle.match_manager import MatchManager
from battle.question_bank import QuestionBank

# se carga una sola vez y se reutiliza (las preguntas no cambian en tiempo real)
_banco_preguntas = None


def _obtener_banco():
    global _banco_preguntas
    if _banco_preguntas is None:
        _banco_preguntas = QuestionBank()
    return _banco_preguntas


class BattleState(State):
    FASE_LANZANDO = "lanzando"
    FASE_ESPERANDO_RESPUESTA = "esperando_respuesta"
    FASE_FEEDBACK = "feedback"
    FASE_FIN_DUELO = "fin_duelo"

    def __init__(self, game, rival, estado_anterior):
        super().__init__(game)
        self.rival = rival
        self.estado_anterior = estado_anterior  # para volver al mapa al terminar

        self.match = MatchManager()
        self.banco = _obtener_banco()
        self.preguntas_usadas = set()

        self.pregunta_actual = None
        self.indice_pregunta_actual = None
        self.fuente_pregunta = pygame.font.SysFont("consolas", 18)
        self.fuente_opciones = pygame.font.SysFont("consolas", 16)
        self.fuente_marcador = pygame.font.SysFont("consolas", 24, bold=True)

        self.fase = None
        # pelota del "saque": siempre va del rival (arriba) hacia el jugador (abajo/centro)
        self.pelota = Ball(x_inicio=120, x_final=ANCHO - 120, y=ALTO // 2 - 40)
        # pelota del "resultado": se crea recién al responder, dirección según acierto/fallo
        self.pelota_resultado = None
        self.mensaje_feedback = ""
        self.color_feedback = BLANCO
        self.tiempo_feedback = 0.0

        self._nueva_pregunta()

    # ---------- flujo del duelo ----------

    def _nueva_pregunta(self):
        indice, pregunta = self.banco.obtener_pregunta_aleatoria(self.rival.tema, self.preguntas_usadas)
        self.indice_pregunta_actual = indice
        self.pregunta_actual = pregunta
        if indice is not None:
            self.preguntas_usadas.add(indice)

        self.pelota.reiniciar()
        self.fase = self.FASE_LANZANDO

    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return

        if self.fase == self.FASE_ESPERANDO_RESPUESTA:
            teclas_opciones = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3}
            if evento.key in teclas_opciones:
                self._responder(teclas_opciones[evento.key])

        elif self.fase == self.FASE_FIN_DUELO:
            if evento.key == pygame.K_SPACE:
                self._terminar_batalla()

    def _responder(self, indice_elegido):
        if self.pregunta_actual is None:
            return
        correcta = self.pregunta_actual["correcta"]

        if indice_elegido == correcta:
            self.match.punto_para_jugador()
            self.mensaje_feedback = "¡Correcto! Punto para ti."
            self.color_feedback = VERDE_OK
            # acertaste -> la pelota "regresa" hacia el rival (mismo eje que el saque, invertido)
            self.pelota_resultado = Ball(
                x_inicio=self.pelota.x_final, x_final=self.pelota.x_inicio,
                y=self.pelota.y, cae_a_mitad=False,
            )
        else:
            self.match.punto_para_rival()
            texto_correcta = self.pregunta_actual["opciones"][correcta]
            self.mensaje_feedback = f"Incorrecto. Era: {texto_correcta}"
            self.color_feedback = ROJO
            # fallaste -> la pelota se va a la red, no cruza al otro lado
            self.pelota_resultado = Ball(
                x_inicio=self.pelota.x_final, x_final=self.pelota.x_inicio,
                y=self.pelota.y, cae_a_mitad=True,
            )

        self.tiempo_feedback = 1.6
        self.fase = self.FASE_FEEDBACK

    def _terminar_batalla(self):
        if self.match.gano_jugador():
            self.game.datos_globales["rivales_vencidos"].add(self.rival.id)
        self.game.cambiar_estado(self.estado_anterior)

    # ---------- loop ----------

    def actualizar(self, dt):
        if self.fase == self.FASE_LANZANDO:
            self.pelota.actualizar(dt)
            if self.pelota.terminado:
                self.fase = self.FASE_ESPERANDO_RESPUESTA

        elif self.fase == self.FASE_FEEDBACK:
            if self.pelota_resultado is not None:
                self.pelota_resultado.actualizar(dt)
            self.tiempo_feedback -= dt
            if self.tiempo_feedback <= 0:
                if self.match.duelo_terminado():
                    self.fase = self.FASE_FIN_DUELO
                else:
                    self._nueva_pregunta()

    def dibujar(self, pantalla):
        pantalla.fill((20, 60, 30))  

        mesa = assets.get_image("tiles/tile_mesa.png", size=(ANCHO - 200, 120))
        pantalla.blit(mesa, (100, ALTO // 2 - 60))

        sprite_rival = assets.get_image(f"rivals/rival_{self.rival.tema}.png", size=(64, 64))
        pantalla.blit(sprite_rival, (ANCHO // 2 - 32, 40))

        tema_visible = TEMAS_NOMBRE_VISIBLE[self.rival.tema]
        titulo = self.fuente_marcador.render(f"Duelo: {tema_visible}", True, AMARILLO)
        pantalla.blit(titulo, (20, 15))

        marcador = self.fuente_marcador.render(
            f"Tú {self.match.marcador_texto()} Rival", True, BLANCO
        )
        pantalla.blit(marcador, (ANCHO // 2 - marcador.get_width() // 2, ALTO - 40))

        if self.fase == self.FASE_LANZANDO:
            self.pelota.dibujar(pantalla)

        elif self.fase in (self.FASE_ESPERANDO_RESPUESTA, self.FASE_FEEDBACK):
            self._dibujar_pregunta(pantalla)

        if self.fase == self.FASE_FEEDBACK:
            if self.pelota_resultado is not None:
                self.pelota_resultado.dibujar(pantalla)
            texto = self.fuente_opciones.render(self.mensaje_feedback, True, self.color_feedback)
            pantalla.blit(texto, (ANCHO // 2 - texto.get_width() // 2, 300))

        if self.fase == self.FASE_FIN_DUELO:
            self._dibujar_fin_duelo(pantalla)

    def _dibujar_pregunta(self, pantalla):
        if self.pregunta_actual is None:
            return
        caja = pygame.Rect(40, 190, ANCHO - 80, 190)
        pygame.draw.rect(pantalla, (0, 0, 0, 180), caja)
        pygame.draw.rect(pantalla, BLANCO, caja, 2)

        pregunta_txt = self.fuente_pregunta.render(self.pregunta_actual["pregunta"], True, BLANCO)
        pantalla.blit(pregunta_txt, (caja.x + 15, caja.y + 15))

        for i, opcion in enumerate(self.pregunta_actual["opciones"]):
            linea = self.fuente_opciones.render(f"{i + 1}) {opcion}", True, BLANCO)
            pantalla.blit(linea, (caja.x + 25, caja.y + 55 + i * 30))

    def _dibujar_fin_duelo(self, pantalla):
        gano = self.match.gano_jugador()
        texto = "¡GANASTE EL DUELO!" if gano else "Perdiste este duelo... ¡inténtalo de nuevo!"
        color = VERDE_OK if gano else ROJO
        render = self.fuente_marcador.render(texto, True, color)
        pantalla.blit(render, (ANCHO // 2 - render.get_width() // 2, ALTO // 2))

        ayuda = self.fuente_opciones.render("Presiona ESPACIO para volver al mapa", True, BLANCO)
        pantalla.blit(ayuda, (ANCHO // 2 - ayuda.get_width() // 2, ALTO // 2 + 40))
