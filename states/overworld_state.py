"""
overworld_state.py
-------------------
El mapa que se camina, estilo Pokémon. Se carga desde data/map.csv:
    . = pasto/piso (transitable)
    # = pared (no transitable)
    1..5 = rival según config.TEMAS[0..4] (no transitable, choca = batalla)
    P = posición inicial del jugador (se trata como piso)

Editar el mapa es solo editar ese .csv, no hay que tocar este archivo.
"""

import csv
import pygame

from config import (TILE_SIZE, VERDE_PASTO, BLANCO, NEGRO, ANCHO, ALTO, MAP_PATH,
                    MAPA_FONDO, TEMAS, TEMAS_NOMBRE_VISIBLE)
from core.state import State
from core.asset_manager import assets
from entities.player import Player
from entities.npc_rival import NpcRival


class Mapa:
    def __init__(self, ruta_csv):
        self.celdas = []
        with open(ruta_csv, "r", encoding="utf-8") as f:
            lector = csv.reader(f)
            for fila in lector:
                self.celdas.append([c.strip() for c in fila])

        self.filas = len(self.celdas)
        self.columnas = len(self.celdas[0]) if self.filas else 0

    def valor_en(self, col, fila):
        if 0 <= fila < self.filas and 0 <= col < self.columnas:
            return self.celdas[fila][col]
        return "#"  # fuera del mapa = pared

    def es_transitable(self, col, fila):
        valor = self.valor_en(col, fila)
        return valor in (".", "P")

    def dibujar(self, pantalla):
        # si hay una imagen de fondo para todo el mapa, se usa esa (las paredes
        # ya vienen dibujadas en la imagen; el .csv solo dice por dónde se camina)
        if assets.existe(MAPA_FONDO):
            tamano = (self.columnas * TILE_SIZE, self.filas * TILE_SIZE)
            pantalla.blit(assets.get_image(MAPA_FONDO, size=tamano), (0, 0))
            return

        for fila in range(self.filas):
            for col in range(self.columnas):
                valor = self.celdas[fila][col]
                destino = (col * TILE_SIZE, fila * TILE_SIZE)
                if valor == "#":
                    sprite = assets.get_image("tiles/tile_pared.png", size=(TILE_SIZE, TILE_SIZE))
                    pantalla.blit(sprite, destino)
                else:
                    sprite = assets.get_image("tiles/tile_pasto.png", size=(TILE_SIZE, TILE_SIZE))
                    pantalla.blit(sprite, destino)


class OverworldState(State):
    def __init__(self, game):
        super().__init__(game)
        self.mapa = Mapa(MAP_PATH)
        self.rivales = self._crear_rivales_desde_mapa()
        self.jugador = self._crear_jugador_desde_mapa()
        self.mensaje = ""  # se muestra abajo, ej "Ya venciste al rival de Historia."
        self.fuente_mensaje = pygame.font.SysFont("consolas", 18)

    def _crear_jugador_desde_mapa(self):
        for fila in range(self.mapa.filas):
            for col in range(self.mapa.columnas):
                if self.mapa.valor_en(col, fila) == "P":
                    return Player(col, fila)
        return Player(1, 1)  # posición por defecto si no hay 'P' en el mapa

    def _crear_rivales_desde_mapa(self):
        rivales = []
        mapa_digito_a_tema = {str(i + 1): tema for i, tema in enumerate(TEMAS)}
        for fila in range(self.mapa.filas):
            for col in range(self.mapa.columnas):
                valor = self.mapa.valor_en(col, fila)
                if valor in mapa_digito_a_tema:
                    tema = mapa_digito_a_tema[valor]
                    rivales.append(NpcRival(col, fila, tema, id_unico=f"rival_{tema}"))
        return rivales

    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return

        dx, dy = 0, 0
        if evento.key in (pygame.K_UP, pygame.K_w):
            dy = -1
        elif evento.key in (pygame.K_DOWN, pygame.K_s):
            dy = 1
        elif evento.key in (pygame.K_LEFT, pygame.K_a):
            dx = -1
        elif evento.key in (pygame.K_RIGHT, pygame.K_d):
            dx = 1

        if dx or dy:
            rival = self._rival_en(self.jugador.col + dx, self.jugador.fila + dy)
            if rival is not None:
                self.jugador.direccion = {(-1, 0): "left", (1, 0): "right",
                                           (0, -1): "up", (0, 1): "down"}[(dx, dy)]
                if self._esta_vencido(rival):
                    # ya le ganaste: no se repite el duelo, solo se avisa
                    self.mensaje = f"Ya venciste al rival de {TEMAS_NOMBRE_VISIBLE[rival.tema]}."
                else:
                    self.mensaje = ""
                    self._iniciar_batalla(rival)
            else:
                self.mensaje = ""
                self.jugador.mover(dx, dy, self.mapa)

    def _esta_vencido(self, rival):
        return rival.id in self.game.datos_globales["rivales_vencidos"]

    def _rival_en(self, col, fila):
        for rival in self.rivales:
            if rival.col == col and rival.fila == fila:
                return rival
        return None

    def _iniciar_batalla(self, rival):
        # import local para evitar import circular entre estados
        from states.battle_state import BattleState
        self.game.cambiar_estado(BattleState(self.game, rival, self))

    def actualizar(self, dt):
        pass

    def dibujar(self, pantalla):
        self.mapa.dibujar(pantalla)
        for rival in self.rivales:
            rival.dibujar(pantalla, vencido=self._esta_vencido(rival))
        self.jugador.dibujar(pantalla)

        if self.mensaje:
            caja = pygame.Rect(20, ALTO - 70, ANCHO - 40, 50)
            pygame.draw.rect(pantalla, NEGRO, caja)
            pygame.draw.rect(pantalla, BLANCO, caja, 2)
            texto = self.fuente_mensaje.render(self.mensaje, True, BLANCO)
            pantalla.blit(texto, (caja.x + 15, caja.centery - texto.get_height() // 2))
