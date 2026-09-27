"""
question_bank.py
-----------------
Lee data/questions.json y entrega preguntas al azar de un tema específico,
sin repetir dentro del mismo duelo (hasta que se acaben, ahí sí puede reciclar).

Quien va llenando las preguntas SOLO edita data/questions.json.
No necesita tocar este archivo.
"""

import json
import random

from config import QUESTIONS_PATH, TEMAS


class QuestionBank:
    def __init__(self):
        with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
            self._preguntas_por_tema = json.load(f)

        for tema in TEMAS:
            if tema not in self._preguntas_por_tema:
                self._preguntas_por_tema[tema] = []

    def obtener_pregunta_aleatoria(self, tema: str, usadas: set):
        """
        tema: uno de config.TEMAS
        usadas: set de índices ya usados en este duelo (para no repetir)
        Devuelve (indice, pregunta_dict) o (None, None) si no hay preguntas.
        """
        preguntas = self._preguntas_por_tema.get(tema, [])
        if not preguntas:
            return None, None

        disponibles = [i for i in range(len(preguntas)) if i not in usadas]
        if not disponibles:
            disponibles = list(range(len(preguntas)))  # se acabaron, reciclamos

        indice = random.choice(disponibles)
        return indice, self._con_opciones_revueltas(preguntas[indice])

    @staticmethod
    def _con_opciones_revueltas(pregunta):
        """Devuelve una copia de la pregunta con las opciones en orden aleatorio
        (y 'correcta' actualizado), para que no se memorice "era la 2"."""
        orden = list(range(len(pregunta["opciones"])))
        random.shuffle(orden)
        return {
            "pregunta": pregunta["pregunta"],
            "opciones": [pregunta["opciones"][i] for i in orden],
            "correcta": orden.index(pregunta["correcta"]),
        }
