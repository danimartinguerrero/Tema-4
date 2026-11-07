# Tema 4. Materiales dieléctricos — código LaTeX

Apuntes formalizados (Electromagnetismo I) y guía de métodos, en versión **luminosa** y **oscura**
desde el mismo código. Compilar con **LuaLaTeX** (dos pasadas):

```
lualatex Tema4-claro.tex      lualatex Tema4-oscuro.tex
lualatex Guia-T4-claro.tex    lualatex Guia-T4-oscuro.tex
lualatex Repaso-T4-claro.tex  lualatex Repaso-T4-oscuro.tex
lualatex Tema5-oscuro.tex     lualatex Guia-T5-oscuro.tex
```

| Carpeta | Contenido |
|---|---|
| `estilo/` | Preámbulo común (fuentes Latin Modern, paleta por tema, entornos, notación) y portada |
| `tema4/` | Cuerpo del tema: secciones 1–8 (teoría, cavidades, seminarios) y apéndice |
| `guia/` | Guía de métodos y fichas de los doce problemas |
| `repaso/` | Repaso conceptual breve para cuestionarios teóricos (ideas clave, trampas, preguntas razonadas) |
| `tema5/`, `guia5/`, `figuras5/` | Tema 5 (Energía y fuerzas, primera parte): cuerpo, guía y figuras |
| `figuras/` | Todas las figuras en TikZ/pgfplots (usan la paleta del tema activo) |
| `datos/` | Líneas de campo y equipotenciales calculadas (generadas, no editar) |
| `scripts/` | `lineas_campo.py`, `portada.py` (Tema 4) y `tema5.py` (líneas de campo, mapas de $u_e$ y portada del Tema 5) |
| `img/` | Logotipos y gráfica de portada |

El tema se elige en la primera línea de cada fichero maestro (`\oscurotrue` / `\oscurofalse`).
Para regenerar los datos: `python3 scripts/lineas_campo.py && python3 scripts/portada.py`.
