"""
audio.py
--------
TODO sonido del juego se pide aquí, por nombre (igual que asset_manager con
las imágenes). Los archivos viven en assets/sonidos/:
    musica_mapa.wav, musica_duelo.wav          -> música en loop
    victoria.wav, derrota.wav                  -> jingles al terminar un duelo
    golpe.wav, bote.wav, fallo.wav, acierto.wav,
    seleccionar.wav, choque.wav                -> efectos

Se generan con: python tools/generar_sonidos.py
Si falta un archivo, o el computador no tiene audio, el juego sigue
funcionando en silencio (nunca se cae por culpa del sonido).

Tecla M (en cualquier pantalla): silenciar / activar el sonido.
"""

import os
import pygame

from config import SONIDOS_DIR, VOLUMEN_MUSICA, VOLUMEN_EFECTOS


class Audio:
    def __init__(self):
        self._efectos = {}
        self._musica_actual = None
        self.silenciado = False

    def _listo(self):
        """True si hay mixer disponible. Lo intenta iniciar una sola vez."""
        if pygame.mixer.get_init():
            return True
        if getattr(self, "_fallo_init", False):
            return False
        try:
            pygame.mixer.init()
            return True
        except pygame.error:
            self._fallo_init = True  # sin tarjeta de sonido: todo queda en silencio
            return False

    def efecto(self, nombre):
        if self.silenciado or not self._listo():
            return
        if nombre not in self._efectos:
            ruta = os.path.join(SONIDOS_DIR, f"{nombre}.wav")
            sonido = None
            if os.path.isfile(ruta):
                try:
                    sonido = pygame.mixer.Sound(ruta)
                    sonido.set_volume(VOLUMEN_EFECTOS)
                except pygame.error:
                    sonido = None
            self._efectos[nombre] = sonido
        if self._efectos[nombre] is not None:
            self._efectos[nombre].play()

    def musica(self, nombre):
        """Pone una canción en loop. Si ya está sonando esa misma, no la reinicia."""
        if nombre == self._musica_actual:
            return
        self._musica_actual = nombre
        if not self._listo():
            return
        ruta = os.path.join(SONIDOS_DIR, f"{nombre}.wav")
        if not os.path.isfile(ruta):
            pygame.mixer.music.stop()
            return
        try:
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.set_volume(0 if self.silenciado else VOLUMEN_MUSICA)
            pygame.mixer.music.play(loops=-1, fade_ms=400)
        except pygame.error:
            pass

    def parar_musica(self, fade_ms=300):
        self._musica_actual = None
        if self._listo():
            pygame.mixer.music.fadeout(fade_ms)

    def alternar_silencio(self):
        self.silenciado = not self.silenciado
        if self._listo():
            pygame.mixer.music.set_volume(0 if self.silenciado else VOLUMEN_MUSICA)
            if self.silenciado:
                pygame.mixer.stop()  # corta los efectos que estén sonando


# instancia global única, se importa este objeto desde cualquier parte
audio = Audio()
