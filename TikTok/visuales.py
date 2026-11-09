# -*- coding: utf-8 -*-
r"""
Visuales (matplotlib -> capas RGBA) de los edits.  Las líneas de campo son
exactas: curvas de nivel de la función de flujo de Stokes, como en los apuntes.
Las funciones sin argumentos están en caché (se dibujan una vez por proceso);
las de la intro reciben el progreso p en [0, 1].
"""
from functools import lru_cache
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from motor import figura, capa, linea_brillo, HEX
import matplotlib as mpl
import matplotlib.font_manager as fm

for _f in ("lmroman10-regular.otf", "lmroman10-italic.otf", "lmroman10-bold.otf"):
    fm.fontManager.addfont("/usr/share/texmf/fonts/opentype/public/lm/" + _f)
mpl.rcParams.update({"font.family": "Latin Modern Roman", "mathtext.fontset": "cm",
                     "axes.unicode_minus": False})

VW, VH = 960, 640                 # tamaño estándar de los visuales del drop A
GLOW = LinearSegmentedColormap.from_list(
    "glow", ["#000000", "#07061a", "#1a1442", "#3a2d7a", "#6f5fa8", "#20b4ce", "#c9f4fb"])


# ----------------------------------------------------------------- utilidades
def contornos(X, Y, Z, niveles):
    fig, ax = plt.subplots()
    cs = ax.contour(X, Y, Z, levels=niveles)
    segs = [s for nivel in cs.allsegs for s in nivel if len(s) > 2]
    plt.close(fig)
    return segs


def campo_cargas(cargas, x, y):
    Ex = np.zeros_like(x, dtype=float); Ey = np.zeros_like(x, dtype=float)
    for q, x0, y0 in cargas:
        dx, dy = x - x0, y - y0
        r3 = np.maximum(np.hypot(dx, dy), 1e-3) ** 3
        Ex += q * dx / r3; Ey += q * dy / r3
    return Ex, Ey


def lineas_eje(cargas, xm, ym, niveles, r0=0.12):
    """Líneas de campo de cargas sobre el eje x (función de flujo exacta)."""
    x = np.linspace(-xm, xm, 900); y = np.linspace(1e-4, ym, 420)
    X, Y = np.meshgrid(x, y)
    psi = sum(q * (X - x0) / np.hypot(X - x0, Y) for q, x0, _ in cargas)
    segs = contornos(X, Y, psi, niveles)
    out = []
    for s in segs:
        lejos = np.ones(len(s), bool)
        for _, x0, _ in cargas:
            lejos &= np.hypot(s[:, 0] - x0, s[:, 1]) > r0
        cur = []
        for p, b in zip(s, lejos):
            if b:
                cur.append(p)
            elif len(cur) > 2:
                out.append(np.array(cur)); cur = []
            else:
                cur = []
        if len(cur) > 2:
            out.append(np.array(cur))
    return out + [np.c_[s[:, 0], -s[:, 1]] for s in out]


def carga(ax, x, y, signo, r=0.075):
    col = HEX["rojo"] if signo > 0 else HEX["azul"]
    for k, a in ((5, 0.06), (3, 0.12), (1.8, 0.25)):
        ax.add_patch(plt.Circle((x, y), r * k, color=col, alpha=a, lw=0))
    ax.add_patch(plt.Circle((x, y), r, color=col, lw=0))


def mapa_energia(ax, cargas, xm, ym, vmin=-2.2, vmax=2.4):
    x = np.linspace(-xm, xm, 700); y = np.linspace(-ym, ym, int(700 * ym / xm))
    X, Y = np.meshgrid(x, y)
    Ex, Ey = campo_cargas(cargas, X, Y)
    u = np.log10(np.maximum(Ex ** 2 + Ey ** 2, 1e-8))
    ax.imshow(u, extent=(-xm, xm, -ym, ym), origin="lower", cmap=GLOW,
              norm=Normalize(vmin, vmax, clip=True), interpolation="bilinear", alpha=0.95)


# =================================================================== EDIT 1
def v1_intro(p):
    """q1 fija; q2 llega desde el infinito (arriba) por una curva, dejando estela."""
    xm, ym = 2.5, 1.75
    fig, ax = figura(VW, VH, (-xm, xm), (-ym, ym))
    for a in np.linspace(0, 2 * np.pi, 16, endpoint=False):
        r = np.linspace(0.18, 2.6, 2)
        ax.plot(-0.7 + r * np.cos(a), -0.35 + r * np.sin(a), color=HEX["cian"], lw=1.0, alpha=0.18)
    carga(ax, -0.7, -0.35, +1)
    s = np.linspace(0, 1, 200)
    cx = 2.4 - 1.6 * s - 0.4 * np.sin(np.pi * s)
    cy = 2.2 - 2.0 * s ** 0.9
    k = max(2, int(p * len(s)))
    linea_brillo(ax, cx[:k], cy[:k], HEX["ambar"], lw=2.0, brillo=0.15, linestyle=(0, (4, 3)))
    carga(ax, cx[k - 1], cy[k - 1], +1)
    ax.text(-0.7, -0.75, r"$q_1$", color=HEX["texto"], fontsize=26, ha="center", va="top")
    ax.text(cx[k - 1] + 0.18, cy[k - 1] + 0.05, r"$q_2$", color=HEX["texto"], fontsize=26, ha="left", va="bottom")
    if p > 0.95:
        ax.text(0.15, -1.45, r"$W=q_2\,\phi_1$", color=HEX["ambar"], fontsize=30, ha="center")
    return capa(fig, 70)


@lru_cache(None)
def v1_opuestas():
    xm, ym = 2.5, 1.75
    fig, ax = figura(VW, VH, (-xm, xm), (-ym, ym))
    cargas = [(1, -0.9, 0), (-1, 0.9, 0)]
    mapa_energia(ax, cargas, xm, ym)
    for s in lineas_eje(cargas, 3.2, 2.4, np.linspace(0.1, 1.9, 12)):
        ax.plot(s[:, 0], s[:, 1], color=HEX["cian"], lw=1.1, alpha=0.85)
    ax.plot([-0.8, 0.8], [0, 0], color=HEX["cian"], lw=1.1, alpha=0.85)
    carga(ax, -0.9, 0, +1); carga(ax, 0.9, 0, -1)
    return capa(fig, 70)


@lru_cache(None)
def v1_iguales():
    xm, ym = 2.5, 1.75
    fig, ax = figura(VW, VH, (-xm, xm), (-ym, ym))
    cargas = [(1, -0.9, 0), (1, 0.9, 0)]
    mapa_energia(ax, cargas, xm, ym)
    niv = [v for v in np.linspace(-1.9, 1.9, 15) if abs(abs(v) - 2) > 0.05]
    for s in lineas_eje(cargas, 3.2, 2.4, niv):
        ax.plot(s[:, 0], s[:, 1], color=HEX["violeta"], lw=1.1, alpha=0.85)
    carga(ax, -0.9, 0, +1); carga(ax, 0.9, 0, +1)
    return capa(fig, 70)


@lru_cache(None)
def v1_esfera():
    """Esfera uniformemente cargada: densidad de energía (r^2 dentro, r^-4 fuera)."""
    xm, ym = 2.5, 1.75
    fig, ax = figura(VW, VH, (-xm, xm), (-ym, ym))
    a = 0.6
    x = np.linspace(-xm, xm, 700); y = np.linspace(-ym, ym, 490)
    X, Y = np.meshgrid(x, y); R = np.hypot(X, Y) / a
    u = np.where(R < 1, R ** 2, R ** -4.0)
    ax.imshow(np.log10(np.maximum(u, 1e-4)), extent=(-xm, xm, -ym, ym), origin="lower", cmap=GLOW,
              norm=Normalize(-3.2, 0.1), interpolation="bilinear")
    t = np.linspace(0, 2 * np.pi, 300)
    ax.plot(a * np.cos(t), a * np.sin(t), color=HEX["texto"], lw=1.2, alpha=0.8)
    ax.plot(2 * a * np.cos(t), 2 * a * np.sin(t), color=HEX["oro"], lw=1.4, alpha=0.9, dashes=(5, 4))
    ax.text(2 * a * 0.72 + 0.12, 2 * a * 0.72 + 0.08, r"$r=2a$", color=HEX["oro"], fontsize=24, ha="left", va="bottom")
    ax.text(0, -0.08, r"$\rho$", color=HEX["texto"], fontsize=28, ha="center", va="center")
    return capa(fig, 70)


@lru_cache(None)
def v1_dUdr():
    """Energía por unidad de radio de la esfera: r^4 dentro, r^-2 fuera; áreas 1/6 y 5/6."""
    fig = plt.figure(figsize=(VW / 100, VH / 100), dpi=100)
    fig.patch.set_alpha(0)
    ax = fig.add_axes([0.1, 0.16, 0.85, 0.78]); ax.set_facecolor((0, 0, 0, 0))
    r1 = np.linspace(0, 1, 100); r2 = np.linspace(1, 4, 200)
    ax.fill_between(r1, r1 ** 4, color=HEX["violeta"], alpha=0.35, lw=0)
    ax.fill_between(r2, r2 ** -2, color=HEX["cian"], alpha=0.25, lw=0)
    linea_brillo(ax, r1, r1 ** 4, HEX["violeta"], lw=2.4)
    linea_brillo(ax, r2, r2 ** -2, HEX["cian"], lw=2.4)
    ax.text(0.72, 0.12, r"$\frac{1}{6}$", color=HEX["texto"], fontsize=34, ha="center")
    ax.text(1.9, 0.12, r"$\frac{5}{6}$", color=HEX["texto"], fontsize=34, ha="center")
    ax.set_xlim(0, 4); ax.set_ylim(0, 1.15)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(HEX["tenue"])
    ax.tick_params(colors=HEX["tenue"], labelsize=16)
    ax.set_xlabel(r"$r/a$", color=HEX["texto"], fontsize=24)
    ax.set_ylabel(r"$\mathrm{d}U_e/\mathrm{d}r$", color=HEX["texto"], fontsize=24)
    return capa(fig, 20)


# =================================================================== EDIT 2 · Earnshaw y fuerzas
def _phi_silla(x, z):
    """Cuatro cargas +q en (±1, ±1, 0): potencial en el plano y = 0 (unidades q/4πε0a)."""
    return 2 / np.sqrt((x - 1) ** 2 + 1 + z ** 2) + 2 / np.sqrt((x + 1) ** 2 + 1 + z ** 2)


def _silla(azim, elev=26, w=VW, h=VH, bola=True):
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    fig = plt.figure(figsize=(w / 100, h / 100), dpi=100)
    fig.patch.set_alpha(0)
    ax = fig.add_axes([-0.12, -0.18, 1.24, 1.36], projection="3d")
    ax.set_facecolor((0, 0, 0, 0)); ax.set_axis_off()
    x = np.linspace(-0.8, 0.8, 60); z = np.linspace(-0.8, 0.8, 60)
    X, Z = np.meshgrid(x, z); P = _phi_silla(X, Z)
    cm = LinearSegmentedColormap.from_list("s", [HEX["violeta"], HEX["cian"], "#d9fbff"])
    ax.plot_surface(X, Z, P, cmap=cm, rstride=2, cstride=2, linewidth=0.25, edgecolor=(1, 1, 1, 0.18),
                    antialiased=True, alpha=0.92)
    ax.plot(x, 0 * x, _phi_silla(x, 0 * x), color=HEX["cian"], lw=2.4, zorder=5)
    ax.plot(0 * z, z, _phi_silla(0 * z, z), color=HEX["violeta"], lw=2.4, zorder=5)
    if bola:
        ax.scatter([0], [0], [_phi_silla(0, 0) + 0.015], s=160, color=HEX["rojo"], depthshade=False, zorder=10)
    ax.view_init(elev=elev, azim=azim)
    ax.set_box_aspect((1, 1, 0.6))
    return capa(fig, 60)


def v2_intro(p):
    return _silla(-60 + 70 * p)


@lru_cache(None)
def v2_silla():
    return _silla(-35, 30)


@lru_cache(None)
def v2_perfiles():
    fig = plt.figure(figsize=(VW / 100, VH / 100), dpi=100)
    fig.patch.set_alpha(0)
    ax = fig.add_axes([0.13, 0.17, 0.82, 0.75]); ax.set_facecolor((0, 0, 0, 0))
    s = np.linspace(-0.8, 0.8, 200)
    linea_brillo(ax, s, _phi_silla(s, 0 * s), HEX["cian"], lw=3)
    linea_brillo(ax, s, _phi_silla(0 * s, s), HEX["violeta"], lw=3)
    ax.scatter([0], [_phi_silla(0, 0)], s=120, color=HEX["rojo"], zorder=5)
    ax.text(0, 3.0, "según $x$: mínimo", color=HEX["cian"], fontsize=24, ha="center")
    ax.text(0, 2.58, "según $z$: máximo", color=HEX["violeta"], fontsize=24, ha="center")
    ax.set_ylim(2.45, 3.12); ax.set_xlim(-0.8, 0.8)
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)
    for k in ("left", "bottom"):
        ax.spines[k].set_color(HEX["tenue"])
    ax.tick_params(colors=HEX["tenue"], labelsize=18)
    ax.set_xlabel("desplazamiento", color=HEX["texto"], fontsize=24)
    ax.set_ylabel(r"$\phi$", color=HEX["texto"], fontsize=28)
    return capa(fig, 20)


@lru_cache(None)
def v2_placas():
    xm, ym = 2.5, 1.66
    fig, ax = figura(VW, VH, (-xm, xm), (-ym, ym))
    for y0, sg in ((0.75, +1), (-0.75, -1)):
        ax.add_patch(plt.Rectangle((-1.9, y0 - 0.06 if sg > 0 else y0 - 0.06), 3.8, 0.12,
                                   color="#5c6370", lw=0))
        for x0 in np.linspace(-1.7, 1.7, 9):
            ax.text(x0, y0 + 0.2 * sg, "+" if sg > 0 else "−", color=HEX["rojo"] if sg > 0 else HEX["azul"],
                    fontsize=20, ha="center", va="center")
    for x0 in np.linspace(-1.5, 1.5, 7):
        linea_brillo(ax, [x0, x0], [0.66, -0.66], HEX["cian"], lw=1.6, brillo=0.12)
        ax.annotate("", (x0, -0.1), (x0, 0.05), arrowprops=dict(arrowstyle="-|>", color=HEX["cian"], lw=1.4))
    for y0, d in ((1.0, -1), (-1.0, 1)):
        ax.annotate("", (2.2, y0 + 0.45 * d), (2.2, y0), arrowprops=dict(arrowstyle="-|>", color=HEX["violeta"], lw=3, mutation_scale=28))
    ax.text(2.2, 1.18, r"$\vec F$", color=HEX["violeta"], fontsize=28, ha="center")
    ax.text(-2.25, 0, r"$d$", color=HEX["texto"], fontsize=28, ha="center", va="center")
    ax.annotate("", (-2.05, 0.69), (-2.05, -0.69), arrowprops=dict(arrowstyle="<->", color=HEX["tenue"], lw=1.2))
    return capa(fig, 60)


# =================================================================== EDIT 3 · Dieléctricos
def v3_intro(p):
    xm, ym = 2.5, 1.66
    fig, ax = figura(VW, VH, (-xm, xm), (-ym, ym))
    for k, a in ((1.0, 0.22), (0.8, 0.22), (0.6, 0.2), (0.4, 0.2)):
        ax.add_patch(plt.Circle((0, -0.15), k, color=HEX["cian"], alpha=a * 0.6, lw=0))
    ax.add_patch(plt.Circle((0, -0.15), 1.0, fill=False, ec=HEX["cian"], lw=1.4, alpha=0.8))
    d = 0.42 * p
    carga(ax, d, -0.15, +1, r=0.07)
    ax.text(-0.55, 0.5, r"$-q$", color=HEX["texto"], fontsize=26, ha="center")
    ax.text(d, -0.42, r"$+q$", color=HEX["texto"], fontsize=24, ha="center", va="top")
    L = 2.6 * p
    if L > 0.05:
        ax.annotate("", (-1.3 + L, 1.35), (-1.3, 1.35), arrowprops=dict(arrowstyle="-|>", color=HEX["cian"], lw=3, mutation_scale=30))
        ax.text(-1.3 + L + 0.12, 1.35, r"$\vec E$", color=HEX["cian"], fontsize=30, va="center")
    if p > 0.4:
        ax.annotate("", (d, -0.15), (0, -0.15), arrowprops=dict(arrowstyle="-|>", color=HEX["ambar"], lw=3, mutation_scale=24))
        ax.text(d / 2, 0.02, r"$\vec p$", color=HEX["ambar"], fontsize=28, ha="center", va="bottom")
    return capa(fig, 60)


@lru_cache(None)
def v3_red():
    xm, ym = 2.5, 1.66
    fig, ax = figura(VW, VH, (-xm, xm), (-ym, ym))
    ax.add_patch(plt.Rectangle((-1.8, -1.1), 3.6, 2.2, color="#1c2433", lw=0))
    ax.add_patch(plt.Rectangle((-1.8, -1.1), 3.6, 2.2, fill=False, ec=HEX["texto"], lw=1.2, alpha=0.7))
    for i in range(6):
        for j in range(4):
            x0, y0 = -1.5 + 0.6 * i, -0.8 + 0.53 * j
            ax.annotate("", (x0 + 0.38, y0), (x0 - 0.0, y0), arrowprops=dict(arrowstyle="-|>", color=HEX["ambar"], lw=2, mutation_scale=16))
    for j in range(5):
        y0 = -0.9 + 0.45 * j
        ax.text(-2.0, y0, "−", color=HEX["azul"], fontsize=26, ha="center", va="center")
        ax.text(2.0, y0, "+", color=HEX["rojo"], fontsize=26, ha="center", va="center")
    ax.text(0, 1.32, r"$\vec P$ uniforme $\Rightarrow\ \rho_P=0,\ \ \sigma_P=\vec P\cdot\hat n$", color=HEX["texto"], fontsize=22, ha="center")
    return capa(fig, 60)


def _lineas_esfera(er, campo="E"):
    beta = (er - 1) / (er + 2)
    xm, ym = 2.6, 1.8
    x = np.linspace(-xm, xm, 700); y = np.linspace(1e-4, ym, 260)
    X, Y = np.meshgrid(x, y); R = np.hypot(X, Y)
    fuera = R > 1
    pout = 0.5 * Y ** 2 + beta * Y ** 2 / np.maximum(R, 1e-6) ** 3
    k_in = 3 / (er + 2) * (er if campo == "D" else 1)
    pin = 0.5 * Y ** 2 * k_in
    niv = [0.5 * h ** 2 for h in np.arange(0.18, 1.85, 0.2)]
    if campo == "D" or er == 1:
        Z = np.where(fuera, pout, pin)
        segs = contornos(X, Y, Z, niv)
    else:
        segs = contornos(X, Y, np.ma.masked_where(~fuera, pout), niv) + \
            contornos(X, Y, np.ma.masked_where(fuera, pin), niv)
    return segs + [np.c_[s[:, 0], -s[:, 1]] for s in segs]


@lru_cache(None)
def v3_esfera(er=4, campo="E"):
    xm, ym = 2.5, 1.66
    fig, ax = figura(VW, VH, (-xm, xm), (-ym, ym))
    ax.add_patch(plt.Circle((0, 0), 1, color="#2a2350", alpha=0.9, lw=0))
    col = HEX["cian"] if campo == "E" else HEX["violeta"]
    for s in _lineas_esfera(er, campo):
        ax.plot(s[:, 0], s[:, 1], color=col, lw=1.3, alpha=0.9)
    ax.plot([-xm, xm], [0, 0], color=col, lw=1.3, alpha=0.9)
    ax.add_patch(plt.Circle((0, 0), 1, fill=False, ec=HEX["texto"], lw=1.4))
    if campo == "E" and er > 1:
        for a in np.radians([-60, -30, 0, 30, 60]):
            ax.text(1.17 * np.cos(a), 1.17 * np.sin(a), "+", color=HEX["rojo"], fontsize=20, ha="center", va="center")
            ax.text(-1.17 * np.cos(a), 1.17 * np.sin(a), "−", color=HEX["azul"], fontsize=20, ha="center", va="center")
    ax.text(0, -1.5, r"$\varepsilon_{r}=%g$" % er, color=HEX["texto"], fontsize=28, ha="center",
            bbox=dict(fc="#000000", ec="none", pad=3))
    return capa(fig, 60)


def v3_e1():
    return v3_esfera(1, "E")


def v3_e4():
    return v3_esfera(4, "E")


def v3_e20():
    return v3_esfera(20, "E")


def v3_d4():
    return v3_esfera(4, "D")


# =================================================================== EDIT 4 · Cavidades
def _medio(ax, xm, ym):
    ax.add_patch(plt.Rectangle((-2.3, -1.45), 4.6, 2.9, color="#1c1a3a", lw=0))
    for c in np.linspace(-5, 5, 34):
        ax.plot([c - 1.5, c + 1.5], [-1.45, 1.45], color=HEX["violeta"], lw=0.6, alpha=0.18)
    for yy in (1.15, -1.15):
        ax.annotate("", (-0.9, yy), (-2.0, yy), arrowprops=dict(arrowstyle="-|>", color=HEX["cian"], lw=2.2, mutation_scale=20))
    ax.text(-1.45, 1.15 + 0.12, r"$\vec E_d$", color=HEX["cian"], fontsize=24, ha="center", va="bottom")


def N_esferoide(m):
    """Factor de despolarización (eje de revolución paralelo al campo); m = c/a."""
    if abs(m - 1) < 1e-6:
        return 1 / 3
    if m > 1:
        e = np.sqrt(1 - 1 / m ** 2)
        return (1 - e ** 2) / e ** 3 * (np.arctanh(e) - e)
    e = np.sqrt(1 / m ** 2 - 1)
    return (1 + e ** 2) / e ** 3 * (e - np.arctan(e))


def _cavidad(m, etiqueta=True):
    xm, ym = 2.5, 1.66
    fig, ax = figura(VW, VH, (-xm, xm), (-ym, ym))
    _medio(ax, xm, ym)
    # esferoide de volumen constante: c = semieje según x, a = transversal
    c = 0.75 * m ** (2 / 3); a = 0.75 * m ** (-1 / 3)
    c, a = min(c, 1.9), min(a, 1.2)
    t = np.linspace(0, 2 * np.pi, 300)
    ax.fill(c * np.cos(t), a * np.sin(t), color="#000000", lw=0)
    ax.plot(c * np.cos(t), a * np.sin(t), color=HEX["texto"], lw=1.4)
    N = N_esferoide(m)
    Lc = 0.7 * (1 + 1.4 * N)
    ax.annotate("", (Lc / 2, 0), (-Lc / 2, 0), arrowprops=dict(arrowstyle="-|>", color=HEX["oro"], lw=3, mutation_scale=24))
    if etiqueta:
        ax.text(0, -1.38, r"$N=%.2f$" % N, color=HEX["oro"], fontsize=26, ha="center", va="bottom",
                bbox=dict(fc="#000000", ec="none", pad=2))
    return capa(fig, 50)


def v4_intro(p):
    m = 10 ** (1.4 - 2.8 * p)          # de aguja (m ≈ 25) a lenteja (m ≈ 0,04)
    return _cavidad(m)


@lru_cache(None)
def v4_aguja():
    return _cavidad(25)


@lru_cache(None)
def v4_lenteja():
    return _cavidad(0.04)


@lru_cache(None)
def v4_esfera():
    return _cavidad(1.0)


@lru_cache(None)
def v4_curva():
    fig = plt.figure(figsize=(VW / 100, VH / 100), dpi=100)
    fig.patch.set_alpha(0)
    ax = fig.add_axes([0.12, 0.17, 0.84, 0.75]); ax.set_facecolor((0, 0, 0, 0))
    ms = np.logspace(-2, 2, 300); Ns = [N_esferoide(m) for m in ms]
    linea_brillo(ax, ms, Ns, HEX["cian"], lw=3)
    for m, txt, col in ((0.02, "lenteja", HEX["violeta"]), (1, "esfera", HEX["oro"]), (30, "aguja", HEX["cian"])):
        ax.scatter([m], [N_esferoide(m)], s=110, color=col, zorder=5)
        ax.text(m, N_esferoide(m) + 0.09, txt, color=col, fontsize=22, ha="center")
    ax.set_xscale("log"); ax.set_ylim(0, 1.15); ax.set_xlim(0.01, 100)
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)
    for k in ("left", "bottom"):
        ax.spines[k].set_color(HEX["tenue"])
    ax.tick_params(colors=HEX["tenue"], labelsize=18)
    ax.set_xlabel(r"forma $m=c/a$", color=HEX["texto"], fontsize=24)
    ax.set_ylabel(r"$N$", color=HEX["texto"], fontsize=28)
    return capa(fig, 20)
