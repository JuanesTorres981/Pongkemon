"""
overworld_state.py
-------------------
El mapa que se camina, estilo Pokémon. Se carga desde data/map.csv:
    . = pasto/piso (transitable)
    # = pared (no transitable)
    1..5 = rival según config.TEMAS[0..4] (no transitable, choca = batalla)
    P = posición inicial del jugador (se trata como piso)
    T, c, S, M, f, v = decoración (árbol, cerca, letrero, mini mesa,
                       flores, pasto alto; ver entities/decoracion.py)

Cada rival tiene su "zona": una cancha de color de 3x3 casillas a su
alrededor (dejen esas casillas libres de paredes al mover rivales).

Editar el mapa es solo editar ese .csv, no hay que tocar este archivo.
"""

import csv
import math
import pygame

from config import (TILE_SIZE, SPRITE_MAPA, BLANCO, AMARILLO, ANCHO, ALTO, MAP_PATH,
                    MAPA_FONDO, TEMAS, TEMAS_NOMBRE_VISIBLE, TEMAS_COLOR)
from core.state import State
from core.asset_manager import assets
from core.audio import audio
from core.ui import dibujar_marco
from core.texto import envolver_texto, dibujar_lineas
from entities.decoracion import (Decoracion, DECORACIONES, LETRAS_TRANSITABLES,
                                 Mariposa, Nube, dibujar_zona)
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
        return valor in (".", "P") or valor in LETRAS_TRANSITABLES

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
        self.fuente_etiqueta = pygame.font.SysFont("consolas", 14, bold=True)
        self.tiempo = 0.0               # para la animación de "respirar" de los rivales
        self.cooldown_choque = 0.0      # para que el sonido de chocar no se repita a lo loco
        self.esperar_soltar = False     # al volver de un duelo, hay que soltar la flecha primero

        # decoración y vida del mapa
        self.decoraciones = [Decoracion(self.mapa.valor_en(c, f), c, f)
                             for f in range(self.mapa.filas) for c in range(self.mapa.columnas)
                             if self.mapa.valor_en(c, f) in DECORACIONES]
        self.area_mapa = pygame.Rect(0, 0, self.mapa.columnas * TILE_SIZE, self.mapa.filas * TILE_SIZE)
        self.mariposas = [Mariposa(c, color) for c, color in [
            ((250, 90), "amarilla"), ((560, 110), "rosa"), ((180, 300), "rosa"), ((520, 420), "amarilla")]]
        self.nubes = [Nube(-100, 20, 1.3, 14), Nube(300, 230, 1.0, 10), Nube(650, 380, 1.5, 12)]

    def al_entrar(self):
        audio.musica("musica_mapa")

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

    TECLAS_DIRECCION = {
        pygame.K_UP: (0, -1), pygame.K_w: (0, -1),
        pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
        pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0),
        pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
    }

    def manejar_evento(self, evento):
        # un toque de tecla: da un paso (mantenerla presionada se maneja en actualizar)
        if evento.type == pygame.KEYDOWN and evento.key in self.TECLAS_DIRECCION:
            self.esperar_soltar = False
            if not self.jugador.moviendo:
                self._intentar_mover(*self.TECLAS_DIRECCION[evento.key])

    def _direccion_presionada(self):
        teclas = pygame.key.get_pressed()
        for tecla, direccion in self.TECLAS_DIRECCION.items():
            if teclas[tecla]:
                return direccion
        return None

    def _intentar_mover(self, dx, dy):
        destino = self.mapa.valor_en(self.jugador.col + dx, self.jugador.fila + dy)
        if destino in ("S", "M"):  # letrero o mesa de práctica: se "leen"
            self.jugador.mirar(dx, dy)
            self._leer_objeto(destino, self.jugador.col + dx, self.jugador.fila + dy)
            return
        rival = self._rival_en(self.jugador.col + dx, self.jugador.fila + dy)
        if rival is not None:
            self.jugador.mirar(dx, dy)
            if self._esta_vencido(rival):
                # ya le ganaste: no se repite el duelo, solo se avisa
                self.mensaje = f"Ya venciste al rival de {TEMAS_NOMBRE_VISIBLE[rival.tema]}."
            else:
                self.mensaje = ""
                self._iniciar_batalla(rival)
        elif self.jugador.mover(dx, dy, self.mapa):
            self.mensaje = ""
        elif self.cooldown_choque <= 0:  # pared: "tuc" como en Pokémon
            audio.efecto("choque")
            self.cooldown_choque = 0.3

    def _leer_objeto(self, letra, col, fila):
        rival = min(self.rivales, key=lambda r: abs(r.col - col) + abs(r.fila - fila))
        tema = TEMAS_NOMBRE_VISIBLE[rival.tema]
        if letra == "S" and self._esta_vencido(rival):
            nuevo = f"Letrero: «Zona de {tema}». ¡Ya dominas este tema!"
        elif letra == "S":
            nuevo = f"Letrero: «Zona de {tema}». ¡Vence a su rival para dominar el tema!"
        else:
            nuevo = f"Una mesa de práctica. Aquí entrena el rival de {tema}."
        if nuevo != self.mensaje:
            audio.efecto("seleccionar")
        self.mensaje = nuevo

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
        self.esperar_soltar = True
        self.game.cambiar_estado(BattleState(self.game, rival, self))

    def actualizar(self, dt):
        self.tiempo += dt
        self.cooldown_choque -= dt
        self.jugador.actualizar(dt)
        for nube in self.nubes:
            nube.actualizar(dt, self.area_mapa.w)

        # caminar manteniendo la tecla presionada
        direccion = self._direccion_presionada()
        if direccion is None:
            self.esperar_soltar = False
        elif not self.esperar_soltar and not self.jugador.moviendo:
            self._intentar_mover(*direccion)

    def dibujar(self, pantalla):
        # 1) el piso: fondo, canchas de los rivales y decoración que se pisa
        self.mapa.dibujar(pantalla)
        for rival in self.rivales:
            dibujar_zona(pantalla, rival, TEMAS_COLOR[rival.tema], self._esta_vencido(rival))
        for deco in self.decoraciones:
            if deco.transitable:
                deco.dibujar(pantalla, self.tiempo)

        # 2) lo que tiene altura, ordenado de arriba a abajo (así Mew puede
        #    quedar detrás de la copa de un árbol o delante de él)
        cosas = [(d.pie_y, lambda d=d: d.dibujar(pantalla, self.tiempo))
                 for d in self.decoraciones if not d.transitable]
        cosas += [(r.rect.bottom, lambda r=r: r.dibujar(pantalla, vencido=self._esta_vencido(r),
                                                         tiempo=self.tiempo)) for r in self.rivales]
        cosas.append((self.jugador.rect.bottom + 0.5, lambda: self.jugador.dibujar(pantalla)))
        for _, dibujar in sorted(cosas, key=lambda cosa: cosa[0]):
            dibujar()

        # 3) lo que va "en el aire": mariposas y sombras de nubes (solo sobre el mapa)
        pantalla.set_clip(self.area_mapa)
        for mariposa in self.mariposas:
            mariposa.dibujar(pantalla, self.tiempo)
        for nube in self.nubes:
            nube.dibujar(pantalla)
        pantalla.set_clip(None)

        for rival in self.rivales:
            if abs(rival.col - self.jugador.col) + abs(rival.fila - self.jugador.fila) <= 2:
                self._dibujar_etiqueta(pantalla, rival)
        self._dibujar_barra_inferior(pantalla)

    def _dibujar_etiqueta(self, pantalla, rival):
        """Cartelito con el tema sobre un rival cercano, y un "!" si aún no lo vences."""
        texto = self.fuente_etiqueta.render(TEMAS_NOMBRE_VISIBLE[rival.tema], True, BLANCO)
        caja = pygame.Rect(0, 0, texto.get_width() + 24, texto.get_height() + 16)
        caja.midbottom = (rival.rect.centerx, rival.rect.bottom - SPRITE_MAPA - 2)
        caja.clamp_ip(pantalla.get_rect())
        dibujar_marco(pantalla, caja)
        pantalla.blit(texto, texto.get_rect(center=caja.center))
        if not self._esta_vencido(rival):
            salto = int(3 * abs(math.sin(self.tiempo * 6)))
            signo = assets.get_image("ui/exclamacion.png", size=(16, 24))
            pantalla.blit(signo, signo.get_rect(midbottom=(caja.right + 4, caja.bottom - salto)))

    def _dibujar_barra_inferior(self, pantalla):
        """Barra de abajo: trofeo con rivales vencidos + mensaje o ayuda."""
        alto_mapa = self.mapa.filas * TILE_SIZE
        caja = pygame.Rect(8, alto_mapa + 6, ANCHO - 16, ALTO - alto_mapa - 12)
        if caja.h < 40:  # el mapa ocupa toda la pantalla: la barra va encima, abajo
            caja = pygame.Rect(8, ALTO - 58, ANCHO - 16, 50)
        dibujar_marco(pantalla, caja)

        trofeo = assets.get_image("ui/trofeo.png", size=(32, 32))
        pantalla.blit(trofeo, trofeo.get_rect(midleft=(caja.x + 16, caja.centery)))
        vencidos = sum(self._esta_vencido(r) for r in self.rivales)
        conteo = self.fuente_mensaje.render(f"{vencidos}/{len(self.rivales)}", True, AMARILLO)
        pantalla.blit(conteo, conteo.get_rect(midleft=(caja.x + 56, caja.centery)))

        x_texto = caja.x + 120
        if self.mensaje:  # puede ocupar 2 líneas
            lineas = envolver_texto(self.mensaje, self.fuente_mensaje, caja.right - 20 - x_texto)
            alto = len(lineas) * self.fuente_mensaje.get_linesize()
            dibujar_lineas(pantalla, lineas, self.fuente_mensaje, BLANCO, x_texto, caja.centery - alto // 2)
        else:
            texto = self.fuente_etiqueta.render(
                "Choca con un rival para retarlo a un duelo   |   M: sonido", True, (170, 180, 210))
            pantalla.blit(texto, texto.get_rect(midleft=(x_texto, caja.centery)))
