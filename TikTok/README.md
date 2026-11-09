# Edits de TikTok · Electromagnetismo I

Serie de cuatro edits verticales (1080×1920, 30 fps, 30 s) sobre energía electrostática
y dieléctricos, con la tipografía y la paleta de los apuntes. Todo se genera por código:

| Edit | Contenido |
|---|---|
| `01-energia` | de ½Σqφ a (ε₀/2)∫E² dV; la energía vive en el campo |
| `02-earnshaw-fuerzas` | teorema de Earnshaw, punto de silla y trabajos virtuales |
| `03-dielectricos` | polarización, cargas ligadas, D y esfera dieléctrica |
| `04-cavidades` | aguja, esfera y lenteja; factor de despolarización |

Coreografía común a 150 BPM: intro escrita (0–6,4 s), cortes cada 2 pulsos (6,4–19,2 s),
ráfaga de 1 pulso (19,2–25,6 s) y cierre dorado. Música original sintetizada (`musica.py`).

```
python3 edits.py todos              # renderiza la serie (≈ 4 min con 4 núcleos)
python3 edits.py energia --preview  # fotogramas de control
```
Requiere pdflatex, pdftocairo, ffmpeg, numpy, scipy y matplotlib.

## Serie tranquila (`videos/tranquilos/`)

Los mismos cuatro temas en seis bloques de 5 s (título, cuatro capítulos y cierre), con fundidos a negro,
visuales que evolucionan de forma continua (la carga que llega, las cargas que se separan, la permitividad que
crece, la cavidad que pasa de aguja a lenteja…), polvo de luz, un zoom muy lento y música ambient sin percusión.

```
python3 edits_calma.py todos
```
