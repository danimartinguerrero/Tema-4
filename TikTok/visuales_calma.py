# -*- coding: utf-8 -*-
r"""
Visuales que evolucionan de forma continua para los edits tranquilos.
Cada función recibe p en [0, 1] (progreso dentro del capítulo) y devuelve una capa RGBA.
"""
from functools import lru_cache
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from motor import figura, capa, linea_brillo, HEX
import visuales as V                     # reutiliza fuentes, cargas, mapas y geometrías

CW, CH = 980, 720
XM, YM = 2.5, 2.5 * CH / CW


def _fig():
    return figura(CW, CH, (-XM, XM), (-YM, YM))


def _texto(ax, x, y, s, col="texto", fs=26, **kw):
    ax.text(x, y, s, color=HEX[col], fontsize=fs, ha="center", va="center",
            bbox=dict(fc="#000000", ec="none", pad=3, alpha=0.75), **kw)


# =================================================================== energía
def c1_llegada(p):
    """La segunda carga llega desde el infinito; el trabajo crece con ella."""
    fig, ax = _fig()
    for a in np.linspace(0, 2 * np.pi, 18, endpoint=False):
        r = np.linspace(0.2, 3.2, 2)
        ax.plot(-0.8 + r * np.cos(a), -0.3 + r * np.sin(a), color=HEX["cian"], lw=1.0, alpha=0.14)
    V.carga(ax, -0.8, -0.3, +1)
    s = np.linspace(0, 1, 240)
    cx = 2.3 - 1.7 * s - 0.35 * np.sin(np.pi * s); cy = 1.9 - 1.9 * s ** 0.9
    k = max(2, int(p * len(s)))
    linea_brillo(ax, cx[:k], cy[:k], HEX["ambar"], lw=1.8, brillo=0.12, linestyle=(0, (4, 3)))
    V.carga(ax, cx[k - 1], cy[k - 1], +1)
    d = np.hypot(cx[k - 1] + 0.8, cy[k - 1] + 0.3)
    _texto(ax, 0, -1.55, r"$W=q_2\,\phi_1=\frac{k\,q_1q_2}{r}$" + "     " + r"$r=%.2f$" % d, "ambar", 24)
    return capa(fig, 70)


def c1_dos(p):
    """Dos cargas opuestas que se separan despacio: densidad de energía y líneas de campo."""
    sep = 0.55 + 0.55 * p
    fig, ax = _fig()
    cargas = [(1, -sep, 0), (-1, sep, 0)]
    V.mapa_energia(ax, cargas, XM, YM)
    for s in V.lineas_eje(cargas, 3.4, 2.4, np.linspace(0.1, 1.9, 12)):
        ax.plot(s[:, 0], s[:, 1], color=HEX["cian"], lw=1.0, alpha=0.8)
    ax.plot([-sep + 0.12, sep - 0.12], [0, 0], color=HEX["cian"], lw=1.0, alpha=0.8)
    V.carga(ax, -sep, 0, +1); V.carga(ax, sep, 0, -1)
    return capa(fig, 80)


@lru_cache(None)
def _esfera_base():
    a = 0.55
    x = np.linspace(-XM, XM, 700); y = np.linspace(-YM, YM, int(700 * YM / XM))
    X, Y = np.meshgrid(x, y); R = np.hypot(X, Y) / a
    return np.log10(np.maximum(np.where(R < 1, R ** 2, R ** -4.0), 1e-4)), a


def c1_esfera(p):
    """Esfera uniformemente cargada; un casquete de radio r barre el exterior y
    muestra qué fracción de la energía queda fuera: U(>r)/U = 5a/(6r)."""
    u, a = _esfera_base()
    fig, ax = _fig()
    ax.imshow(u, extent=(-XM, XM, -YM, YM), origin="lower", cmap=V.GLOW, norm=Normalize(-3.2, 0.1),
              interpolation="bilinear")
    t = np.linspace(0, 2 * np.pi, 300)
    ax.plot(a * np.cos(t), a * np.sin(t), color=HEX["texto"], lw=1.1, alpha=0.8)
    r = a * (1 + 2.1 * p)
    linea_brillo(ax, r * np.cos(t), r * np.sin(t), HEX["oro"], lw=1.6, brillo=0.12)
    frac = 5 / 6 * a / r
    _texto(ax, 0, -YM + 0.32, r"energía fuera de $r$:  $%d\,\%%$" % round(100 * frac), "oro", 26)
    return capa(fig, 70)


@lru_cache(None)
def _cruzado():
    x = np.linspace(-XM, XM, 700); y = np.linspace(-YM, YM, int(700 * YM / XM))
    X, Y = np.meshgrid(x, y)
    E1 = V.campo_cargas([(1, -0.8, 0)], X, Y); E2 = V.campo_cargas([(1, 0.8, 0)], X, Y)
    c = E1[0] * E2[0] + E1[1] * E2[1]
    return np.sign(c) * np.log10(1 + np.abs(c) / 0.02)


def c1_cruzado(p):
    s = _cruzado()
    fig, ax = _fig()
    div = LinearSegmentedColormap.from_list("d", [HEX["azul"], "#000000", HEX["rojo"]])
    ax.imshow(s * (0.55 + 0.45 * p), extent=(-XM, XM, -YM, YM), origin="lower", cmap=div,
              norm=Normalize(-3.2, 3.2), interpolation="bilinear")
    t = np.linspace(0, 2 * np.pi, 200)
    ax.plot(0.8 * np.cos(t), 0.8 * np.sin(t), color=HEX["tenue"], lw=1.0, dashes=(4, 3))
    V.carga(ax, -0.8, 0, +1); V.carga(ax, 0.8, 0, +1)
    _texto(ax, 0, -YM + 0.32, r"$\varepsilon_0\,\vec E_1\cdot\vec E_2$", "texto", 28)
    return capa(fig, 80)


# =================================================================== Earnshaw y fuerzas
def c2_silla(p):
    return V._silla(-70 + 110 * p, 24 + 8 * np.sin(np.pi * p), w=CW, h=CH)


def c2_perfiles(p):
    """Cortes por el centro y una bola que, en la dirección inestable, se escapa."""
    fig = plt.figure(figsize=(CW / 100, CH / 100), dpi=100)
    fig.patch.set_alpha(0)
    ax = fig.add_axes([0.12, 0.16, 0.84, 0.76]); ax.set_facecolor((0, 0, 0, 0))
    s = np.linspace(-0.8, 0.8, 300)
    linea_brillo(ax, s, V._phi_silla(s, 0 * s), HEX["cian"], lw=3)
    linea_brillo(ax, s, V._phi_silla(0 * s, s), HEX["violeta"], lw=3)
    z = 0.78 * p ** 1.8
    ax.scatter([z], [V._phi_silla(0, z)], s=170, color=HEX["rojo"], zorder=5)
    ax.text(0, 3.0, "según $x$: el potencial sube", color=HEX["cian"], fontsize=24, ha="center")
    ax.text(0, 2.58, "según $z$: el potencial baja", color=HEX["violeta"], fontsize=24, ha="center")
    ax.set_ylim(2.45, 3.12); ax.set_xlim(-0.8, 0.8)
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)
    for k in ("left", "bottom"):
        ax.spines[k].set_color(HEX["tenue"])
    ax.tick_params(colors=HEX["tenue"], labelsize=18)
    ax.set_xlabel("desplazamiento", color=HEX["texto"], fontsize=24)
    ax.set_ylabel(r"$\phi$", color=HEX["texto"], fontsize=28)
    return capa(fig, 20)


def c2_placas(p):
    """Placas con carga fija que se acercan: la energía Q²x/(2ε₀S) disminuye."""
    h = 0.95 - 0.45 * p
    fig, ax = _fig()
    for y0, sg in ((h, +1), (-h, -1)):
        ax.add_patch(plt.Rectangle((-1.9, y0 - 0.06), 3.8, 0.12, color="#5c6370", lw=0))
        for x0 in np.linspace(-1.7, 1.7, 9):
            ax.text(x0, y0 + 0.2 * sg, "+" if sg > 0 else "−", color=HEX["rojo"] if sg > 0 else HEX["azul"],
                    fontsize=20, ha="center", va="center")
    for x0 in np.linspace(-1.5, 1.5, 7):
        linea_brillo(ax, [x0, x0], [h - 0.09, -h + 0.09], HEX["cian"], lw=1.4, brillo=0.1)
    for y0, dd in ((h + 0.25, -1), (-h - 0.25, 1)):
        ax.annotate("", (2.25, y0 + 0.4 * dd), (2.25, y0),
                    arrowprops=dict(arrowstyle="-|>", color=HEX["violeta"], lw=2.6, mutation_scale=26))
    _texto(ax, 0, -YM + 0.3, r"$U_e=\frac{Q^2x}{2\varepsilon_0 S}$" + "    " + r"$x=%.2f$" % (2 * h), "texto", 26)
    return capa(fig, 70)


def c2_coaxial(p):
    """Condensador cilíndrico (corte longitudinal): el cilindro interior entra con fuerza constante."""
    fig, ax = _fig()
    ax.add_patch(plt.Rectangle((-2.2, -0.9), 3.2, 1.8, color="#1c2433", lw=0))
    ax.plot([1.0, -2.2, -2.2, 1.0], [0.9, 0.9, -0.9, -0.9], color=HEX["texto"], lw=1.3)
    xi = 0.75 - 1.75 * p                                   # extremo izquierdo del cilindro interior
    Li = 1.6
    ax.add_patch(plt.Rectangle((xi, -0.38), Li, 0.76, color="#5c6370", lw=0))
    ax.add_patch(plt.Rectangle((xi, -0.38), Li, 0.76, fill=False, ec=HEX["texto"], lw=1.2))
    for xx in np.arange(xi + 0.12, min(1.0, xi + Li), 0.22):
        ax.plot([xx, xx], [0.42, 0.86], color=HEX["cian"], lw=1.0, alpha=0.8)
        ax.plot([xx, xx], [-0.42, -0.86], color=HEX["cian"], lw=1.0, alpha=0.8)
    ax.annotate("", (xi + Li - 0.15 - 0.55, -1.25), (xi + Li - 0.15, -1.25),
                arrowprops=dict(arrowstyle="-|>", color=HEX["violeta"], lw=3, mutation_scale=26))
    ax.text(xi + Li - 0.42, -1.05, r"$F$", color=HEX["violeta"], fontsize=26, ha="center")
    _texto(ax, 0, YM - 0.3, r"$F=\frac{\pi\varepsilon_0V_0^{2}}{\ln(R_1/R_2)}$,  constante", "texto", 24)
    return capa(fig, 60)


# =================================================================== dieléctricos
def c3_atomo(p):
    """El núcleo se separa del centro de la nube a medida que crece el campo."""
    fig, ax = _fig()
    for k, al in ((1.0, 0.13), (0.8, 0.13), (0.6, 0.12), (0.4, 0.12)):
        ax.add_patch(plt.Circle((0, -0.2), k, color=HEX["cian"], alpha=al, lw=0))
    ax.add_patch(plt.Circle((0, -0.2), 1.0, fill=False, ec=HEX["cian"], lw=1.3, alpha=0.8))
    d = 0.42 * p
    V.carga(ax, d, -0.2, +1, r=0.07)
    ax.text(-0.6, 0.45, r"$-q$", color=HEX["texto"], fontsize=26, ha="center")
    L = 2.8 * p
    if L > 0.05:
        ax.annotate("", (-1.4 + L, 1.25), (-1.4, 1.25),
                    arrowprops=dict(arrowstyle="-|>", color=HEX["cian"], lw=3, mutation_scale=30))
        ax.text(-1.4 + L + 0.14, 1.25, r"$\vec E$", color=HEX["cian"], fontsize=30, va="center")
    if p > 0.3:
        ax.annotate("", (d, -0.2), (0, -0.2),
                    arrowprops=dict(arrowstyle="-|>", color=HEX["ambar"], lw=3, mutation_scale=22))
    _texto(ax, 0, -YM + 0.32, r"$d=%.2f\,a$     $p=q\,d$" % d, "ambar", 24)
    return capa(fig, 70)


def c3_red(p):
    fig, ax = _fig()
    ax.add_patch(plt.Rectangle((-1.8, -1.05), 3.6, 2.1, color="#1c2433", lw=0))
    ax.add_patch(plt.Rectangle((-1.8, -1.05), 3.6, 2.1, fill=False, ec=HEX["texto"], lw=1.2, alpha=0.7))
    L = 0.08 + 0.32 * p
    for i in range(6):
        for j in range(4):
            x0, y0 = -1.5 + 0.6 * i, -0.78 + 0.52 * j
            ax.annotate("", (x0 + L, y0), (x0, y0),
                        arrowprops=dict(arrowstyle="-|>", color=HEX["ambar"], lw=2, mutation_scale=16))
    for j in range(5):
        y0 = -0.88 + 0.44 * j
        ax.text(-2.0, y0, "−", color=HEX["azul"], fontsize=26, ha="center", va="center", alpha=p)
        ax.text(2.0, y0, "+", color=HEX["rojo"], fontsize=26, ha="center", va="center", alpha=p)
    _texto(ax, 0, -YM + 0.32, r"$\rho_P=0$  dentro,   $\sigma_P=\pm P$  en las caras", "texto", 24)
    return capa(fig, 60)


def c3_barrido(p):
    """Esfera dieléctrica: la permitividad crece de 1 a 20 y el campo interior se debilita."""
    er = 1 + 19 * p ** 1.6
    fig, ax = _fig()
    ax.add_patch(plt.Circle((0, 0), 1, color="#2a2350", alpha=0.6 + 0.35 * p, lw=0))
    for s in V._lineas_esfera(er, "E"):
        ax.plot(s[:, 0], s[:, 1], color=HEX["cian"], lw=1.2, alpha=0.9)
    ax.plot([-XM, XM], [0, 0], color=HEX["cian"], lw=1.2, alpha=0.9)
    ax.add_patch(plt.Circle((0, 0), 1, fill=False, ec=HEX["texto"], lw=1.3))
    _texto(ax, 0, -YM + 0.32, r"$\varepsilon_r=%.1f$     $E_{\mathrm{int}}/E_0=%.2f$" % (er, 3 / (er + 2)), "texto", 26)
    return capa(fig, 70)


@lru_cache(None)
def _lineasD():
    return V._lineas_esfera(4, "D")


def c3_D(p):
    """Líneas de D (continuas) que se dibujan poco a poco."""
    fig, ax = _fig()
    ax.add_patch(plt.Circle((0, 0), 1, color="#2a2350", alpha=0.9, lw=0))
    for s in _lineasD():
        k = max(2, int(len(s) * min(1, 0.05 + p * 1.05)))
        ax.plot(s[:k, 0], s[:k, 1], color=HEX["violeta"], lw=1.3, alpha=0.95)
    ax.plot([-XM, -XM + 2 * XM * min(1, 0.05 + 1.05 * p)], [0, 0], color=HEX["violeta"], lw=1.3)
    ax.add_patch(plt.Circle((0, 0), 1, fill=False, ec=HEX["texto"], lw=1.3))
    _texto(ax, 0, -YM + 0.32, r"líneas de $\vec D$:  sin principio ni fin sin carga libre", "texto", 24)
    return capa(fig, 70)


# =================================================================== cavidades
def _hueco(m, p_brillo=1.0):
    fig, ax = _fig()
    V._medio(ax, XM, YM)
    c = min(0.75 * m ** (2 / 3), 1.9); a = min(0.75 * m ** (-1 / 3), 1.2)
    t = np.linspace(0, 2 * np.pi, 300)
    ax.fill(c * np.cos(t), a * np.sin(t), color="#000000", lw=0)
    ax.plot(c * np.cos(t), a * np.sin(t), color=HEX["texto"], lw=1.4)
    N = V.N_esferoide(m)
    Lc = 0.7 * (1 + 1.4 * N)
    ax.annotate("", (Lc / 2, 0), (-Lc / 2, 0),
                arrowprops=dict(arrowstyle="-|>", color=HEX["oro"], lw=3, mutation_scale=24, alpha=p_brillo))
    _texto(ax, 0, -1.25, r"$N=%.2f$" % N, "oro", 26)
    return capa(fig, 60)


def c4_aguja(p):
    return _hueco(25, 0.6 + 0.4 * np.sin(np.pi * p))


def c4_lenteja(p):
    return _hueco(0.04, 0.6 + 0.4 * np.sin(np.pi * p))


def c4_morfo(p):
    return _hueco(10 ** (1.4 - 2.8 * p))


def c4_curva(p):
    fig = plt.figure(figsize=(CW / 100, CH / 100), dpi=100)
    fig.patch.set_alpha(0)
    ax = fig.add_axes([0.12, 0.16, 0.84, 0.76]); ax.set_facecolor((0, 0, 0, 0))
    ms = np.logspace(-2, 2, 300); Ns = [V.N_esferoide(m) for m in ms]
    linea_brillo(ax, ms, Ns, HEX["cian"], lw=3)
    m = 10 ** (1.8 - 3.6 * p)
    ax.scatter([m], [V.N_esferoide(m)], s=170, color=HEX["oro"], zorder=5)
    for mm, txt, col in ((0.02, "lenteja", HEX["violeta"]), (1, "esfera", HEX["oro"]), (30, "aguja", HEX["cian"])):
        ax.text(mm, V.N_esferoide(mm) + 0.1, txt, color=col, fontsize=22, ha="center")
    ax.set_xscale("log"); ax.set_ylim(0, 1.15); ax.set_xlim(0.01, 100)
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)
    for k in ("left", "bottom"):
        ax.spines[k].set_color(HEX["tenue"])
    ax.tick_params(colors=HEX["tenue"], labelsize=18)
    ax.set_xlabel(r"forma $m=c/a$", color=HEX["texto"], fontsize=24)
    ax.set_ylabel(r"$N$", color=HEX["texto"], fontsize=28)
    return capa(fig, 20)
