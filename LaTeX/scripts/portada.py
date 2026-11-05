#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gráfica de portada del Tema 4: haz tridimensional de líneas del vector
desplazamiento D alrededor de una esfera dieléctrica (eps_r = 5) sumergida en un
campo uniforme.  Las líneas de D son continuas (no hay carga libre) y se
concentran al atravesar la esfera: es la imagen visual de la polarización.

Las líneas son curvas de nivel exactas de la función de corriente de Stokes

    psi_D = eps0 E0 rho^2 [1/2 + beta a^3/r^3]      (r > a)
    psi_D = eps0 E0 rho^2 (3 eps_r / (eps_r + 2)) / 2 (r < a)

con beta = (eps_r - 1)/(eps_r + 2), giradas alrededor del eje del campo.

Uso:  python3 portada.py      -> img/portada-oscuro.png, img/portada-claro.png
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap

AQUI = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(AQUI, "..", "img")

ER = 5.0
BETA = (ER - 1) / (ER + 2)


def lineas_meridianas(hs, xm=3.4):
    """Líneas de D en el semiplano meridiano (x, rho >= 0) para cada rho_inf = h."""
    x = np.linspace(-xm, xm, 1400)
    y = np.linspace(1e-4, 2.6, 700)
    X, Y = np.meshgrid(x, y)
    R = np.hypot(X, Y)
    Z = np.where(R > 1, 0.5 * Y**2 + BETA * Y**2 / R**3, 0.5 * Y**2 * 3 * ER / (ER + 2))
    fig, ax = plt.subplots()
    out = []
    for h in hs:
        cs = ax.contour(X, Y, Z, levels=[0.5 * h**2])
        segs = [s for s in cs.allsegs[0] if len(s) > 10]
        s = max(segs, key=len)
        if s[0, 0] > s[-1, 0]:
            s = s[::-1]
        out.append(s)
    plt.close(fig)
    return out


def render(modo):
    oscuro = modo == "oscuro"
    cols = ["#5b6cff", "#2fb6e6", "#33d1a0", "#b6e04a", "#ffd23f", "#ff9a3c", "#ff5e7a", "#c066ff"]
    if not oscuro:
        cols = ["#3341c9", "#1488b8", "#0f9a70", "#6f9c16", "#c99700", "#d6661a", "#d6304f", "#8f36d6"]
    cmap = LinearSegmentedColormap.from_list("arcoiris", cols)

    hs = np.linspace(0.14, 2.3, 17)
    segs = lineas_meridianas(hs)

    fig = plt.figure(figsize=(12, 7), dpi=220)
    ax = fig.add_axes([0, 0, 1, 1], projection="3d")
    fig.patch.set_alpha(0.0)
    ax.set_facecolor((0, 0, 0, 0))
    ax.set_axis_off()
    ax.computed_zorder = False

    # Plano meridiano (y = rho*cos, z = 0): líneas de D a ambos lados del eje
    n = len(hs)
    for j, s in enumerate(segs):
        c = cmap(j / (n - 1))
        for sg in (1, -1):
            X, Y = s[:, 0], sg * s[:, 1]
            Z = 0.10 * np.exp(-((X / 1.6) ** 2)) * 0  # plano
            ax.plot(X, Y, Z, color=c, lw=4.0, alpha=0.07, zorder=2)
            ax.plot(X, Y, Z, color=c, lw=1.05, alpha=0.95, zorder=3)
    # Eje del campo
    ax.plot([-3.4, 3.4], [0, 0], [0, 0], color="#f4f4f4" if oscuro else "#202020",
            lw=1.8, alpha=0.95, zorder=4)

    # Esfera dieléctrica: vidrio translúcido sombreado, por encima del plano
    u, v = np.mgrid[0:2 * np.pi:160j, 0:np.pi:80j]
    xs, ys, zs = np.cos(v), np.sin(v) * np.cos(u), np.sin(v) * np.sin(u)
    lx, ly, lz = -0.35, -0.55, 0.76
    luz = np.clip(lx * xs + ly * ys + lz * zs, -1, 1)
    base = np.array([0.55, 0.66, 1.0]) if oscuro else np.array([0.42, 0.52, 0.92])
    cara = np.zeros(xs.shape + (4,))
    brillo = 0.30 + 0.55 * (luz + 1) / 2 + 0.35 * np.clip(luz, 0, 1) ** 12
    cara[..., :3] = np.clip(base[None, None, :] * brillo[..., None] + 0.08, 0, 1)
    cara[..., 3] = (0.10 + 0.22 * (1 - np.abs(luz))) if oscuro else (0.04 + 0.13 * (1 - np.abs(luz)))
    ax.plot_surface(xs, ys, zs, facecolors=cara, linewidth=0, antialiased=True,
                    shade=False, zorder=5)
    t = np.linspace(0, 2 * np.pi, 300)
    ax.plot(np.cos(t), np.sin(t), 0 * t, color="#ffffff" if oscuro else "#2a2f45",
            lw=0.8, alpha=0.55, zorder=6)

    ax.set_xlim(-3.0, 3.0); ax.set_ylim(-2.3, 2.3); ax.set_zlim(-1.2, 1.2)
    ax.set_box_aspect((6.0, 4.6, 2.4))
    ax.view_init(elev=32, azim=-62)
    ruta = os.path.join(IMG, "portada-%s.png" % modo)
    fig.savefig(ruta, transparent=True, dpi=220)
    plt.close(fig)
    # Recorte de márgenes transparentes
    from PIL import Image
    im = Image.open(ruta)
    im.crop(im.getbbox()).save(ruta)
    print("  ->", ruta, im.crop(im.getbbox()).size)


if __name__ == "__main__":
    render("oscuro")
    render("claro")
