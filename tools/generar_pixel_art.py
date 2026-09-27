"""
generar_pixel_art.py
---------------------
Dibuja con código los detalles de pixel art del juego (pelota, marcos de
las cajas de texto, íconos y fondo del duelo) y los guarda en
assets/sprites/ui/.

Uso (desde la carpeta del proyecto):
    python tools/generar_pixel_art.py

Cada dibujo es una "grilla" de letras: cada letra es un color de la
paleta y '.' es transparente. Para cambiar un dibujo basta con editar
las letras. Si alguien del equipo dibuja su propia versión, puede
reemplazar el .png con el mismo nombre; no hay que tocar código.
"""

import os
import random
import pygame

CARPETA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "assets", "sprites", "ui")

# ---------- dibujos (una letra = un pixel) ----------

PELOTA = {  # 10x10, se dibuja al doble (20x20)
    "paleta": {"o": (110, 45, 10), "O": (255, 140, 40), "W": (255, 232, 196), "d": (214, 98, 22)},
    "pixeles": [
        "...oooo...",
        "..oOOOOo..",
        ".oOWWOOOo.",
        "oOWWOOOOOo",
        "oOWOOOOOdo",
        "oOOOOOOOdo",
        "oOOOOOOddo",
        ".oOOOOddo.",
        "..oddddo..",
        "...oooo...",
    ],
}

MARCO = {  # 12x12, se corta en 9 partes para armar cajas de cualquier tamaño
    "paleta": {"k": (16, 16, 24), "w": (236, 236, 244), "b": (80, 124, 214), "n": (22, 30, 58)},
    "pixeles": [
        "..kkkkkkkk..",
        ".kwwwwwwwwk.",
        "kwwbbbbbbwwk",
        "kwbnnnnnnbwk",
        "kwbnnnnnnbwk",
        "kwbnnnnnnbwk",
        "kwbnnnnnnbwk",
        "kwbnnnnnnbwk",
        "kwbnnnnnnbwk",
        "kwwbbbbbbwwk",
        ".kwwwwwwwwk.",
        "..kkkkkkkk..",
    ],
}

TROFEO = {  # 16x16
    "paleta": {"k": (70, 44, 12), "Y": (248, 200, 48), "W": (255, 248, 204),
               "d": (204, 140, 24), "B": (124, 76, 42)},
    "pixeles": [
        "...kkkkkkkkkk...",
        ".kkYWYYYYYYdYkk.",
        "kYkYWYYYYYYdYkYk",
        "kYkYWYYYYYYdYkYk",
        ".kkYWYYYYYYdYkk.",
        "...kYYYYYYYdk...",
        "....kYYYYYdk....",
        ".....kYYYdk.....",
        "......kYdk......",
        "......kYdk......",
        ".....kYYYdk.....",
        "....kkkkkkkk....",
        "....kBBBBBBk....",
        "....kBBBBBBk....",
        "...kkkkkkkkkk...",
        "................",
    ],
}

EXCLAMACION = {  # 8x12, el "!" que sale sobre un rival al acercarte
    "paleta": {"k": (16, 16, 24), "w": (250, 250, 250), "r": (222, 40, 40)},
    "pixeles": [
        ".kkkkkk.",
        "kwwwwwwk",
        "kwwrrwwk",
        "kwwrrwwk",
        "kwwrrwwk",
        "kwwrrwwk",
        "kwwwwwwk",
        "kwwrrwwk",
        "kwwwwwwk",
        ".kkkkkk.",
        "...kk...",
        "...k....",
    ],
}


# ---------- decoración del mapa (se dibujan al doble: 16x16 -> 32x32) ----------

ARBOL = {  # 16x24: la copa sobresale hacia la casilla de arriba
    "paleta": {"k": (26, 52, 30), "G": (58, 140, 60), "g": (40, 104, 48), "L": (104, 184, 80),
               "t": (122, 78, 44), "T": (86, 54, 30)},
    "pixeles": [
        "....kkkkkkkk....",
        "..kkLLLGGGGGkk..",
        ".kLLLGGGGGGGGgk.",
        ".kLLGGGGGGGGGgk.",
        "kLLGGGGGGGGGGggk",
        "kLGGGGGGGGGGGggk",
        "kGGGGGGLGGGGGggk",
        "kGGGGGLLGGGGgggk",
        "kGGGGGGGGGGGgggk",
        "kgGGGGGGGGGGgggk",
        ".kgGGGGGGGGgggk.",
        ".kggGGGGGGggggk.",
        "..kgggggggggggk.",
        "...kkggggggkkk..",
        ".....kkttkkk....",
        "......kttTk.....",
        "......kttTk.....",
        "......kttTk.....",
        "......kttTk.....",
        ".....kkttTkk....",
        "....kttttTTTk...",
        "....kkkkkkkkk...",
        "................",
        "................",
    ],
}

FLORES = {  # 16x16, animada: las cabecitas se mecen
    "paleta": {"r": (232, 64, 72), "w": (248, 248, 248), "y": (250, 214, 60), "o": (244, 150, 40),
               "s": (48, 116, 44)},
    "pixeles": [
        "................",
        "................",
        "..r.........w...",
        ".ror.......wow..",
        "..r.........w...",
        "..s.....y...s...",
        "..s....yoy..s...",
        "..ss....y..ss...",
        "...s....s..s....",
        "...s....s.s.....",
        "........ss......",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
}

MATOJO = {  # 16x16, pasto alto que se mece
    "paleta": {"l": (150, 210, 80), "d": (64, 128, 48)},
    "pixeles": [
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "...l.......l....",
        "..ld...l..ld....",
        "..ld..ld..ld..l.",
        ".lddl.ld.lddl.ld",
        ".lddl.lddlddl.ld",
        "................",
        "................",
        "................",
    ],
}

CERCA = {  # 16x16, se une con la de al lado
    "paleta": {"k": (72, 42, 20), "w": (196, 140, 84), "W": (230, 184, 124)},
    "pixeles": [
        "................",
        "................",
        "................",
        "................",
        ".kk..........kk.",
        "kWWk........kWWk",
        "kwwkkkkkkkkkkwwk",
        "kwwWWWWWWWWWWwwk",
        "kwwwwwwwwwwwwwwk",
        "kwwkkkkkkkkkkwwk",
        "kwwk........kwwk",
        "kwwkkkkkkkkkkwwk",
        "kwwWWWWWWWWWWwwk",
        "kwwwwwwwwwwwwwwk",
        "kwwkkkkkkkkkkwwk",
        ".kk..........kk.",
    ],
}

LETRERO = {  # 16x16
    "paleta": {"k": (60, 36, 16), "b": (206, 156, 96), "B": (158, 108, 60), "l": (104, 66, 32)},
    "pixeles": [
        "................",
        ".kkkkkkkkkkkkkk.",
        "kbbbbbbbbbbbbbbk",
        "kbllllllllllllbk",
        "kbbbbbbbbbbbbbbk",
        "kbllllllllbbbbbk",
        "kbbbbbbbbbbbbbbk",
        "kBBBBBBBBBBBBBBk",
        ".kkkkkkkkkkkkkk.",
        "......kBBk......",
        "......kBBk......",
        "......kBBk......",
        "......kBBk......",
        ".....kkBBkk.....",
        "................",
        "................",
    ],
}

MINI_MESA = {  # 16x16, mesa de ping pong vista desde arriba
    "paleta": {"k": (20, 30, 24), "g": (46, 150, 70), "w": (240, 240, 240), "n": (150, 150, 160),
               "b": (100, 64, 36)},
    "pixeles": [
        "................",
        "................",
        ".kkkkkkkkkkkkkk.",
        "kwwwwwwwnwwwwwwk",
        "kwggggggnggggggk",
        "kwggggggnggggggk",
        "kwwwwwwwnwwwwwwk",
        "kwggggggnggggggk",
        "kwggggggnggggggk",
        "kwwwwwwwnwwwwwwk",
        ".kkkkkkkkkkkkkk.",
        ".bb..........bb.",
        ".bb..........bb.",
        "................",
        "................",
        "................",
    ],
}

MARIPOSA_ABIERTA = ["aa...aa", "aaa.aaa", ".aakaa.", "aa.k.aa", "a.....a"]
MARIPOSA_CERRADA = [".......", "..a.a..", "..aka..", "..aka..", "...k..."]
COLORES_MARIPOSA = {"rosa": (250, 160, 206), "amarilla": (252, 222, 90)}


def desplazar(dibujo, filas, dx):
    """Copia del dibujo con esas filas corridas dx pixeles (para el 2º cuadro de animación)."""
    pix = list(dibujo["pixeles"])
    for f in filas:
        pix[f] = ("." * dx + pix[f])[:len(pix[f])]
    return {"paleta": dibujo["paleta"], "pixeles": pix}


def al_doble(s):
    return pygame.transform.scale(s, (s.get_width() * 2, s.get_height() * 2))


def desde_grilla(dibujo):
    filas = dibujo["pixeles"]
    ancho = len(filas[0])
    assert all(len(f) == ancho for f in filas), "todas las filas deben tener el mismo largo"
    s = pygame.Surface((ancho, len(filas)), pygame.SRCALPHA)
    for y, fila in enumerate(filas):
        for x, letra in enumerate(fila):
            if letra != ".":
                s.set_at((x, y), dibujo["paleta"][letra])
    return s


def fondo_duelo():
    """Gimnasio visto de frente, 200x150 (el juego lo agranda x4 sin suavizar,
    así se ve pixelado). Pared con banderines arriba y piso de madera abajo.
    El piso empieza en y=85 (340 px en pantalla)."""
    random.seed(3)
    s = pygame.Surface((200, 150))
    # pared
    s.fill((44, 62, 94), (0, 0, 200, 85))
    s.fill((36, 51, 78), (0, 58, 200, 24))       # franja baja más oscura
    for x in range(0, 200, 25):                   # paneles de la pared
        pygame.draw.line(s, (38, 54, 82), (x, 0), (x, 57))
    s.fill((22, 28, 42), (0, 82, 200, 3))         # zócalo
    # cuerda de banderines (un poquito caída en el centro)
    colores = [(222, 60, 60), (248, 200, 48), (80, 140, 230), (240, 240, 240)]
    for i, x in enumerate(range(0, 200, 10)):
        caida = int(6 * (1 - ((x + 5 - 100) / 100) ** 2))
        y = 8 + caida
        pygame.draw.polygon(s, colores[i % 4], [(x + 1, y), (x + 9, y), (x + 5, y + 7)])
    for x in range(200):
        caida = int(6 * (1 - ((x - 100) / 100) ** 2))
        s.set_at((x, 8 + caida), (20, 20, 28))
    # piso de madera: tablas horizontales con uniones
    for i, y in enumerate(range(85, 150, 6)):
        base = (152, 98, 58) if i % 2 == 0 else (141, 89, 52)
        s.fill(base, (0, y, 200, 6))
        pygame.draw.line(s, (172, 114, 68), (0, y), (199, y))        # brillo de la tabla
        pygame.draw.line(s, (110, 68, 40), (0, y + 5), (199, y + 5))  # sombra entre tablas
        x = random.randint(0, 40)
        while x < 200:                                                 # uniones de las tablas
            pygame.draw.line(s, (110, 68, 40), (x, y + 1), (x, y + 4))
            x += random.randint(35, 60)
    return s


def main():
    pygame.init()
    os.makedirs(CARPETA, exist_ok=True)
    dibujos = {
        "ball.png": desde_grilla(PELOTA),
        "marco.png": desde_grilla(MARCO),
        "trofeo.png": desde_grilla(TROFEO),
        "exclamacion.png": desde_grilla(EXCLAMACION),
        "fondo_duelo.png": fondo_duelo(),
    }
    for nombre, surface in dibujos.items():
        pygame.image.save(surface, os.path.join(CARPETA, nombre))
        print(f"  -> assets/sprites/ui/{nombre} {surface.get_size()}")

    # decoración del mapa, ya al doble de tamaño (32 px = 1 casilla)
    carpeta_deco = os.path.join(os.path.dirname(CARPETA), "deco")
    os.makedirs(carpeta_deco, exist_ok=True)
    deco = {
        "arbol.png": desde_grilla(ARBOL),
        "flores_0.png": desde_grilla(FLORES),
        "flores_1.png": desde_grilla(desplazar(FLORES, range(2, 7), 1)),
        "matojo_0.png": desde_grilla(MATOJO),
        "matojo_1.png": desde_grilla(desplazar(MATOJO, range(8, 11), 1)),
        "cerca.png": desde_grilla(CERCA),
        "letrero.png": desde_grilla(LETRERO),
        "mini_mesa.png": desde_grilla(MINI_MESA),
    }
    for color, rgb in COLORES_MARIPOSA.items():
        paleta = {"a": rgb, "k": (50, 24, 50)}
        deco[f"mariposa_{color}_0.png"] = desde_grilla({"paleta": paleta, "pixeles": MARIPOSA_ABIERTA})
        deco[f"mariposa_{color}_1.png"] = desde_grilla({"paleta": paleta, "pixeles": MARIPOSA_CERRADA})
    for nombre, surface in deco.items():
        surface = al_doble(surface)
        pygame.image.save(surface, os.path.join(carpeta_deco, nombre))
        print(f"  -> assets/sprites/deco/{nombre} {surface.get_size()}")


if __name__ == "__main__":
    main()
