# -*- coding: utf-8 -*-
r"""
Plantilla tranquila: seis bloques de 5 s, sin cortes bruscos.

   0 –  5 s   título: rótulo, frase grande en cursiva y la fórmula del tema
   5 – 25 s   cuatro capítulos: rótulo, fórmula, visual que evoluciona de forma
              continua (p de 0 a 1 en el capítulo) y una frase breve
  25 – 30 s   cierre: resultado en dorado y dos líneas que se apagan

Transiciones por fundido a negro; zoom muy lento en todo el vídeo; polvo de luz
flotando en el fondo.  Sin golpes de zoom ni destellos.
"""
import numpy as np
from motor import Video, W, H, tex, pon, cabecera, caja_oro, rampa, suave, sale, clamp, C, ajusta

BLOQUE = 5.0
Y_ROT, Y_FORM, Y_VIS, Y_FRASE = 330, 560, 1110, 1555


def _polvo(n=70, semilla=11):
    rng = np.random.default_rng(semilla)
    return dict(x=rng.uniform(0, W, n), y=rng.uniform(0, H, n), v=rng.uniform(6, 22, n),
                r=rng.uniform(1.2, 3.4, n), a=rng.uniform(0.10, 0.35, n), f=rng.uniform(0, 6.28, n),
                col=rng.choice(["cian", "violeta", "texto"], n, p=[0.45, 0.35, 0.2]))


def _dibuja_polvo(L, t, P):
    for x, y, v, r, a, f, col in zip(P["x"], P["y"], P["v"], P["r"], P["a"], P["f"], P["col"]):
        yy = (y - v * t) % H
        xx = x + 14 * np.sin(0.4 * t + f)
        al = a * (0.6 + 0.4 * np.sin(1.3 * t + f))
        x0, x1 = int(max(0, xx - 3 * r)), int(min(W, xx + 3 * r + 1))
        y0, y1 = int(max(0, yy - 3 * r)), int(min(H, yy + 3 * r + 1))
        if x0 >= x1 or y0 >= y1:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1), np.arange(y0, y1))
        g = np.exp(-((gx - xx) ** 2 + (gy - yy) ** 2) / (2 * r * r))[..., None] * al
        L[y0:y1, x0:x1] = L[y0:y1, x0:x1] * (1 - g) + np.array(C[col], np.float32) * g


def construye(cfg):
    v = Video(cfg["nombre"])
    v.deriva = 0.035
    polvo = _polvo()

    @v.clip(0, 30.0)
    def fondo(L, t, lt, d):
        _dibuja_polvo(L, t, polvo)

    # ------------------------------------------------------------- título
    @v.clip(0, BLOQUE)
    def titulo(L, t, lt, d):
        a = rampa(t, 0.4, 1.2) * (1 - rampa(t, BLOQUE - 0.9, 0.8))
        cabecera(L, cfg["cabecera"], alfa=a)
        for i, linea in enumerate(cfg["titulo"]):
            img = tex(r"\textit{%s}" % linea, 66, "texto", math=False)
            pon(L, img, W / 2, 760 + 92 * i, alfa=a * rampa(t, 0.6 + 0.5 * i, 1.4), brillo=0.25,
                escala=ajusta(img) * (1.0 + 0.01 * t))
        f = tex(cfg["titulo_formula"], 64, "cian")
        pon(L, f, W / 2, 1120, alfa=a * rampa(t, 2.0, 1.4) * 0.9, brillo=0.35, escala=ajusta(f))

    # ------------------------------------------------------------- capítulos
    for k, cap in enumerate(cfg["capitulos"]):
        t0 = BLOQUE * (k + 1)

        def capitulo(L, t, lt, d, cap=cap):
            a = rampa(lt, 0.15, 0.9) * (1 - rampa(lt, d - 0.85, 0.8))
            if a <= 0.003:
                return
            cabecera(L, cfg["cabecera"], alfa=0.55 * a, color="tenue")
            rot = tex(r"\textsc{%s}" % cap["rotulo"], 34, "cian", math=False)
            pon(L, rot, W / 2, Y_ROT, alfa=a)
            f = tex(cap["formula"], 80)
            p_esc = clamp((lt - 0.3) / 1.6)
            pon(L, f, W / 2, Y_FORM, alfa=a * min(1, 0.2 + p_esc), barrido=sale(p_esc), brillo=0.28,
                escala=ajusta(f))
            pv = suave(clamp((lt - 0.4) / (d - 1.2)))
            pon(L, cap["visual"](pv), W / 2, Y_VIS, alfa=a * rampa(lt, 0.5, 1.0))
            fr = tex(r"\textit{%s}" % cap["frase"], 38, "tenue", math=False)
            pon(L, fr, W / 2, Y_FRASE, alfa=a * rampa(lt, 1.8, 1.0), escala=ajusta(fr, 940))
        v.clips.append((t0, t0 + BLOQUE, capitulo))

    # ------------------------------------------------------------- cierre
    @v.clip(BLOQUE * 5, 30.0)
    def cierre(L, t, lt, d):
        a = rampa(lt, 0.3, 1.2) * (1 - rampa(t, 28.6, 1.3))
        cabecera(L, cfg["cabecera"], alfa=0.7 * a)
        f = tex(cfg["final"], 96, "oro")
        caja_oro(L, f, W / 2, 860, alfa=a, escala=ajusta(f, 860) * (1.0 + 0.012 * lt))
        for i, linea in enumerate(cfg["frase"]):
            img = tex(r"\textit{%s}" % linea, 42, "texto", math=False)
            pon(L, img, W / 2, 1180 + 66 * i, alfa=a * 0.85 * rampa(lt, 1.2 + 0.6 * i, 1.0),
                escala=ajusta(img, 940))
    return v
