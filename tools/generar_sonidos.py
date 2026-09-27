"""
generar_sonidos.py
-------------------
Genera TODA la música y los efectos del juego (estilo 8-bit / chiptune)
sintetizándolos con código, así no dependemos de descargar audio con
derechos de autor. Se guardan en assets/sonidos/ como .wav.

Uso (desde la carpeta del proyecto):
    python tools/generar_sonidos.py

Si alguien del equipo consigue o compone música propia, basta con
reemplazar el .wav con el mismo nombre; no hay que tocar código.
"""

import array
import math
import os
import random
import wave

FREQ = 22050  # muestras por segundo (suficiente para sonido 8-bit)
CARPETA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "sonidos")

NOTAS = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
random.seed(7)  # para que el ruido de la batería salga igual cada vez


def midi(nota):
    """'C#5' -> número MIDI."""
    nombre, octava = nota[:-1], int(nota[-1])
    return 12 * (octava + 1) + NOTAS[nombre]


def hz(numero_midi):
    return 440.0 * 2 ** ((numero_midi - 69) / 12)


# ---------- formas de onda ----------

def cuadrada(fase, duty=0.5):
    return 1.0 if (fase % 1.0) < duty else -1.0


def triangular(fase):
    f = fase % 1.0
    return 4 * f - 1 if f < 0.5 else 3 - 4 * f


def envolvente(i, total, ataque=0.005, soltar=0.03):
    """Evita los 'clics' al empezar y terminar cada nota."""
    t, fin = i / FREQ, total / FREQ
    if t < ataque:
        return t / ataque
    if t > fin - soltar:
        return max(0.0, (fin - t) / soltar)
    return 1.0


# ---------- pista (mezcla de varias voces) ----------

class Pista:
    def __init__(self, segundos):
        self.buf = [0.0] * int(segundos * FREQ)

    def nota(self, inicio, dur, freq, vol, onda="cuadrada", duty=0.5, staccato=0.9, vibrato=0.0):
        i0 = int(inicio * FREQ)
        n = int(dur * staccato * FREQ)
        fase = 0.0
        for i in range(n):
            if i0 + i >= len(self.buf):
                break
            f = freq * (1 + vibrato * math.sin(2 * math.pi * 6 * i / FREQ))
            fase += f / FREQ
            muestra = triangular(fase) if onda == "triangular" else cuadrada(fase, duty)
            self.buf[i0 + i] += muestra * vol * envolvente(i, n)

    def bombo(self, inicio, vol=0.9):
        i0, n, fase = int(inicio * FREQ), int(0.12 * FREQ), 0.0
        for i in range(n):
            if i0 + i >= len(self.buf):
                break
            t = i / FREQ
            fase += (150 * math.exp(-t * 25) + 45) / FREQ
            self.buf[i0 + i] += math.sin(2 * math.pi * fase) * vol * math.exp(-t * 20)

    def ruido(self, inicio, dur, vol, decaimiento):
        i0 = int(inicio * FREQ)
        for i in range(int(dur * FREQ)):
            if i0 + i >= len(self.buf):
                break
            self.buf[i0 + i] += random.uniform(-1, 1) * vol * math.exp(-(i / FREQ) * decaimiento)

    def guardar(self, nombre, pico=0.8):
        maximo = max(1e-9, max(abs(x) for x in self.buf))
        datos = array.array("h", (int(x / maximo * pico * 32767) for x in self.buf))
        os.makedirs(CARPETA, exist_ok=True)
        with wave.open(os.path.join(CARPETA, nombre), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(FREQ)
            w.writeframes(datos.tobytes())
        print(f"  -> assets/sonidos/{nombre} ({len(self.buf) / FREQ:.1f} s)")


def parsear(melodia):
    """'E5:.5 G5:.5 R:1' -> [('E5', 0.5), ('G5', 0.5), (None, 1.0)]"""
    salida = []
    for token in melodia.split():
        nota, beats = token.split(":")
        salida.append((None if nota == "R" else nota, float(beats)))
    return salida


ACORDES = {  # nota raíz (para el bajo) y notas del acorde (para el arpegio)
    "C": ("C3", ["C4", "E4", "G4"]), "Am": ("A2", ["A3", "C4", "E4"]),
    "F": ("F2", ["F3", "A3", "C4"]), "G": ("G2", ["G3", "B3", "D4"]),
    "E": ("E2", ["E3", "G#3", "B3"]),
}


def cancion(nombre, bpm, melodia, acordes, bombo_en, caja_en, duty_melodia=0.5, vol_arpegio=0.07):
    """acordes: un acorde por MEDIO compás (2 beats)."""
    beat = 60 / bpm
    compases = len(acordes) / 2
    pista = Pista(compases * 4 * beat)

    t = 0.0
    for nota, beats in parsear(melodia):
        if nota:
            pista.nota(t, beats * beat, hz(midi(nota)), 0.22, duty=duty_melodia, vibrato=0.004)
        t += beats * beat

    for k, acorde in enumerate(acordes):
        raiz, tonos = ACORDES[acorde]
        base = k * 2 * beat
        for corchea in range(4):  # bajo: raíz y octava alternadas
            f = hz(midi(raiz) + (12 if corchea % 2 else 0))
            pista.nota(base + corchea * beat / 2, beat / 2, f, 0.30, onda="triangular", staccato=0.8)
        for semi in range(8):  # arpegio rápido, bien bajito
            f = hz(midi(tonos[semi % 3]) + 12)
            pista.nota(base + semi * beat / 4, beat / 4, f, vol_arpegio, duty=0.25, staccato=0.7)

    total_beats = int(compases * 4)
    for b in range(total_beats):
        if b % 4 in bombo_en:
            pista.bombo(b * beat)
        if b % 4 in caja_en:
            pista.ruido(b * beat, 0.12, 0.25, 30)
        for medio in range(2):  # platillo en cada corchea
            pista.ruido(b * beat + medio * beat / 2, 0.03, 0.06, 150)
    pista.guardar(nombre)


def jingle(nombre, bpm, melodia, raices, vibrato_final=0.0):
    beat = 60 / bpm
    notas = parsear(melodia)
    pista = Pista(sum(b for _, b in notas) * beat + 0.3)
    t = 0.0
    for idx, (nota, beats) in enumerate(notas):
        if nota:
            ultima = idx == len(notas) - 1
            pista.nota(t, beats * beat, hz(midi(nota)), 0.3, staccato=0.95,
                       vibrato=vibrato_final if ultima else 0.0)
            pista.nota(t, beats * beat, hz(midi(nota) - 12), 0.12, duty=0.25, staccato=0.95)
        t += beats * beat
    t = 0.0
    for raiz, beats in raices:
        pista.nota(t, beats * beat, hz(midi(raiz)), 0.3, onda="triangular", staccato=0.95)
        t += beats * beat
    pista.guardar(nombre)


def efecto(nombre, segundos, funcion, pico=0.8):
    pista = Pista(segundos)
    fase = 0.0
    for i in range(len(pista.buf)):
        muestra, f = funcion(i / FREQ)
        pista.buf[i] = muestra(fase)
        fase += f / FREQ
    pista.guardar(nombre, pico)


def main():
    print("Generando música...")
    # Mapa: alegre, Do mayor, 120 bpm, 8 compases (16 s, hace loop perfecto)
    cancion(
        "musica_mapa.wav", 120,
        "E5:.5 G5:.5 C6:1 B5:.5 G5:.5 A5:1 "      # C
        "G5:1 E5:.5 C5:.5 D5:1 E5:1 "             # Am
        "F5:.5 G5:.5 A5:1 G5:.5 F5:.5 E5:.5 D5:.5 "  # F
        "D5:2 R:1 G4:1 "                          # G
        "E5:.5 G5:.5 C6:1 D6:.5 C6:.5 G5:1 "      # C
        "A5:1 C6:.5 B5:.5 A5:1 E5:1 "             # Am
        "F5:.5 A5:.5 C6:1 B5:.5 G5:.5 D5:1 "      # F G
        "C5:2 R:1 G4:1",                          # C
        ["C", "C", "Am", "Am", "F", "F", "G", "G", "C", "C", "Am", "Am", "F", "G", "C", "C"],
        bombo_en=(0, 2), caja_en=(), duty_melodia=0.5,
    )
    # Duelo: con energía, La menor, 150 bpm
    cancion(
        "musica_duelo.wav", 150,
        "A4:.5 C5:.5 E5:.5 A5:.5 G5:.5 E5:.5 C5:.5 E5:.5 "   # Am
        "F5:.5 A5:.5 C6:1 A5:.5 F5:.5 C5:1 "                 # F
        "E5:.5 G5:.5 C6:.5 G5:.5 E5:.5 G5:.5 C6:.5 E6:.5 "   # C
        "D6:1 B5:.5 G5:.5 D5:1 R:1 "                         # G
        "A5:.5 A5:.5 R:.5 A5:.5 G5:.5 A5:.5 C6:1 "           # Am
        "A5:.5 F5:.5 R:.5 F5:.5 E5:.5 F5:.5 A5:1 "           # F
        "G5:.5 E5:.5 C5:.5 E5:.5 G5:.5 B5:.5 D6:.5 B5:.5 "   # C G
        "E5:1 G#5:1 B5:1 E6:1",                              # E (vuelve a Am)
        ["Am", "Am", "F", "F", "C", "C", "G", "G", "Am", "Am", "F", "F", "C", "G", "E", "E"],
        bombo_en=(0, 2), caja_en=(1, 3), duty_melodia=0.25, vol_arpegio=0.05,
    )

    print("Generando jingles...")
    jingle("victoria.wav", 150, "G4:.33 C5:.33 E5:.34 G5:1 E5:.5 G5:2",
           [("C3", 1), ("G2", 1), ("C3", 2.5)])
    jingle("derrota.wav", 100, "G4:.5 F#4:.5 F4:.5 E4:2", [("C3", 1.5), ("C3", 2)], vibrato_final=0.02)

    print("Generando efectos...")
    # golpe de raqueta: "toc" agudo y cortito
    efecto("golpe.wav", 0.08, lambda t: (
        (lambda fase: math.sin(2 * math.pi * fase) * math.exp(-t * 70) + random.uniform(-1, 1) * 0.3 * math.exp(-t * 400)),
        1500))
    # bote en la mesa: parecido pero más grave y suave
    efecto("bote.wav", 0.06, lambda t: (
        (lambda fase: math.sin(2 * math.pi * fase) * math.exp(-t * 110)), 950), pico=0.55)
    # fallo: tono que baja, tipo "fuiiu"
    efecto("fallo.wav", 0.5, lambda t: (
        (lambda fase: cuadrada(fase, 0.5) * 0.6 * min(1, (0.5 - t) * 10)), 520 * math.exp(-t * 2.6)), pico=0.5)
    # acierto: dos notas rápidas hacia arriba
    efecto("acierto.wav", 0.22, lambda t: (
        (lambda fase: cuadrada(fase, 0.25) * math.exp(-(t % 0.08) * 12)), hz(midi("E6") if t < 0.08 else midi("B6"))), pico=0.45)
    # seleccionar en menús
    efecto("seleccionar.wav", 0.1, lambda t: (
        (lambda fase: cuadrada(fase, 0.5) * (1 - t * 8)), 880 if t < 0.05 else 1320), pico=0.4)
    # chocar contra una pared en el mapa
    efecto("choque.wav", 0.09, lambda t: (
        (lambda fase: triangular(fase) * math.exp(-t * 35)), 95), pico=0.7)
    print("Listo.")


if __name__ == "__main__":
    main()
