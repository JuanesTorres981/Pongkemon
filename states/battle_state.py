"""
battle_state.py
----------------
La pantalla de duelo: el rival "lanza" una pelota junto a una pregunta
de su tema. El jugador responde con las teclas 1-4.
- Correcta   -> le devuelves la pelota al rival y es punto para ti
- Incorrecta -> la pelota se te pasa, se sale de la mesa y es punto del rival

Usa MatchManager para llevar el marcador con las reglas reales
(11 puntos, diferencia de 2) y QuestionBank para traer las preguntas.

Fases del duelo (en orden):
    LANZANDO            -> la pelota viaja del rival hacia ti
    ESPERANDO_RESPUESTA -> aparece la pregunta
    RESULTADO           -> animación de la devolución (o del fallo) + mensaje
    FIN_DUELO           -> alguien ganó el juego
"""

import math
import random
import pygame

from config import ANCHO, ALTO, BLANCO, VERDE_OK, ROJO, AMARILLO, TEMAS_NOMBRE_VISIBLE
from core.state import State
from core.asset_manager import assets
from core.audio import audio
from core.texto import envolver_texto, dibujar_lineas
from entities.ball import Ball, Tramo
from battle.match_manager import MatchManager
from battle.question_bank import QuestionBank

# se carga una sola vez y se reutiliza (las preguntas no cambian en tiempo real)
_banco_preguntas = None


def _obtener_banco():
    global _banco_preguntas
    if _banco_preguntas is None:
        _banco_preguntas = QuestionBank()
    return _banco_preguntas


# ---------- geometría de la escena ----------
# La mesa se dibuja vista de lado (con patas) respetando la proporción de
# tile_mesa.png. Si cambian el dibujo de la mesa, ajusten estos dos valores:
PROPORCION_MESA = 432 / 1103  # alto / ancho de la imagen
ALTURA_SUPERFICIE = 0.354     # dónde está la superficie verde (0 = arriba, 1 = abajo de la imagen)

_ancho_mesa = 460
_alto_mesa = int(_ancho_mesa * PROPORCION_MESA)
CENTRO_Y = ALTO // 2  # la pelota bota a esta altura (sobre la superficie verde)
MESA = pygame.Rect((ANCHO - _ancho_mesa) // 2, CENTRO_Y - int(_alto_mesa * ALTURA_SUPERFICIE),
                   _ancho_mesa, _alto_mesa)
PISO_Y = MESA.bottom          # donde terminan las patas (los personajes se paran aquí)
X_RIVAL = MESA.left - 5       # donde le pega el rival (extremo izquierdo)
X_JUGADOR = MESA.right + 5    # donde le pegas tú (extremo derecho)
TAMANO_PERSONAJE = 150
BOTE = 140                    # qué tan lejos de la red bota la pelota

# ---------- jugadas (trayectorias de la pelota) ----------
# el rival te la manda: bota en tu mitad de la mesa y llega a tu raqueta
JUGADA_RIVAL = [
    Tramo((X_RIVAL, CENTRO_Y), (MESA.centerx + BOTE, CENTRO_Y), 0.7, 70, sonido="bote"),
    Tramo((MESA.centerx + BOTE, CENTRO_Y), (X_JUGADOR, CENTRO_Y), 0.35, 35),
]
# acertaste: se la devuelves, bota en la mitad del rival y le llega
JUGADA_DEVOLUCION = [
    Tramo((X_JUGADOR, CENTRO_Y), (MESA.centerx - BOTE, CENTRO_Y), 0.6, 80, sonido="bote"),
    Tramo((MESA.centerx - BOTE, CENTRO_Y), (X_RIVAL, CENTRO_Y), 0.3, 35),
]
# fallaste: no le pegas, la pelota sigue de largo, cae al piso, bota y se va
JUGADA_FALLO = [
    Tramo((X_JUGADOR, CENTRO_Y), (X_JUGADOR + 40, PISO_Y), 0.4, 20, sonido="bote"),
    Tramo((X_JUGADOR + 40, PISO_Y), (ANCHO + 40, PISO_Y), 0.45, 40),
]

MENSAJES_ACIERTO = [
    "¡Correcto! Se la devolviste con todo.",
    "¡Eso! Punto para ti.",
    "¡Qué golpe! El rival ni la vio venir.",
    "¡Bien jugado! Ese punto es tuyo.",
]
MENSAJES_FALLO = [
    "¡Uy! Se te pasó la pelota.",
    "¡Nooo! Le pegaste al aire.",
    "Punto para el rival...",
    "Se te fue la pelota de la mesa.",
]

# cuánto se queda el mensaje en pantalla DESPUÉS de que la pelota termina
PAUSA_ACIERTO = 0.8
PAUSA_FALLO = 2.2  # más larga para alcanzar a leer la respuesta correcta
DURACION_PAF = 0.35  # el "¡PAF!" que sale cuando le pegas

# animación de golpe de los personajes (se lanzan hacia la mesa y giran la raqueta)
DURACION_GOLPE = 0.28
AVANCE_GOLPE = 18         # pixeles que se acercan a la mesa
GIRO_GOLPE = 22           # grados que se inclinan al pegarle
RETRASO_GOLPE_FALLIDO = 0.3  # si fallas, Mew le pega al aire... tarde


class BattleState(State):
    FASE_LANZANDO = "lanzando"
    FASE_ESPERANDO_RESPUESTA = "esperando_respuesta"
    FASE_RESULTADO = "resultado"
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
        self.pelota = Ball(X_RIVAL, CENTRO_Y)
        self.acerto = False
        self.mensaje_feedback = ""
        self.color_feedback = BLANCO
        self.tiempo_resultado = 0.0  # tiempo transcurrido dentro de FASE_RESULTADO
        self.tiempo = 0.0            # para la animación de "respirar"
        # tiempo desde que empezó el golpe de cada uno (None = no está golpeando;
        # negativo = va a golpear dentro de un rato)
        self.golpe_rival = None
        self.golpe_jugador = None

        self._nueva_pregunta()

    def al_entrar(self):
        audio.musica("musica_duelo")

    # ---------- flujo del duelo ----------

    def _nueva_pregunta(self):
        indice, pregunta = self.banco.obtener_pregunta_aleatoria(self.rival.tema, self.preguntas_usadas)
        self.indice_pregunta_actual = indice
        self.pregunta_actual = pregunta
        if indice is not None:
            self.preguntas_usadas.add(indice)

        self.pelota.lanzar(JUGADA_RIVAL)
        self.golpe_rival = 0.0  # el rival le pega (saca)
        audio.efecto("golpe")
        self.fase = self.FASE_LANZANDO

    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return

        if self.fase == self.FASE_ESPERANDO_RESPUESTA:
            teclas_opciones = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3}
            if evento.key in teclas_opciones:
                self._responder(teclas_opciones[evento.key])

        elif self.fase == self.FASE_RESULTADO:
            # ESPACIO / ENTER salta la pausa, pero solo cuando ya terminó la animación
            if evento.key in (pygame.K_SPACE, pygame.K_RETURN) and self.pelota.terminado:
                self._despues_del_resultado()

        elif self.fase == self.FASE_FIN_DUELO:
            if evento.key == pygame.K_SPACE:
                audio.efecto("seleccionar")
                self._terminar_batalla()

    def _responder(self, indice_elegido):
        if self.pregunta_actual is None:
            return
        correcta = self.pregunta_actual["correcta"]
        self.acerto = indice_elegido == correcta

        if self.acerto:
            self.game.datos_globales["aciertos"] += 1
            self.match.punto_para_jugador()
            self.mensaje_feedback = random.choice(MENSAJES_ACIERTO)
            self.color_feedback = VERDE_OK
            self.pelota.lanzar(JUGADA_DEVOLUCION)
            self.golpe_jugador = 0.0
            audio.efecto("golpe")
            audio.efecto("acierto")
        else:
            self.game.datos_globales["fallos"] += 1
            self.match.punto_para_rival()
            texto_correcta = self.pregunta_actual["opciones"][correcta]
            self.mensaje_feedback = f"{random.choice(MENSAJES_FALLO)} La respuesta era: {texto_correcta}"
            self.color_feedback = ROJO
            self.pelota.lanzar(JUGADA_FALLO)
            self.golpe_jugador = -RETRASO_GOLPE_FALLIDO  # le pega al aire cuando ya pasó
            audio.efecto("fallo")

        self.tiempo_resultado = 0.0
        self.fase = self.FASE_RESULTADO

    def _despues_del_resultado(self):
        if self.match.duelo_terminado():
            self.pelota.visible = False
            self.fase = self.FASE_FIN_DUELO
            audio.parar_musica()
            audio.efecto("victoria" if self.match.gano_jugador() else "derrota")
        else:
            self._nueva_pregunta()

    def _terminar_batalla(self):
        if self.match.gano_jugador():
            self.game.datos_globales["rivales_vencidos"].add(self.rival.id)

        # si ya se vencieron todos los rivales del mapa -> pantalla final
        ids_rivales = {r.id for r in self.estado_anterior.rivales}
        if ids_rivales and ids_rivales <= self.game.datos_globales["rivales_vencidos"]:
            from states.final_state import FinalState
            self.game.cambiar_estado(FinalState(self.game))
        else:
            self.game.cambiar_estado(self.estado_anterior)

    # ---------- loop ----------

    def actualizar(self, dt):
        self.tiempo += dt
        self.golpe_rival = self._avanzar_golpe(self.golpe_rival, dt)
        self.golpe_jugador = self._avanzar_golpe(self.golpe_jugador, dt)

        if self.fase == self.FASE_LANZANDO:
            self._sonar(self.pelota.actualizar(dt))
            if self.pelota.terminado:
                self.fase = self.FASE_ESPERANDO_RESPUESTA

        elif self.fase == self.FASE_RESULTADO:
            self._sonar(self.pelota.actualizar(dt))
            self.tiempo_resultado += dt
            if self.pelota.terminado:
                self.pelota.visible = self.acerto  # la que se fue de la mesa ya no se ve
                pausa = PAUSA_ACIERTO if self.acerto else PAUSA_FALLO
                duracion_jugada = sum(t.duracion for t in (JUGADA_DEVOLUCION if self.acerto else JUGADA_FALLO))
                if self.tiempo_resultado >= duracion_jugada + pausa:
                    self._despues_del_resultado()

    @staticmethod
    def _avanzar_golpe(t, dt):
        if t is None:
            return None
        t += dt
        return None if t >= DURACION_GOLPE else t

    @staticmethod
    def _sonar(sonidos):
        for nombre in sonidos:
            audio.efecto(nombre)

    def _dibujar_personaje(self, pantalla, sprite, x, t_golpe, hacia):
        """Dibuja a un personaje parado en el piso. 'hacia' = +1 si la mesa
        está a su derecha, -1 si está a su izquierda.
        - Quieto: "respira" (sube y baja un poquito).
        - Golpeando: se lanza hacia la mesa y se inclina, como un swing."""
        y = PISO_Y - TAMANO_PERSONAJE
        y += int(2 * math.sin(self.tiempo * 4 + hacia))  # respirar
        if t_golpe is not None and t_golpe >= 0:
            fuerza = math.sin(t_golpe / DURACION_GOLPE * math.pi)  # 0 -> 1 -> 0
            x += int(hacia * AVANCE_GOLPE * fuerza)
            centro_pies = (x + TAMANO_PERSONAJE // 2, PISO_Y)
            # rotate: ángulo positivo = antihorario. Inclinarse hacia la derecha = negativo
            sprite = pygame.transform.rotate(sprite, -hacia * GIRO_GOLPE * fuerza)
            pantalla.blit(sprite, sprite.get_rect(midbottom=centro_pies))
            return
        pantalla.blit(sprite, (x, y))

    def dibujar(self, pantalla):
        pantalla.fill((20, 60, 30))  # cancha de fondo (placeholder de color)

        # mesa de ping pong al centro (placeholder si no hay sprite) + la red
        mesa = assets.get_image("tiles/tile_mesa.png", size=MESA.size)
        pantalla.blit(mesa, MESA.topleft)
        if not assets.existe("tiles/tile_mesa.png"):  # el dibujo real ya trae su red
            pygame.draw.line(pantalla, BLANCO, (MESA.centerx, MESA.top - 6), (MESA.centerx, MESA.bottom + 6), 3)

        # rival a la izquierda de la mesa, jugador a la derecha
        sprite_rival = assets.get_image(f"rivals/rival_{self.rival.tema}.png",
                                        size=(TAMANO_PERSONAJE, TAMANO_PERSONAJE))
        self._dibujar_personaje(pantalla, sprite_rival, MESA.left + 10 - TAMANO_PERSONAJE,
                                self.golpe_rival, hacia=+1)
        sprite_jugador = assets.get_image("player/player_walk_left_0.png",
                                          size=(TAMANO_PERSONAJE, TAMANO_PERSONAJE))
        self._dibujar_personaje(pantalla, sprite_jugador, MESA.right - 10,
                                self.golpe_jugador, hacia=-1)

        tema_visible = TEMAS_NOMBRE_VISIBLE[self.rival.tema]
        titulo = self.fuente_marcador.render(f"Duelo: {tema_visible}", True, AMARILLO)
        pantalla.blit(titulo, (20, 15))

        marcador = self.fuente_marcador.render(
            f"Tú {self.match.marcador_texto()} Rival", True, BLANCO
        )
        pantalla.blit(marcador, (ANCHO // 2 - marcador.get_width() // 2, ALTO - 40))

        if self.fase == self.FASE_ESPERANDO_RESPUESTA:
            self._dibujar_pregunta(pantalla)

        elif self.fase == self.FASE_RESULTADO:
            if self.acerto and self.tiempo_resultado < DURACION_PAF:
                paf = self.fuente_marcador.render("¡PAF!", True, AMARILLO)
                pantalla.blit(paf, (MESA.right - paf.get_width() // 2, CENTRO_Y - 80))
            self._dibujar_feedback(pantalla)

        elif self.fase == self.FASE_FIN_DUELO:
            self._dibujar_fin_duelo(pantalla)

        # la pelota va de última para que ninguna caja la tape
        if self.fase in (self.FASE_LANZANDO, self.FASE_RESULTADO):
            self.pelota.dibujar(pantalla)

    def _dibujar_pregunta(self, pantalla):
        """Dibuja la caja con la pregunta y opciones, con salto de línea
        automático. La caja crece según el texto. Devuelve la 'y' donde termina."""
        if self.pregunta_actual is None:
            return 70
        margen = 15
        caja_x, caja_y = 40, 70
        ancho_caja = ANCHO - 80
        ancho_texto = ancho_caja - 2 * margen

        lineas_pregunta = envolver_texto(self.pregunta_actual["pregunta"], self.fuente_pregunta, ancho_texto)

        # cada opción se envuelve por separado; las líneas de continuación
        # quedan alineadas debajo del texto, no debajo del "1)"
        bloques_opciones = []
        for i, opcion in enumerate(self.pregunta_actual["opciones"]):
            prefijo = f"{i + 1}) "
            sangria = self.fuente_opciones.size(prefijo)[0]
            lineas = envolver_texto(opcion, self.fuente_opciones, ancho_texto - 10 - sangria)
            bloques_opciones.append((prefijo, sangria, lineas))

        alto_preg = len(lineas_pregunta) * self.fuente_pregunta.get_linesize()
        alto_opc = sum(len(l) for _, _, l in bloques_opciones) * self.fuente_opciones.get_linesize()
        alto_caja = margen + alto_preg + 12 + alto_opc + 6 * len(bloques_opciones) + margen

        caja = pygame.Rect(caja_x, caja_y, ancho_caja, alto_caja)
        self._dibujar_caja(pantalla, caja)

        y = dibujar_lineas(pantalla, lineas_pregunta, self.fuente_pregunta, BLANCO,
                           caja.x + margen, caja.y + margen)
        y += 12
        for prefijo, sangria, lineas in bloques_opciones:
            x = caja.x + margen + 10
            pantalla.blit(self.fuente_opciones.render(prefijo, True, AMARILLO), (x, y))
            y = dibujar_lineas(pantalla, lineas, self.fuente_opciones, BLANCO, x + sangria, y)
            y += 6
        return caja.bottom

    def _dibujar_feedback(self, pantalla):
        """Mensaje de acierto/fallo debajo de la mesa, sin tapar la animación."""
        margen = 12
        ancho_caja = ANCHO - 80
        lineas = envolver_texto(self.mensaje_feedback, self.fuente_pregunta, ancho_caja - 2 * margen)
        alto = len(lineas) * self.fuente_pregunta.get_linesize() + 2 * margen
        caja = pygame.Rect(40, PISO_Y + 14, ancho_caja, alto)
        self._dibujar_caja(pantalla, caja)
        dibujar_lineas(pantalla, lineas, self.fuente_pregunta, self.color_feedback,
                       caja.x + margen, caja.y + margen, centrado=True, ancho_centro=ancho_caja - 2 * margen)

    @staticmethod
    def _dibujar_caja(pantalla, caja):
        fondo = pygame.Surface(caja.size, pygame.SRCALPHA)
        fondo.fill((0, 0, 0, 235))
        pantalla.blit(fondo, caja.topleft)
        pygame.draw.rect(pantalla, BLANCO, caja, 2)

    def _dibujar_fin_duelo(self, pantalla):
        gano = self.match.gano_jugador()
        texto = "¡GANASTE EL DUELO!" if gano else "Perdiste este duelo... ¡inténtalo de nuevo!"
        color = VERDE_OK if gano else ROJO
        render = self.fuente_marcador.render(texto, True, color)
        ayuda = self.fuente_opciones.render("Presiona ESPACIO para volver al mapa", True, BLANCO)

        caja = pygame.Rect(0, 0, max(render.get_width(), ayuda.get_width()) + 60, 100)
        caja.center = (ANCHO // 2, ALTO // 2)
        self._dibujar_caja(pantalla, caja)
        pantalla.blit(render, (ANCHO // 2 - render.get_width() // 2, caja.y + 20))
        pantalla.blit(ayuda, (ANCHO // 2 - ayuda.get_width() // 2, caja.y + 62))
