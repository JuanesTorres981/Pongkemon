"""
config.py
---------
Todas las constantes del juego en un solo lugar.
Si necesitan cambiar el tamaño de pantalla, velocidad, colores, etc,
CAMBIENLO AQUI y no repartido por el código.
"""

import os
import sys

# ---------- RUTAS ----------
# Si corre como .exe (PyInstaller), los assets están en la carpeta temporal sys._MEIPASS
BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
SONIDOS_DIR = os.path.join(ASSETS_DIR, "sonidos")
DATA_DIR = os.path.join(BASE_DIR, "data")

QUESTIONS_PATH = os.path.join(DATA_DIR, "questions.json")
MAP_PATH = os.path.join(DATA_DIR, "map.csv")
# imagen de fondo de todo el mapa (ruta dentro de assets/sprites). Si no existe,
# el mapa se dibuja con tile_pasto / tile_pared casilla por casilla.
MAPA_FONDO = "tiles/fondo_mapa.png"

# ---------- VENTANA ----------
TILE_SIZE = 32          # tamaño de cada casilla del mapa, en pixeles
SPRITE_MAPA = 48        # tamaño de los personajes en el mapa (sobresalen de su casilla, como en Pokémon)
ANCHO = 800
ALTO = 600
FPS = 60
TITULO = "Ping Pong RPG - Del ping pong al tenis de mesa"

# ---------- SONIDO (0.0 a 1.0) ----------
VOLUMEN_MUSICA = 0.45
VOLUMEN_EFECTOS = 0.7

# ---------- COLORES (estilo retro / pixel) ----------
NEGRO = (10, 10, 10)
BLANCO = (245, 245, 245)
GRIS = (60, 60, 60)
GRIS_CLARO = (150, 150, 150)
VERDE_PASTO = (86, 158, 74)
AZUL_MESA = (30, 90, 160)
ROJO = (200, 50, 50)
VERDE_OK = (70, 180, 90)
AMARILLO = (240, 200, 50)

# ---------- JUGADOR ----------
VELOCIDAD_JUGADOR = TILE_SIZE  # se mueve casilla por casilla (estilo Pokémon)

# ---------- REGLAS DEL DUELO ----------
# Un solo juego (game) a 11 puntos, hay que ganar por diferencia de 2.
PUNTOS_PARA_GANAR = 11
DIFERENCIA_MINIMA = 2
JUEGOS_POR_DUELO = 1  # "al mejor de 1" -> si luego quieren mejor de 3/5, solo cambien esto
                       # y ajusten match_manager.py (ya viene preparado para eso)

# ---------- TEMAS (deben coincidir con las claves de data/questions.json) ----------
TEMAS = ["historia", "reglamentacion", "indumentaria", "tecnica", "arbitraje"]

# color de la "cancha" de cada rival en el mapa
TEMAS_COLOR = {
    "historia": (196, 140, 72),
    "reglamentacion": (72, 132, 220),
    "indumentaria": (222, 92, 160),
    "tecnica": (240, 136, 48),
    "arbitraje": (226, 206, 56),
}

TEMAS_NOMBRE_VISIBLE = {
    "historia": "Historia del Tenis de Mesa",
    "reglamentacion": "Reglamentación",
    "indumentaria": "Indumentaria",
    "tecnica": "Fundamentación Técnica",
    "arbitraje": "Arbitraje",
}
