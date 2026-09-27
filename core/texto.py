"""
texto.py
--------
Utilidades para dibujar texto. pygame no hace salto de línea solo, así que
cualquier texto largo (preguntas, opciones, mensajes) debe pasar por aquí.
"""


def envolver_texto(texto, fuente, ancho_max):
    """Parte 'texto' en líneas que quepan en 'ancho_max' pixeles con 'fuente'.
    Si una sola palabra es más ancha que ancho_max, la corta por caracteres."""
    lineas = []
    linea_actual = ""

    for palabra in texto.split():
        # palabra más ancha que la caja: se corta en pedazos
        while fuente.size(palabra)[0] > ancho_max:
            corte = len(palabra)
            while corte > 1 and fuente.size(palabra[:corte])[0] > ancho_max:
                corte -= 1
            if linea_actual:
                lineas.append(linea_actual)
                linea_actual = ""
            lineas.append(palabra[:corte])
            palabra = palabra[corte:]

        candidata = f"{linea_actual} {palabra}" if linea_actual else palabra
        if fuente.size(candidata)[0] <= ancho_max:
            linea_actual = candidata
        else:
            lineas.append(linea_actual)
            linea_actual = palabra

    if linea_actual:
        lineas.append(linea_actual)
    return lineas or [""]


def dibujar_lineas(pantalla, lineas, fuente, color, x, y, centrado=False, ancho_centro=0):
    """Dibuja una lista de líneas una debajo de otra. Devuelve la 'y' final.
    Si centrado=True, cada línea se centra respecto a x + ancho_centro / 2."""
    alto_linea = fuente.get_linesize()
    for linea in lineas:
        render = fuente.render(linea, True, color)
        destino_x = x + (ancho_centro - render.get_width()) // 2 if centrado else x
        pantalla.blit(render, (destino_x, y))
        y += alto_linea
    return y
