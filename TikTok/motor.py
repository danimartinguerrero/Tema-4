# -*- coding: utf-8 -*-
r"""
Motor de los edits de TikTok de Electromagnetismo I.

Vídeo vertical 1080x1920 a 30 fps.  Cada vídeo es una lista de «clips»
(funciones que dibujan sobre el lienzo en un intervalo de tiempo) más unos
efectos globales sincronizados con el pulso de la música (150 BPM):
golpes de zoom, destellos, viñeta y grano.

Las fórmulas y los textos se componen con LaTeX (pdflatex + Latin Modern, la
misma tipografía que los apuntes) y se rasterizan con pdftocairo; quedan en
caché en TikTok/cache.  Las gráficas se dibujan con matplotlib sobre fondo
transparente y se componen como capas RGBA.

El render se reparte en segmentos que se codifican en paralelo con ffmpeg y
se concatenan al final, junto con la pista de audio generada por musica.py.
"""
import os, math, hashlib, subprocess, tempfile, shutil
import numpy as np
from PIL import Image, ImageFilter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

W, H, FPS = 1080, 1920, 30
BPM = 150.0
BEAT = 60.0 / BPM            # 0,4 s
AQUI = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(AQUI, "cache")
os.makedirs(CACHE, exist_ok=True)

# Paleta (la del documento oscuro)
C = dict(
    negro=(0.0, 0.0, 0.0), texto=(0.93, 0.93, 0.93), tenue=(0.55, 0.58, 0.63),
    cian=(0.125, 0.706, 0.808), violeta=(0.643, 0.545, 0.980), ambar=(0.941, 0.706, 0.161),
    rojo=(1.0, 0.42, 0.42), azul=(0.357, 0.549, 1.0), verde=(0.29, 0.87, 0.50),
    oro=(0.96, 0.78, 0.32), gris=(0.18, 0.19, 0.21), caja=(0.055, 0.063, 0.078),
)
HEX = {k: "#%02x%02x%02x" % tuple(int(255 * c) for c in v) for k, v in C.items()}


# ============================================================== utilidades
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def suave(x):                       # easeInOutCubic en [0,1]
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def sale(x):                        # easeOutCubic
    x = clamp(x)
    return 1 - (1 - x) ** 3


def rampa(t, t0, d):                # 0 -> 1 entre t0 y t0+d, suavizado
    return suave((t - t0) / d) if d > 0 else float(t >= t0)


# ============================================================== LaTeX -> RGBA
PREAMBULO = r"""\documentclass[border=4pt]{standalone}
\usepackage[T1]{fontenc}\usepackage[utf8]{inputenc}\usepackage{lmodern}
\usepackage{amsmath,amssymb,esint,bm}
\newcommand{\vE}{\vec E}\newcommand{\vD}{\vec D}\newcommand{\vP}{\vec P}\newcommand{\vp}{\vec p}
\newcommand{\vr}{\vec r}\newcommand{\vF}{\vec F}\newcommand{\eo}{\varepsilon_0}\newcommand{\er}{\varepsilon_{\mathrm r}}
\newcommand{\dd}{\mathrm{d}}\newcommand{\grad}{\vec\nabla}\newcommand{\divg}{\vec\nabla\!\cdot}
\newcommand{\rot}{\vec\nabla\!\times}\newcommand{\nn}{\hat n}\newcommand{\rhoP}{\rho_{\mathrm P}}
\newcommand{\sigmaP}{\sigma_{\mathrm P}}\newcommand{\rhof}{\rho_{\mathrm f}}\newcommand{\vcero}{\vec 0}
\begin{document}
%s
\end{document}
"""


def _clave(*cosas):
    return hashlib.sha1("|".join(map(str, cosas)).encode()).hexdigest()[:16]


def tex_png(cuerpo, px):
    """Rasteriza un fragmento LaTeX a PNG con transparencia; px = tamaño de 1 em."""
    k = _clave(cuerpo, px)
    png = os.path.join(CACHE, k + ".png")
    if os.path.exists(png):
        return png
    d = tempfile.mkdtemp(dir=CACHE)
    try:
        with open(os.path.join(d, "f.tex"), "w", encoding="utf-8") as f:
            f.write(PREAMBULO % cuerpo)
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "f.tex"],
                           cwd=d, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if r.returncode != 0:
            raise RuntimeError("LaTeX falló con:\n%s\n%s" % (cuerpo, r.stdout.decode(errors="ignore")[-1500:]))
        dpi = px * 72.27 / 10.0
        subprocess.run(["pdftocairo", "-png", "-transp", "-singlefile", "-r", "%.3f" % dpi,
                        os.path.join(d, "f.pdf"), os.path.join(d, "out")], check=True)
        shutil.move(os.path.join(d, "out.png"), png)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return png


_TEX = {}


def tex(s, px=64, color="texto", math=True):
    """Devuelve una capa RGBA (float32) con el texto o la fórmula coloreada."""
    k = (s, px, color, math)
    if k in _TEX:
        return _TEX[k]
    cuerpo = ("$\\displaystyle %s$" % s) if math else s
    a = np.asarray(Image.open(tex_png(cuerpo, px)).convert("RGBA"), dtype=np.float32) / 255.0
    alfa = a[..., 3]
    col = C[color] if isinstance(color, str) else color
    out = np.zeros_like(a)
    out[..., 0], out[..., 1], out[..., 2] = col
    out[..., 3] = alfa
    _TEX[k] = out
    return out


# ============================================================== matplotlib -> RGBA
def figura(w, h, xlim=None, ylim=None, aspecto=True):
    fig = plt.figure(figsize=(w / 100, h / 100), dpi=100)
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor((0, 0, 0, 0))
    ax.set_axis_off()
    if xlim:
        ax.set_xlim(*xlim)
    if ylim:
        ax.set_ylim(*ylim)
    if aspecto:
        ax.set_aspect("equal", adjustable="box")
    return fig, ax


def capa(fig, difumina=0):
    """Figura -> RGBA.  difumina: anchura (px) del borde que se funde con el fondo."""
    fig.canvas.draw()
    a = np.asarray(fig.canvas.buffer_rgba(), dtype=np.float32).copy() / 255.0
    plt.close(fig)
    if difumina:
        h, w = a.shape[:2]
        fx = np.clip(np.minimum(np.arange(w), w - 1 - np.arange(w)) / difumina, 0, 1)
        fy = np.clip(np.minimum(np.arange(h), h - 1 - np.arange(h)) / difumina, 0, 1)
        m = (np.sin(np.pi / 2 * fy)[:, None] * np.sin(np.pi / 2 * fx)[None, :]) ** 1.5
        a[..., 3] *= m
    return a


def ajusta(img, ancho=960):
    """Factor de escala para que una capa no supere el ancho útil."""
    return min(1.0, ancho / img.shape[1])


def linea_brillo(ax, x, y, color, lw=2.2, brillo=0.18, **kw):
    ax.plot(x, y, color=color, lw=lw * 4.5, alpha=brillo, solid_capstyle="round", **kw)
    ax.plot(x, y, color=color, lw=lw, alpha=1.0, solid_capstyle="round", **kw)


# ============================================================== composición
_ESC = {}
_BLUR = {}


def _escala(img, s):
    if abs(s - 1) < 1e-3:
        return img
    k = (id(img), round(s, 3))
    if k not in _ESC:
        h, w = img.shape[:2]
        im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), "RGBA")
        im = im.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)
        if len(_ESC) > 400:
            _ESC.clear()
        _ESC[k] = np.asarray(im, dtype=np.float32) / 255.0
    return _ESC[k]


def _desenfoque(img, r):
    k = (id(img), r)
    if k not in _BLUR:
        a = Image.fromarray((np.clip(img[..., 3], 0, 1) * 255).astype(np.uint8), "L")
        _BLUR[k] = np.asarray(a.filter(ImageFilter.GaussianBlur(r)), dtype=np.float32) / 255.0
    return _BLUR[k]


def pon(lienzo, img, cx, cy, alfa=1.0, barrido=1.0, escala=1.0, brillo=0.0):
    """Compone la capa img centrada en (cx, cy).  barrido revela de izquierda a derecha."""
    if alfa <= 0.003 or barrido <= 0:
        return
    if brillo > 0:
        g = _desenfoque(img, 16)
        col = np.array(_color_dom(img), np.float32)
        add = g[..., None] * col[None, None, :] * (brillo * alfa)
        if barrido < 1:
            xs = np.arange(add.shape[1], dtype=np.float32)
            add = add * np.clip((barrido * add.shape[1] - xs) / 24.0 + 0.5, 0, 1)[None, :, None]
        _suma(lienzo, add, cx, cy, escala)
    im = _escala(img, escala)
    h, w = im.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xa >= xb or ya >= yb:
        return
    sub = im[ya - y0:yb - y0, xa - x0:xb - x0]
    a = sub[..., 3:4] * alfa
    if barrido < 1:
        xs = np.arange(xa - x0, xb - x0, dtype=np.float32)
        a = a * np.clip((barrido * w - xs) / 24.0 + 0.5, 0, 1)[None, :, None]
    dst = lienzo[ya:yb, xa:xb]
    dst *= (1 - a)
    dst += sub[..., :3] * a


def _color_dom(img):
    a = img[..., 3]
    s = a.sum()
    if s < 1:
        return (1, 1, 1)
    return tuple((img[..., i] * a).sum() / s for i in range(3))


def _suma(lienzo, add, cx, cy, escala):
    if abs(escala - 1) > 1e-3:
        h, w = add.shape[:2]
        im = Image.fromarray((np.clip(add, 0, 1) * 255).astype(np.uint8), "RGB")
        add = np.asarray(im.resize((max(1, int(w * escala)), max(1, int(h * escala)))), dtype=np.float32) / 255
    h, w = add.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xa < xb and ya < yb:
        lienzo[ya:yb, xa:xb] += add[ya - y0:yb - y0, xa - x0:xb - x0]


def rect(lienzo, x0, y0, x1, y1, color, alfa=1.0, grosor=None):
    col = np.array(C[color] if isinstance(color, str) else color, dtype=np.float32)
    x0, y0, x1, y1 = [int(round(v)) for v in (x0, y0, x1, y1)]
    if grosor is None:
        sl = lienzo[max(0, y0):min(H, y1), max(0, x0):min(W, x1)]
        sl *= (1 - alfa)
        sl += col * alfa
    else:
        g = grosor
        for (a, b, c, d) in ((x0, y0, x1, y0 + g), (x0, y1 - g, x1, y1), (x0, y0, x0 + g, y1), (x1 - g, y0, x1, y1)):
            rect(lienzo, a, b, c, d, color, alfa)


# ============================================================== vídeo
class Video:
    def __init__(self, nombre, duracion=30.0):
        self.nombre = nombre
        self.dur = duracion
        self.clips = []          # (t0, t1, fn)
        self.golpes = []         # (t, intensidad): zoom punch
        self.destellos = []      # (t, intensidad, color)
        self.ondas = []          # (t, cy): onda expansiva de luz

    def clip(self, t0, t1):
        def deco(fn):
            self.clips.append((t0, t1, fn))
            return fn
        return deco

    def golpe(self, t, k=0.035):
        self.golpes.append((t, k))

    def destello(self, t, k=0.85, color="texto"):
        self.destellos.append((t, k, color))

    # ---------------------------------------------------- frame
    def frame(self, t):
        L = np.zeros((H, W, 3), np.float32)
        for t0, t1, fn in self.clips:
            if t0 - 1e-6 <= t < t1 - 1e-6:          # tolerancia: sin huecos en los cortes
                fn(L, t, t - t0, t1 - t0)
        # golpes de zoom (decaen en ~0,25 s)
        z = 1.0
        for tg, k in self.golpes:
            if 0 <= t - tg < 0.5:
                z += k * math.exp(-(t - tg) / 0.09)
        if z > 1.0005:
            im = Image.fromarray((np.clip(L, 0, 1) * 255).astype(np.uint8))
            w2, h2 = int(W * z), int(H * z)
            im = im.resize((w2, h2), Image.BILINEAR).crop(((w2 - W) // 2, (h2 - H) // 2, (w2 - W) // 2 + W, (h2 - H) // 2 + H))
            L = np.asarray(im, dtype=np.float32) / 255
        # destellos
        for tf, k, col in self.destellos:
            if 0 <= t - tf < 0.35:
                a = k * math.exp(-(t - tf) / 0.07)
                L = L * (1 - a) + np.array(C[col], np.float32) * a
        L = L * VINETA[..., None]
        L += GRANO[int(t * FPS) % len(GRANO)]
        return (np.clip(L, 0, 1) * 255).astype(np.uint8)


def _vineta():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot((x - W / 2) / (W * 0.62), (y - H / 2) / (H * 0.62))
    return np.clip(1.08 - 0.42 * r ** 2.2, 0.55, 1.0).astype(np.float32)


VINETA = _vineta()
_rng = np.random.default_rng(7)
GRANO = [(_rng.standard_normal((H, W, 1)).astype(np.float32) * 0.006) for _ in range(6)]


# ============================================================== elementos comunes
def cabecera(L, texto, alfa=1.0, color="cian"):
    """Rótulo pequeño en versalitas, arriba (zona segura de TikTok)."""
    img = tex(r"\textsc{%s}" % texto, 30, color, math=False)
    pon(L, img, W / 2, 205, alfa=alfa)


def pie(L, texto, alfa=1.0):
    img = tex(r"\textit{%s}" % texto, 30, "tenue", math=False)
    pon(L, img, W / 2, 1490, alfa=alfa)


def caja_oro(L, img, cx, cy, alfa=1.0, pad=46, escala=1.0):
    h, w = img.shape[:2]
    w, h = w * escala, h * escala
    rect(L, cx - w / 2 - pad, cy - h / 2 - pad * 0.8, cx + w / 2 + pad, cy + h / 2 + pad * 0.8, "oro", alfa, grosor=4)
    pon(L, img, cx, cy, alfa=alfa, escala=escala, brillo=0.55)


# ============================================================== render paralelo
def render(construir, salida, audio=None, trabajadores=4, fps=FPS, preview=False):
    """construir() -> Video.  Se llama dentro de cada proceso (los clips son clausuras)."""
    import multiprocessing as mp
    v = construir()
    n = int(round(v.dur * fps))
    cortes = np.linspace(0, n, trabajadores + 1).astype(int)
    tmp = tempfile.mkdtemp(dir=AQUI)
    trozos = [(construir, i, cortes[i], cortes[i + 1], os.path.join(tmp, "s%02d.mp4" % i), fps)
              for i in range(trabajadores)]
    with mp.get_context("fork").Pool(trabajadores) as pool:
        pool.map(_render_trozo, trozos)
    lista = os.path.join(tmp, "lista.txt")
    with open(lista, "w") as f:
        for t in trozos:
            f.write("file '%s'\n" % t[4])
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista]
    if audio:
        cmd += ["-i", audio, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    else:
        cmd += ["-c", "copy"]
    cmd += ["-movflags", "+faststart", salida]
    subprocess.run(cmd, check=True)
    shutil.rmtree(tmp, ignore_errors=True)


def _render_trozo(args):
    construir, i, a, b, ruta, fps = args
    v = construir()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", "%dx%d" % (W, H), "-r", str(fps), "-i", "-",
                          "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
                          "-profile:v", "high", ruta], stdin=subprocess.PIPE)
    for k in range(a, b):
        p.stdin.write(v.frame(k / fps).tobytes())
    p.stdin.close()
    p.wait()
