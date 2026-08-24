"""
match_manager.py
-----------------
Controla el puntaje de UN duelo contra un rival, siguiendo la regla real
del tenis de mesa: se gana un juego llegando a PUNTOS_PARA_GANAR (11),
con diferencia mínima de DIFERENCIA_MINIMA (2). Si no se llega a esa
diferencia, se sigue jugando (10-10 -> 11-10 no gana, sigue hasta 12-10, etc).

Estructura pensada para poder crecer a "mejor de 3 / 5 juegos" sin reescribir
todo: por ahora JUEGOS_POR_DUELO = 1 en config.py.
"""

from config import PUNTOS_PARA_GANAR, DIFERENCIA_MINIMA, JUEGOS_POR_DUELO


class MatchManager:
    def __init__(self):
        self.juegos_ganados_jugador = 0
        self.juegos_ganados_rival = 0
        self.puntos_jugador = 0
        self.puntos_rival = 0
        self.juegos_necesarios_para_ganar_duelo = (JUEGOS_POR_DUELO // 2) + 1

    def punto_para_jugador(self):
        self.puntos_jugador += 1
        self._revisar_fin_de_juego()

    def punto_para_rival(self):
        self.puntos_rival += 1
        self._revisar_fin_de_juego()

    def _juego_terminado(self):
        maximo = max(self.puntos_jugador, self.puntos_rival)
        diferencia = abs(self.puntos_jugador - self.puntos_rival)
        return maximo >= PUNTOS_PARA_GANAR and diferencia >= DIFERENCIA_MINIMA

    def _revisar_fin_de_juego(self):
        if not self._juego_terminado():
            return
        if self.puntos_jugador > self.puntos_rival:
            self.juegos_ganados_jugador += 1
        else:
            self.juegos_ganados_rival += 1
        self.puntos_jugador = 0
        self.puntos_rival = 0

    def duelo_terminado(self):
        return (
            self.juegos_ganados_jugador >= self.juegos_necesarios_para_ganar_duelo
            or self.juegos_ganados_rival >= self.juegos_necesarios_para_ganar_duelo
        )

    def gano_jugador(self):
        return self.juegos_ganados_jugador > self.juegos_ganados_rival

    def marcador_texto(self):
        return f"{self.puntos_jugador} - {self.puntos_rival}"
