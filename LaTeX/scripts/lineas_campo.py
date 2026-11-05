#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Simulaciones del Tema 4 (Materiales dieléctricos) para las figuras pgfplots.

Todos los campos que se dibujan son axisimétricos (simetría de revolución
alrededor del eje x, que es la dirección del campo aplicado o de la
polarización).  Para un campo solenoidal F (div F = 0) con esa simetría existe
una *función de corriente de Stokes* psi(x, rho) tal que

    F_x =  (1/rho) d psi / d rho ,      F_rho = -(1/rho) d psi / d x ,

y las líneas de campo son exactamente las curvas de nivel psi = cte.  Así no hay
que integrar ninguna EDO: basta con extraer contornos.  Para E (que no es
solenoidal en las superficies con carga ligada) se usa psi a trozos en cada
región homogénea, de modo que las líneas de E nacen y mueren en la carga de
polarización, como debe ser.

Salida:  ficheros  LaTeX/datos/*.tex  con órdenes  \addplot  ya orientadas en el
sentido del campo (para que pgfplots dibuje las flechas con la paleta del
documento) y  LaTeX/datos/despolarizacion.dat.

Uso:  python3 lineas_campo.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.special import ellipk, ellipe

AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(AQUI, "..", "datos")
os.makedirs(DATOS, exist_ok=True)


# ---------------------------------------------------------------------------
#  Utilidades geométricas
# ---------------------------------------------------------------------------
def remuestrea(p, paso=0.035):
    """Remuestrea una poligonal por longitud de arco (paso aproximado)."""
    d = np.r_[0.0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    if d[-1] < 1e-9:
        return p
    n = max(int(d[-1] / paso), 3)
    s = np.linspace(0.0, d[-1], n + 1)
    return np.c_[np.interp(s, d, p[:, 0]), np.interp(s, d, p[:, 1])]


def contornos(X, Y, Z, niveles):
    """Curvas de nivel de Z (array enmascarable) como lista de poligonales."""
    fig, ax = plt.subplots()
    cs = ax.contour(X, Y, Z, levels=niveles)
    segs = [s for nivel in cs.allsegs for s in nivel if len(s) > 2]
    plt.close(fig)
    return segs


def orienta(seg, campo):
    """Invierte la poligonal si no sigue el sentido del campo F = campo(x, y)."""
    k = len(seg) // 2
    t = seg[min(k + 1, len(seg) - 1)] - seg[max(k - 1, 0)]
    fx, fy = campo(*seg[k])
    return seg if t[0] * fx + t[1] * fy >= 0 else seg[::-1]


def campo_desde_psi(psi, h=1e-5):
    """F = (1/rho) (d psi/d rho, -d psi/d x) por diferencias centradas."""
    def F(x, y):
        y = max(abs(y), 1e-6)
        dpdy = (psi(x, y + h) - psi(x, y - h)) / (2 * h)
        dpdx = (psi(x + h, y) - psi(x - h, y)) / (2 * h)
        return dpdy / y, -dpdx / y
    return F


def posiciones_flecha(s, xs=(-2.15, 2.15), alt=None):
    """Fracciones de longitud de arco donde dibujar flechas: donde la línea cruza
    las abscisas xs (así las flechas quedan alineadas en columnas discretas a
    ambos lados del objeto); si no cruza ninguna, en el punto medio."""
    d = np.r_[0.0, np.cumsum(np.hypot(*np.diff(s, axis=0).T))]
    if d[-1] < 1e-9:
        return []
    fr = []
    for x0 in xs:
        for i in range(len(s) - 1):
            a, b = s[i, 0] - x0, s[i + 1, 0] - x0
            if a == 0 or a * b < 0:
                t = a / (a - b) if a != b else 0.0
                fr.append((d[i] + t * (d[i + 1] - d[i])) / d[-1])
                break
    fr = [f for f in fr if 0.04 < f < 0.96]
    if not fr and alt is not None:
        return posiciones_flecha(s, (alt,))
    if not fr:
        fr = [0.5]
    return fr


def escribe(nombre, bloques, xs=(-2.15, 2.15)):
    """bloques: lista de (estilo, [poligonales]) -> fichero .tex con \\addplot."""
    ruta = os.path.join(DATOS, nombre + ".tex")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("%% Generado por scripts/lineas_campo.py -- no editar a mano\n")
        for estilo, segs in bloques:
            for k, s in enumerate(segs):
                opc = estilo
                if estilo.startswith("linea"):
                    # líneas cortas (interiores): flechas escalonadas a x = -0.5 / +0.5
                    alt = -0.5 if (k + int(s[0, 1] < 0)) % 2 == 0 else 0.5
                    opc += "".join(", flechaen=%.3f" % fr for fr in posiciones_flecha(s, xs, alt))
                pts = " ".join("(%.3f,%.3f)" % (x, y) for x, y in s)
                f.write("\\addplot[%s] coordinates {%s};\n" % (opc, pts))
    print("  ->", os.path.relpath(ruta, os.path.join(AQUI, "..")),
          sum(len(s) for _, s in bloques), "líneas")


def espejo(segs):
    """Añade la imagen especular respecto al eje (rho -> -rho)."""
    return segs + [np.c_[s[:, 0], -s[:, 1]] for s in segs]


def ajusta_a_superficie(segs, dentro, proyecta, tol=0.04):
    """Prolonga los extremos que quedan a < tol de una superficie de carga."""
    out = []
    for s in segs:
        s = s.copy()
        for i in (0, -1):
            q = proyecta(s[i])
            if np.hypot(*(q - s[i])) < tol:
                s = np.vstack([q, s]) if i == 0 else np.vstack([s, q])
        out.append(s)
    return out


def recorta(segs, xmin, xmax, ymin, ymax):
    """Trocea las poligonales para que queden dentro de la ventana."""
    out = []
    for s in segs:
        ok = (s[:, 0] >= xmin) & (s[:, 0] <= xmax) & (s[:, 1] >= ymin) & (s[:, 1] <= ymax)
        cur = []
        for p, b in zip(s, ok):
            if b:
                cur.append(p)
            elif len(cur) > 2:
                out.append(np.array(cur)); cur = []
            else:
                cur = []
        if len(cur) > 2:
            out.append(np.array(cur))
    return out


# ---------------------------------------------------------------------------
#  A) Esfera dieléctrica (eps_r) en un campo uniforme E0 x  (a = 1, E0 = 1)
# ---------------------------------------------------------------------------
def esfera_dielectrica(er=4.0):
    print("Esfera dieléctrica, eps_r =", er)
    beta = (er - 1) / (er + 2)
    xm, ym = 3.0, 2.2
    x = np.linspace(-xm, xm, 900)
    y = np.linspace(1e-4, ym, 380)
    X, Y = np.meshgrid(x, y)
    R = np.hypot(X, Y)
    fuera = R > 1

    psi_out = lambda x, y: 0.5 * y**2 + beta * y**2 / np.hypot(x, y)**3
    psiD_in = lambda x, y: er * 3 / (er + 2) * 0.5 * y**2
    psiE_in = lambda x, y: 3 / (er + 2) * 0.5 * y**2
    psiD = lambda x, y: psi_out(x, y) if np.hypot(x, y) > 1 else psiD_in(x, y)
    psiE = lambda x, y: psi_out(x, y) if np.hypot(x, y) > 1 else psiE_in(x, y)

    niveles = [0.5 * h**2 for h in np.arange(0.2, 2.21, 0.2)]

    # Líneas de D: psi continua -> contorno global
    ZD = np.where(fuera, psi_out(X, Y), psiD_in(X, Y))
    segD = [orienta(remuestrea(s), campo_desde_psi(psiD)) for s in contornos(X, Y, ZD, niveles)]
    # Líneas de E: por regiones (nacen/mueren en sigma_P)
    proy = lambda p: p / np.hypot(*p)
    Zo = np.ma.masked_where(~fuera, psi_out(X, Y))
    Zi = np.ma.masked_where(fuera, psiE_in(X, Y))
    segE = contornos(X, Y, Zo, niveles) + contornos(X, Y, Zi, niveles)
    segE = ajusta_a_superficie(segE, None, proy)
    segE = [orienta(remuestrea(s), campo_desde_psi(psiE)) for s in segE]

    # Equipotenciales (plano completo)
    yy = np.linspace(-ym, ym, 600)
    X2, Y2 = np.meshgrid(x, yy)
    R2 = np.hypot(X2, Y2)
    phi = np.where(R2 > 1, -X2 + beta * X2 / np.maximum(R2, 1e-9)**3, -3 / (er + 2) * X2)
    segV = [remuestrea(s) for s in contornos(X2, Y2, phi, np.arange(-2.75, 2.76, 0.5))]

    eje = [np.array([[-xm, 0.0], [xm, 0.0]])]
    escribe("esfera-dielectrica-D", [("equipot", segV), ("lineaD", espejo(segD)), ("lineaD", eje)])
    escribe("esfera-dielectrica-E", [("equipot", segV), ("lineaE", espejo(segE)), ("lineaE", eje)])


# ---------------------------------------------------------------------------
#  B) Esfera uniformemente polarizada P x  (problema 4.1; a = 1, P/eps0 = 1)
# ---------------------------------------------------------------------------
def esfera_polarizada():
    print("Esfera uniformemente polarizada")
    xm, ym = 2.6, 2.0
    x = np.linspace(-xm, xm, 900)
    y = np.linspace(1e-4, ym, 360)
    X, Y = np.meshgrid(x, y)
    R = np.hypot(X, Y)
    fuera = R > 1

    psi_out = lambda x, y: y**2 / (3 * np.hypot(x, y)**3)       # dipolo p = 4/3 pi a^3 P
    psiD_in = lambda x, y: y**2 / 3                                # D = 2P/3
    psiE_in = lambda x, y: -y**2 / 6                               # E = -P/(3 eps0)
    psiD = lambda x, y: psi_out(x, y) if np.hypot(x, y) > 1 else psiD_in(x, y)
    psiE = lambda x, y: psi_out(x, y) if np.hypot(x, y) > 1 else psiE_in(x, y)

    hs = [0.22, 0.38, 0.52, 0.64, 0.75, 0.85, 0.94]
    nivD = [h**2 / 3 for h in hs]
    nivEi = sorted(-h**2 / 6 for h in hs)

    ZD = np.where(fuera, psi_out(X, Y), psiD_in(X, Y))
    segD = contornos(X, Y, ZD, nivD)
    segD = [orienta(remuestrea(s), campo_desde_psi(psiD)) for s in segD]

    proy = lambda p: p / np.hypot(*p)
    Zo = np.ma.masked_where(~fuera, psi_out(X, Y))
    Zi = np.ma.masked_where(fuera, psiE_in(X, Y))
    segE = contornos(X, Y, Zo, nivD) + contornos(X, Y, Zi, nivEi)
    segE = ajusta_a_superficie(segE, None, proy)
    segE = [orienta(remuestrea(s), campo_desde_psi(psiE)) for s in segE]

    yy = np.linspace(-ym, ym, 560)
    X2, Y2 = np.meshgrid(x, yy)
    R2 = np.hypot(X2, Y2)
    phi = np.where(R2 > 1, X2 / (3 * np.maximum(R2, 1e-9)**3), X2 / 3)
    nivV = [v for v in np.arange(-0.30, 0.31, 0.06) if abs(v) > 1e-6]
    segV = [remuestrea(s) for s in contornos(X2, Y2, phi, nivV)]

    # Eje: fuera E apunta hacia +x a ambos lados (dipolo); dentro, de + a - (hacia -x)
    ejeE = [np.array([[-xm, 0], [-1, 0]]), np.array([[1, 0], [xm, 0]]),
            np.array([[1, 0], [-1, 0]])]
    ejeD = [np.array([[-xm, 0], [xm, 0]])]
    escribe("esfera-polarizada-E", [("equipot", segV), ("lineaE", espejo(segE)), ("lineaE", ejeE)])
    escribe("esfera-polarizada-D", [("equipot", segV), ("lineaD", espejo(segD)), ("lineaD", ejeD)])


# ---------------------------------------------------------------------------
#  C) Cilindro uniformemente polarizado (electrete en barra, problema 4.4)
#     D es el «campo de un solenoide» con corriente superficial K = P x n
#     (analogía D <-> B/mu0, eps0 E <-> H, P <-> M).
# ---------------------------------------------------------------------------
def psi_espira(x, y, a, x0):
    """rho*A_phi de una espira de radio a en x0, corriente unidad (mu0 = 1)."""
    y = np.maximum(np.abs(y), 1e-9)
    den = (a + y)**2 + (x - x0)**2
    m = np.clip(4 * a * y / den, 0, 1 - 1e-12)
    k = np.sqrt(m)
    Aphi = (1.0 / (np.pi * k)) * np.sqrt(a / y) * ((1 - m / 2) * ellipk(m) - ellipe(m))
    return y * Aphi


def phi_anillo(x, y, s, x0):
    """Potencial (4 pi eps0 = 1 -> factor 1/(4pi)) de un anillo de carga unidad."""
    y = np.abs(y)
    den = (s + y)**2 + (x - x0)**2
    m = np.clip(4 * s * y / den, 0, 1 - 1e-12)
    return (1 / (4 * np.pi)) * (2 / np.pi) * ellipk(m) / np.sqrt(den)


def cilindro_polarizado(a=0.5, l=1.5, nombre="cilindro-polarizado"):
    print("Cilindro polarizado a =", a, " l =", l)
    xm, ym = 3.2, 1.9
    x = np.linspace(-xm, xm, 640)
    y = np.linspace(1e-3, ym, 300)
    X, Y = np.meshgrid(x, y)
    nodos, pesos = np.polynomial.legendre.leggauss(160)
    xs = l * nodos
    ws = l * pesos

    def psiD_arr(Xa, Ya):
        Z = np.zeros_like(Xa, dtype=float)
        for x0, w in zip(xs, ws):
            Z += w * psi_espira(Xa, Ya, a, x0)
        return Z

    dentro = (np.abs(X) < l) & (Y < a)
    ZD = psiD_arr(X, Y)
    ZE = np.where(dentro, ZD - 0.5 * Y**2, ZD)

    psiD = lambda x0, y0: float(psiD_arr(np.array([x0]), np.array([y0]))[0])
    psiE = lambda x0, y0: psiD(x0, y0) - (0.5 * y0**2 if (abs(x0) < l and abs(y0) < a) else 0.0)

    hs = np.linspace(0.08, 0.46, 6) * (a / 0.5)
    nivD = sorted(psiD(0.0, h) for h in hs)
    nivEi = sorted(psiE(0.0, h) for h in np.linspace(0.12, 0.42, 4) * (a / 0.5))

    segD = [orienta(remuestrea(s), campo_desde_psi(psiD)) for s in contornos(X, Y, ZD, nivD)]

    def proy(p):
        cand = [np.array([np.clip(p[0], -l, l), a]),
                np.array([l, np.clip(p[1], 0, a)]),
                np.array([-l, np.clip(p[1], 0, a)])]
        return min(cand, key=lambda q: np.hypot(*(q - p)))
    Zo = np.ma.masked_where(dentro, ZE)
    Zi = np.ma.masked_where(~dentro, ZE)
    segE = contornos(X, Y, Zo, nivD) + contornos(X, Y, Zi, nivEi)
    segE = ajusta_a_superficie(segE, None, proy)
    segE = [orienta(remuestrea(s), campo_desde_psi(psiE)) for s in segE]

    # Equipotenciales: discos +sigma (x = +l) y -sigma (x = -l), sigma = P = 1
    yy = np.linspace(-ym, ym, 300)
    X2, Y2 = np.meshgrid(np.linspace(-xm, xm, 400), yy)
    ns, wsr = np.polynomial.legendre.leggauss(60)
    ss = 0.5 * a * (ns + 1)
    wsr = 0.5 * a * wsr
    phi = np.zeros_like(X2)
    for s, w in zip(ss, wsr):
        dq = 2 * np.pi * s * w            # sigma = 1
        phi += dq * (phi_anillo(X2, Y2, s, l) - phi_anillo(X2, Y2, s, -l))
    phi /= 1.0  # unidades P/eps0 (eps0 = 1)
    vmax = np.nanmax(np.abs(phi))
    nivV = [v for v in np.linspace(-0.8 * vmax, 0.8 * vmax, 12) if abs(v) > 1e-6]
    segV = [remuestrea(s) for s in contornos(X2, Y2, phi, nivV)]

    ejeD = [np.array([[-xm, 0], [xm, 0]])]
    ejeE = [np.array([[l, 0], [xm, 0]]), np.array([[-xm, 0], [-l, 0]]),
            np.array([[l, 0], [-l, 0]])]
    escribe(nombre + "-D", [("equipot", segV), ("lineaD", espejo(segD)), ("lineaD", ejeD)])
    escribe(nombre + "-E", [("equipot", segV), ("lineaE", espejo(segE)), ("lineaE", ejeE)])


# ---------------------------------------------------------------------------
#  D) Factor de despolarización de un esferoide (eje de revolución // campo)
# ---------------------------------------------------------------------------
def despolarizacion():
    print("Factor de despolarización")
    ms = np.logspace(-2, 2, 241)
    N = []
    for m in ms:                    # m = c/a: semieje paralelo / semieje transversal
        if abs(m - 1) < 1e-9:
            N.append(1 / 3)
        elif m > 1:                 # esferoide alargado (aguja en el límite)
            e = np.sqrt(1 - 1 / m**2)
            N.append((1 - e**2) / e**3 * (np.arctanh(e) - e))
        else:                       # esferoide achatado (lenteja en el límite)
            e = np.sqrt(1 / m**2 - 1)
            N.append((1 + e**2) / e**3 * (e - np.arctan(e)))
    ruta = os.path.join(DATOS, "despolarizacion.dat")
    np.savetxt(ruta, np.c_[ms, N], fmt="%.6g", header="m N", comments="")
    print("  ->", ruta)


if __name__ == "__main__":
    esfera_dielectrica(4.0)
    esfera_polarizada()
    cilindro_polarizado()
    despolarizacion()
