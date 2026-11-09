# -*- coding: utf-8 -*-
r"""
Plantilla de los edits: la misma coreografía para toda la serie.

  0,0 –  6,4 s   intro: rótulo, fórmula que se escribe, visual animado, pregunta
  6,4 – 19,2 s   drop A: 16 cortes de 2 pulsos (0,8 s); la fórmula cambia cada
                 2 cortes (8 pasos) con la anterior en sombra; el visual alterna
 19,2 – 25,6 s   drop B: 16 cortes de 1 pulso (0,4 s): fórmulas grandes, tarjetas
                 blancas, números y visuales
 25,6 – 30,0 s   cierre: resultado en un recuadro dorado y una frase

Todos los tiempos son múltiplos del pulso B = 0,4 s (150 BPM).
"""
import numpy as np
from motor import (Video, W, H, BEAT as B, tex, pon, rect, cabecera, caja_oro, rampa,
                   suave, sale, clamp, C, ajusta)

DROP_A, DROP_B, CIERRE, FIN = 16 * B, 48 * B, 64 * B, 30.0
Y_SOMBRA, Y_FORM, Y_VIS = 470, 700, 1225


def escribe(L, img, cx, cy, t, t0, dur=0.6, alfa=1.0, brillo=0.25, escala=1.0):
    """Revela la capa de izquierda a derecha, como si se escribiera."""
    if t < t0:
        return
    p = clamp((t - t0) / dur)
    pon(L, img, cx, cy, alfa=alfa * min(1, 0.3 + p), barrido=sale(p), brillo=brillo, escala=escala * ajusta(img))


def construye(cfg):
    """cfg: diccionario con el contenido del edit (ver edits.py)."""
    v = Video(cfg["nombre"])

    # ------------------------------------------------------------------ intro
    @v.clip(0, DROP_A)
    def intro(L, t, lt, d):
        cabecera(L, cfg["cabecera"], alfa=rampa(t, 0.1, 0.8))
        f = tex(cfg["intro_formula"], 92)
        extra = cfg.get("intro_extra", r"=\ ?")
        fx = W / 2 - (60 * rampa(t, 10 * B, 0.3) if extra else 0)
        escribe(L, f, fx, Y_FORM - 60, t, 1 * B, 4 * B)
        if extra and t >= 10 * B:             # «= ?» en dorado
            q = tex(extra, 92, "oro")
            pon(L, q, fx + f.shape[1] / 2 + 70, Y_FORM - 60, alfa=rampa(t, 10 * B, 0.25), brillo=0.6)
        prog = clamp((t - 5 * B) / (9 * B))
        if t >= 5 * B:
            vis = cfg["intro_visual"](suave(prog))
            pon(L, vis, W / 2, Y_VIS, alfa=rampa(t, 5 * B, 0.5))
        if t >= 12 * B:
            txt = tex(r"\textit{%s}" % cfg["intro_pregunta"], 36, "rojo", math=False)
            pon(L, txt, W / 2, 1530, alfa=rampa(t, 12 * B, 0.4))
    v.golpe(10 * B, 0.025)
    v.destello(10 * B, 0.18, "gris")
    v.golpe(DROP_A, 0.06)
    v.destello(DROP_A, 0.9)

    # ------------------------------------------------------------------ drop A
    pasos = cfg["pasos"]                      # 8 x (rótulo, fórmula)
    visA, visB = cfg["visual_A"], cfg["visual_B"]
    for k in range(16):
        t0 = DROP_A + 2 * k * B
        j = k // 2

        def clipA(L, t, lt, d, k=k, j=j, t0=t0):
            rotulo, form = pasos[j]
            cabecera(L, rotulo, color="tenue")
            if j > 0:
                g = tex(pasos[j - 1][1], 54, "tenue")
                pon(L, g, W / 2, Y_SOMBRA, alfa=0.42, escala=ajusta(g, 900))
            f = tex(form, 84)
            if k % 2 == 0:
                escribe(L, f, W / 2, Y_FORM, t, t0, 0.32, brillo=0.3)
            else:
                pon(L, f, W / 2, Y_FORM, brillo=0.3 + 0.25 * np.exp(-lt / 0.15), escala=ajusta(f))
            vis = (visA if k % 2 == 0 else visB)()
            pon(L, vis, W / 2, Y_VIS, escala=1.0 + 0.025 * lt)
        v.clips.append((t0, t0 + 2 * B, clipA))
        v.golpe(t0, 0.05 if k % 4 == 0 else 0.028)

    # ------------------------------------------------------------------ drop B
    rafaga = cfg["rafaga"]                    # 16 elementos
    for k, item in enumerate(rafaga):
        t0 = DROP_B + k * B

        def clipB(L, t, lt, d, item=item):
            tipo = item[0]
            if tipo == "f":                   # fórmula grande
                _, s, col = item[:3]
                px = item[3] if len(item) > 3 else 120
                img = tex(s, px, col)
                pon(L, img, W / 2, 930, brillo=0.5, escala=(1.06 - 0.06 * sale(lt / 0.3)) * ajusta(img))
            elif tipo == "w":                 # tarjeta blanca, fórmula negra
                L[:] = 0.96
                img = tex(item[1], 130, (0.04, 0.04, 0.05))
                pon(L, img, W / 2, 930, escala=(1.04 - 0.04 * sale(lt / 0.3)) * ajusta(img))
            elif tipo == "n":                 # número / texto en máquina de escribir
                img = tex(r"\texttt{%s}" % item[1], 96, item[2] if len(item) > 2 else "oro", math=False)
                pon(L, img, W / 2, 930, brillo=0.45)
            elif tipo == "v":                 # visual
                pon(L, item[1](), W / 2, 930, escala=1.05 - 0.05 * sale(lt / 0.3))
            elif tipo == "t":                 # frase corta
                img = tex(item[1], 60, item[2] if len(item) > 2 else "texto", math=False)
                pon(L, img, W / 2, 930, brillo=0.3)
        v.clips.append((t0, t0 + B, clipB))
        v.golpe(t0, 0.04 if item[0] != "w" else 0.02)
    v.destello(DROP_B, 0.6)

    # ------------------------------------------------------------------ cierre
    @v.clip(CIERRE, FIN)
    def cierre(L, t, lt, d):
        a = rampa(t, CIERRE, 0.35) * (1 - rampa(t, FIN - 1.0, 0.9))
        f = tex(cfg["final"], 100, "oro")
        caja_oro(L, f, W / 2, 860, alfa=a, escala=1.06 - 0.06 * sale(lt / 0.8))
        if t >= CIERRE + 3 * B:
            for i, linea in enumerate(cfg["frase"]):
                img = tex(r"\textit{%s}" % linea, 40, "tenue", math=False)
                pon(L, img, W / 2, 1180 + 62 * i, alfa=a * rampa(t, CIERRE + (3 + i) * B, 0.5))
        cabecera(L, cfg["cabecera"], alfa=a * 0.8)
    v.destello(CIERRE, 0.95, "oro")
    v.golpe(CIERRE, 0.06)
    return v
