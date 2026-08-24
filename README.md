# Ping Pong RPG — Del ping pong al tenis de mesa

Juego educativo estilo Pokémon (2D, pixel art, top-down) hecho en `pygame`
para la electiva de Ping Pong. Reemplaza los combates Pokémon por duelos
de preguntas sobre tenis de mesa: historia, reglamentación, indumentaria,
fundamentación técnica y arbitraje.

## Cómo correrlo

```bash
pip install pygame
python main.py
```

Controles:
- Mover: flechas o `WASD`
- Chocar contra un rival en el mapa = empieza el duelo automáticamente
- Responder en el duelo: teclas `1`, `2`, `3`, `4`
- Terminar duelo: `ESPACIO` para volver al mapa

## Reglas del duelo (ya implementadas en `battle/match_manager.py`)

Un solo juego a **11 puntos**, ganando con **diferencia mínima de 2**
(si va 10-10 sigue hasta que alguien saque ventaja de 2). Esto es la
regla real de la ITTF para un game de tenis de mesa.

Si más adelante quieren pasar a "mejor de 3" o "mejor de 5" games,
solo cambien `JUEGOS_POR_DUELO` en `config.py`; `MatchManager` ya está
preparado para eso, no hay que tocar nada más.

## División del trabajo sugerida

- **Persona A (código/lógica):** trabaja dentro de `core/`, `states/`,
  `battle/`, `entities/`. No necesita esperar el arte: el juego ya corre
  con placeholders de colores generados automáticamente.
- **Persona B (contenido/arte):**
  - Llena `data/questions.json` con las preguntas reales de los 5 temas
    (historia, reglamentacion, indumentaria, tecnica, arbitraje). El
    campo `"correcta"` es el índice (empezando en 0) de la opción correcta
    dentro de `"opciones"`.
  - Exporta el pixel art del iPad respetando EXACTAMENTE estos nombres
    de archivo y los deja en la carpeta indicada. El juego los detecta
    solos, sin tocar código:

```
assets/sprites/player/player_walk_down_0.png
assets/sprites/player/player_walk_up_0.png
assets/sprites/player/player_walk_left_0.png
assets/sprites/player/player_walk_right_0.png

assets/sprites/rivals/rival_historia.png
assets/sprites/rivals/rival_reglamentacion.png
assets/sprites/rivals/rival_indumentaria.png
assets/sprites/rivals/rival_tecnica.png
assets/sprites/rivals/rival_arbitraje.png

assets/sprites/tiles/tile_pasto.png
assets/sprites/tiles/tile_pared.png
assets/sprites/tiles/tile_mesa.png

assets/sprites/ui/ball.png
```

  Tamaño recomendado: 32x32 px para tiles y personajes (coincide con
  `TILE_SIZE` en `config.py`), 64x64 o más para el sprite del rival en
  la pantalla de batalla (se reescala solo).

## Editar el mapa

`data/map.csv` es el mapa. Es una grilla de texto separada por comas:

- `.` = piso caminable
- `#` = pared / no caminable
- `P` = posición inicial del jugador (una sola vez en el archivo)
- `1` a `5` = un rival de cada tema, en este orden (ver `config.TEMAS`):
  `1=historia, 2=reglamentacion, 3=indumentaria, 4=tecnica, 5=arbitraje`

Pueden agitar filas/columnas libremente, solo cuidando que todas las
filas tengan el mismo número de columnas (si no, el juego truena al cargar).

## Qué falta / próximos pasos

- [ ] Llenar `data/questions.json` con preguntas reales (con buena
      investigación y fuentes — recuerden que la profe pide bibliografía
      APA en el recurso escrito, aunque acá en el JSON no hace falta citarlo).
- [ ] Reemplazar los placeholders por el pixel art real.
- [ ] (Opcional) Sonido al acertar/fallar.
- [ ] (Opcional) Animación de "victoria" del jugador en vez de solo texto.

## Recordatorio importante para la entrega completa

Este juego cubre el punto de "presentación interactiva" de la guía de
la profesora, pero la webquest pide ADEMÁS: un PPT/Canva/Slides con la
investigación, un libro en Calameo o Book Creator, un juego de evaluación
en Educaplay, y todo publicado en una página de Google Sites, citando
fuentes en formato APA. El pygame no reemplaza esas otras entregas.
