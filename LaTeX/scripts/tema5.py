#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Simulaciones del Tema 5 (Energía y fuerzas, primera parte).

Genera, para las figuras pgfplots del documento:

  * datos/t5-dos-cargas-{iguales,opuestas}.tex
      Líneas de campo EXACTAS de dos cargas puntuales en el eje x.  Para cargas
      sobre un eje, el flujo de E a través de un casquete es proporcional a
          psi(x, rho) = sum_i q_i (x - x_i) / |r - r_i| ,
      y las líneas de campo son las curvas de nivel psi = cte (sin integrar EDO).
  * datos/t5-dipolo-exterior.tex
      Líneas de campo del dipolo puntual fuera de una esfera de radio a = 1
      (problema 5.2): psi = sen^2(theta) / r.
  * img/t5-ue-{iguales,opuestas,cruzado}-{oscuro,claro}.png
      Mapas de la densidad de energía u_e = eps0 E^2 / 2 (escala logarítmica) y
      del término cruzado eps0 E1.E2, con la paleta de cada tema del documento.
  * img/t5-portada-oscuro.png
      Gráfica 3D de portada: plano con las líneas de campo de un par de cargas
      opuestas sobre su densidad de energía.

Uso:  python3 tema5.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(AQUI, "..", "datos")
IMG = os.path.join(AQUI, "..", "img")
os.makedirs(DATOS, exist_ok=True)

PALETA = {
    "oscuro": dict(fondo="#000000", energia=["#000000", "#0c0a1d", "#1d1745", "#352a70",
                                              "#5a4a9c", "#8a78c8"],
                   pos="#ff6b6b", neg="#5b8cff"),
    "claro": dict(fondo="#ffffff", energia=["#ffffff", "#f3f0fe", "#e0d8fc", "#c6b6f8",
                                             "#a690ef", "#8a6de6"],
                  pos="#d23b3b", neg="#2c4fc7"),
}


# ---------------------------------------------------------------- utilidades
def remuestrea(p, paso=0.04):
    d = np.r_[0.0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    if d[-1] < 1e-9:
        return p
    n = max(int(d[-1] / paso), 3)
    s = np.linspace(0.0, d[-1], n + 1)
    return np.c_[np.interp(s, d, p[:, 0]), np.interp(s, d, p[:, 1])]


def contornos(X, Y, Z, niveles):
    fig, ax = plt.subplots()
    cs = ax.contour(X, Y, Z, levels=niveles)
    segs = [s for nivel in cs.allsegs for s in nivel if len(s) > 2]
    plt.close(fig)
    return segs


def campo_cargas(cargas, x, y):
    Ex = np.zeros_like(x, dtype=float)
    Ey = np.zeros_like(x, dtype=float)
    for q, x0 in cargas:
        dx, dy = x - x0, y
        r3 = np.maximum(np.hypot(dx, dy), 1e-6) ** 3
        Ex += q * dx / r3
        Ey += q * dy / r3
    return Ex, Ey


def orienta(seg, cargas):
    k = len(seg) // 2
    t = seg[min(k + 1, len(seg) - 1)] - seg[max(k - 1, 0)]
    ex, ey = campo_cargas(cargas, np.array(seg[k, 0]), np.array(seg[k, 1]))
    return seg if t[0] * ex + t[1] * ey >= 0 else seg[::-1]


def recorta_cerca(segs, puntos, r0):
    """Trocea las líneas que pasan a menos de r0 de alguno de los puntos."""
    out = []
    for s in segs:
        lejos = np.ones(len(s), bool)
        for (px, py) in puntos:
            lejos &= np.hypot(s[:, 0] - px, s[:, 1] - py) > r0
        cur = []
        for p, b in zip(s, lejos):
            if b:
                cur.append(p)
            else:
                if len(cur) > 2:
                    out.append(np.array(cur))
                cur = []
        if len(cur) > 2:
            out.append(np.array(cur))
    return out


def flechas(s, xs=(-2.0, 2.0), alt=(-0.45, 0.45)):
    """Fracciones de arco donde poner flechas: cruces con x = xs; si no hay, con x = alt."""
    d = np.r_[0.0, np.cumsum(np.hypot(*np.diff(s, axis=0).T))]
    if d[-1] < 1e-9:
        return []
    for grupo in (xs, alt):
        fr = []
        for x0 in grupo:
            for i in range(len(s) - 1):
                a, b = s[i, 0] - x0, s[i + 1, 0] - x0
                if a == 0 or a * b < 0:
                    t = a / (a - b) if a != b else 0.0
                    fr.append((d[i] + t * (d[i + 1] - d[i])) / d[-1])
                    break
        fr = [f for f in fr if 0.06 < f < 0.94]
        if fr:
            return fr
    return [0.5]


def escribe(nombre, bloques):
    ruta = os.path.join(DATOS, nombre + ".tex")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("%% Generado por scripts/tema5.py -- no editar a mano\n")
        for estilo, segs in bloques:
            for s in segs:
                opc = estilo + "".join(", flechaen=%.3f" % fr for fr in flechas(s))
                pts = " ".join("(%.3f,%.3f)" % (x, y) for x, y in s)
                f.write("\\addplot[%s] coordinates {%s};\n" % (opc, pts))
    print("  ->", os.path.relpath(ruta, os.path.join(AQUI, "..")))


# ---------------------------------------------------------------- dos cargas
def dos_cargas(qs, nombre, xm=2.6, ym=1.8):
    cargas = [(qs[0], -1.0), (qs[1], 1.0)]
    x = np.linspace(-xm, xm, 1000)
    y = np.linspace(1e-4, ym, 400)
    X, Y = np.meshgrid(x, y)
    psi = sum(q * (X - x0) / np.hypot(X - x0, Y) for q, x0 in cargas)
    if qs[0] == qs[1]:
        niveles = np.linspace(-1.85, 1.85, 13)          # equal charges
        niveles = [v for v in niveles if abs(abs(v) - 2) > 0.05]
    else:
        niveles = np.linspace(0.12, 1.88, 9)            # opposite charges
    segs = contornos(X, Y, psi, niveles)
    segs = recorta_cerca(segs, [(-1, 0), (1, 0)], 0.13)
    segs = [orienta(remuestrea(s), cargas) for s in segs]
    segs = segs + [np.c_[s[:, 0], -s[:, 1]] for s in segs]
    # eje
    ejes = []
    if qs[0] == qs[1]:
        ejes = [np.array([[-1.13, 0], [-xm, 0]]), np.array([[1.13, 0], [xm, 0]])]
        if qs[0] < 0:
            ejes = [e[::-1] for e in ejes]
    else:
        e = np.array([[-0.87, 0], [0.87, 0]])
        ejes = [e if qs[0] > 0 else e[::-1],
                np.array([[-xm, 0], [-1.13, 0]]) if qs[0] < 0 else np.array([[-1.13, 0], [-xm, 0]]),
                np.array([[1.13, 0], [xm, 0]]) if qs[1] > 0 else np.array([[xm, 0], [1.13, 0]])]
    escribe(nombre, [("lineaE", segs), ("lineaE", ejes)])


# ---------------------------------------------------------------- dipolo
def dipolo_exterior(xm=2.6, ym=2.0):
    x = np.linspace(-xm, xm, 900)
    y = np.linspace(1e-4, ym, 360)
    X, Y = np.meshgrid(x, y)
    R = np.hypot(X, Y)
    psi = np.ma.masked_where(R < 1.0, Y**2 / R**3)       # sen^2(theta)/r
    niveles = [0.08, 0.17, 0.28, 0.42, 0.6, 0.82]
    segs = [remuestrea(s) for s in contornos(X, Y, psi, niveles)]
    # sentido: dipolo según +x; en el ecuador E apunta hacia -x
    out = []
    for s in segs:
        k = np.argmax(s[:, 1])
        out.append(s if s[0, 0] > s[-1, 0] else s[::-1])
    out = out + [np.c_[s[:, 0], -s[:, 1]] for s in out]
    ejes = [np.array([[1.0, 0], [xm, 0]]), np.array([[-xm, 0], [-1.0, 0]])]
    escribe("t5-dipolo-exterior", [("lineaE", out), ("lineaE", ejes)])


# ---------------------------------------------------------------- mapas de u_e
def mapas():
    xm, ym = 2.6, 1.8
    n = 900
    x = np.linspace(-xm, xm, n)
    y = np.linspace(-ym, ym, int(n * ym / xm))
    X, Y = np.meshgrid(x, y)
    casos = {"iguales": (1, 1), "opuestas": (1, -1)}
    for modo, pal in PALETA.items():
        cm = LinearSegmentedColormap.from_list("e", pal["energia"])
        for nombre, qs in casos.items():
            Ex, Ey = campo_cargas([(qs[0], -1.0), (qs[1], 1.0)], X, Y)
            u = np.log10(np.maximum(Ex**2 + Ey**2, 1e-6))
            img = cm(Normalize(-2.4, 2.2, clip=True)(u))
            ruta = os.path.join(IMG, "t5-ue-%s-%s.png" % (nombre, modo))
            Image.fromarray((img[::-1] * 255).astype(np.uint8)).save(ruta)
        # término cruzado E1.E2 para cargas iguales (signo: +) -> divergente
        E1x, E1y = campo_cargas([(1, -1.0)], X, Y)
        E2x, E2y = campo_cargas([(1, 1.0)], X, Y)
        c = E1x * E2x + E1y * E2y
        s = np.sign(c) * np.log10(1 + np.abs(c) / 0.02)
        div = LinearSegmentedColormap.from_list(
            "d", [pal["neg"], pal["fondo"], pal["pos"]])
        img = div(Normalize(-3.2, 3.2, clip=True)(s))
        ruta = os.path.join(IMG, "t5-ue-cruzado-%s.png" % modo)
        Image.fromarray((img[::-1] * 255).astype(np.uint8)).save(ruta)
    print("  -> img/t5-ue-*.png")


# ---------------------------------------------------------------- portada
def portada():
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    cols = ["#5b6cff", "#2fb6e6", "#33d1a0", "#b6e04a", "#ffd23f", "#ff9a3c", "#ff5e7a", "#c066ff"]
    arco = LinearSegmentedColormap.from_list("arcoiris", cols)
    cargas = [(1, -1.0), (-1, 1.0)]
    xm, ym = 3.0, 2.2
    # líneas de campo (semiplano superior + espejo)
    x = np.linspace(-xm, xm, 1400)
    y = np.linspace(1e-4, ym, 600)
    X, Y = np.meshgrid(x, y)
    psi = sum(q * (X - x0) / np.hypot(X - x0, Y) for q, x0 in cargas)
    niveles = np.linspace(0.06, 1.94, 19)
    segs = recorta_cerca(contornos(X, Y, psi, niveles), [(-1, 0), (1, 0)], 0.09)
    segs = [remuestrea(s, 0.02) for s in segs if len(s) > 10]
    # densidad de energía sobre el plano
    gx = np.linspace(-xm, xm, 420)
    gy = np.linspace(-ym, ym, 320)
    GX, GY = np.meshgrid(gx, gy)
    Ex, Ey = campo_cargas(cargas, GX, GY)
    u = np.log10(np.maximum(Ex**2 + Ey**2, 1e-6))
    cmap = LinearSegmentedColormap.from_list(
        "glow", ["#000000", "#05040c", "#140f2e", "#2e2560", "#5a4aa0", "#20b4ce"])
    fc = cmap(Normalize(-2.2, 2.6, clip=True)(u))
    fc[..., 3] = np.clip(0.15 + 0.85 * Normalize(-2.2, 2.6, clip=True)(u), 0, 1)

    fig = plt.figure(figsize=(12, 7), dpi=220)
    ax = fig.add_axes([0, 0, 1, 1], projection="3d")
    fig.patch.set_alpha(0.0)
    ax.set_facecolor((0, 0, 0, 0))
    ax.set_axis_off()
    ax.computed_zorder = False
    ax.plot_surface(GX, GY, np.zeros_like(GX), facecolors=fc, rstride=1, cstride=1,
                    linewidth=0, antialiased=False, shade=False, zorder=1)
    n = len(niveles)
    for s in segs:
        # color según el nivel psi del punto medio de la línea
        k = len(s) // 2
        pv = sum(q * (s[k, 0] - x0) / np.hypot(s[k, 0] - x0, s[k, 1]) for q, x0 in cargas)
        c = arco(np.clip((pv - 0.06) / 1.88, 0, 1))
        for sg in (1, -1):
            ax.plot(s[:, 0], sg * s[:, 1], 0 * s[:, 0], color=c, lw=4.0, alpha=0.07, zorder=2)
            ax.plot(s[:, 0], sg * s[:, 1], 0 * s[:, 0], color=c, lw=1.0, alpha=0.95, zorder=3)
    ax.plot([-0.91, 0.91], [0, 0], [0, 0], color="#f0f0f0", lw=1.2, alpha=0.8, zorder=3)
    # cargas como esferas luminosas
    uu, vv = np.mgrid[0:2 * np.pi:40j, 0:np.pi:20j]
    for (q, x0), col in zip(cargas, ["#ff6b6b", "#5b8cff"]):
        r = 0.085
        ax.plot_surface(x0 + r * np.cos(uu) * np.sin(vv), r * np.sin(uu) * np.sin(vv),
                        r * np.cos(vv), color=col, linewidth=0, shade=True, zorder=5)
    ax.set_xlim(-2.8, 2.8); ax.set_ylim(-2.1, 2.1); ax.set_zlim(-1.0, 1.0)
    ax.set_box_aspect((5.6, 4.2, 2.0))
    ax.view_init(elev=30, azim=-60)
    ruta = os.path.join(IMG, "t5-portada-oscuro.png")
    fig.savefig(ruta, transparent=True, dpi=220)
    plt.close(fig)
    im = Image.open(ruta)
    im = im.crop(im.getbbox())
    im.save(ruta)
    print("  ->", ruta, im.size)


if __name__ == "__main__":
    dos_cargas((1, 1), "t5-dos-cargas-iguales")
    dos_cargas((1, -1), "t5-dos-cargas-opuestas")
    dipolo_exterior()
    mapas()
    portada()
