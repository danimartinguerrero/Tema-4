# Tema 4. Materiales dieléctricos — código LaTeX

Apuntes formalizados (Electromagnetismo I) y guía de métodos, en versión **luminosa** y **oscura**
desde el mismo código. Compilar con **LuaLaTeX** (dos pasadas):

```
lualatex Tema4-claro.tex      lualatex Tema4-oscuro.tex
lualatex Guia-T4-claro.tex    lualatex Guia-T4-oscuro.tex
```

| Carpeta | Contenido |
|---|---|
| `estilo/` | Preámbulo común (fuentes Latin Modern, paleta por tema, entornos, notación) y portada |
| `tema4/` | Cuerpo del tema: secciones 1–8 (teoría, cavidades, seminarios) y apéndice |
| `guia/` | Guía de métodos y fichas de los doce problemas |
| `figuras/` | Todas las figuras en TikZ/pgfplots (usan la paleta del tema activo) |
| `datos/` | Líneas de campo y equipotenciales calculadas (generadas, no editar) |
| `scripts/` | `lineas_campo.py` (funciones de corriente de Stokes exactas) y `portada.py` |
| `img/` | Logotipos y gráfica de portada |

El tema se elige en la primera línea de cada fichero maestro (`\oscurotrue` / `\oscurofalse`).
Para regenerar los datos: `python3 scripts/lineas_campo.py && python3 scripts/portada.py`.
