"""
state.py
--------
Clase base para todas las "pantallas" del juego (menú, mapa, batalla, resultado).
Cada estado nuevo hereda de esta clase e implementa sus propios métodos.
"""


class State:
    def __init__(self, game):
        self.game = game  # referencia al objeto Game, para cambiar de estado o leer assets

    def manejar_evento(self, evento):
        """Se llama por cada evento de pygame (teclado, mouse, etc)."""
        pass

    def actualizar(self, dt):
        """Se llama cada frame para actualizar lógica. dt = tiempo en segundos."""
        pass

    def dibujar(self, pantalla):
        """Se llama cada frame para dibujar en la pantalla."""
        pass
