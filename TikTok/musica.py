# -*- coding: utf-8 -*-
r"""
Música original para los edits (síntesis aditiva en numpy, sin muestras externas).

Estructura de 30 s a 150 BPM (pulso de 0,4 s), igual en todos los edits para
que los cortes caigan en el pulso:

    0,0 –  6,4 s  (16 pulsos)  intro: colchón de acordes + arpegio pluck, subida al final
    6,4 – 19,2 s  (32 pulsos)  drop A: bombo, palmada, charles, sub-bajo con «sidechain»
   19,2 – 25,6 s  (16 pulsos)  drop B: charles en semicorcheas, arpegio más brillante
   25,6 – 30,0 s               cierre: impacto, campana y colchón que se apaga

Cada edit usa una tonalidad y una progresión distintas (parámetros de pista()).
"""
import numpy as np
from scipy.signal import fftconvolve, lfilter

SR = 44100
BPM = 150.0
B = 60.0 / BPM
DUR = 30.0
N = int(SR * DUR)
DROP_A, DROP_B, CIERRE = 16 * B, 48 * B, 64 * B


def nota(n):                          # número MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12.0)


def env_ad(n, ataque, caida):
    t = np.arange(n) / SR
    e = np.minimum(t / max(ataque, 1e-4), 1.0) * np.exp(-np.maximum(t - ataque, 0) / caida)
    return e


def pasa_bajos(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    return lfilter([1 - a], [1, -a], x)


def pasa_altos(x, fc):
    return x - pasa_bajos(x, fc)


def pon(buf, x, t):
    i = int(t * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += x[:j - i]


# ------------------------------------------------------------- instrumentos
def pluck(f, dur=0.55, brillo=0.5, rng=None):
    """Karplus–Strong."""
    rng = rng or np.random.default_rng(0)
    n = int(dur * SR)
    p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p)
    buf = pasa_bajos(buf, 2000 + 6000 * brillo)
    out = np.empty(n)
    for k in range(0, n, p):
        m = min(p, n - k)
        out[k:k + m] = buf[:m]
        buf = 0.5 * (buf + np.roll(buf, 1)) * 0.996
    return out * env_ad(n, 0.002, dur * 0.55)


def pad(fs, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for f in fs:
        for det in (-0.004, 0.0, 0.004):
            ff = f * (1 + det)
            for h, ah in ((1, 1.0), (2, 0.35), (3, 0.15)):
                x += ah * np.sin(2 * np.pi * ff * h * t + 7 * det)
    e = np.minimum(t / 0.6, 1) * np.minimum((dur - t) / 0.5, 1)
    return pasa_bajos(x * e, 1400) / (len(fs) * 3)


def bombo():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t / 0.18)
    x[:200] += np.random.default_rng(1).uniform(-1, 1, 200) * np.linspace(0.4, 0, 200)
    return np.tanh(1.6 * x)


def palmada(rng):
    n = int(0.25 * SR)
    ruido = rng.uniform(-1, 1, n)
    x = pasa_altos(pasa_bajos(ruido, 2800), 700)
    e = np.zeros(n)
    for d in (0, 0.009, 0.018):
        i = int(d * SR)
        e[i:] += np.exp(-np.arange(n - i) / SR / 0.06)
    return x * e * 0.9


def charles(rng, dur=0.05):
    n = int(dur * SR)
    return pasa_altos(rng.uniform(-1, 1, n), 7000) * np.exp(-np.arange(n) / SR / (dur / 3))


def sub(f, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.2 * np.sin(4 * np.pi * f * t)
    return x * np.minimum(t / 0.01, 1) * np.minimum((dur - t) / 0.02, 1)


def subida(dur, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    ruido = rng.uniform(-1, 1, n)
    x = np.zeros(n)
    trozos = 24
    for k in range(trozos):
        a, b = k * n // trozos, (k + 1) * n // trozos
        fc = 400 * (24 ** (k / trozos))
        x[a:b] = pasa_bajos(ruido, fc)[a:b]
    x += 0.4 * np.sin(2 * np.pi * (200 * t + 600 * t ** 2 / dur))
    return x * (t / dur) ** 2.2


def impacto(rng):
    n = int(2.4 * SR)
    t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (38 * t + 30 * (1 - np.exp(-t / 0.05)))) * np.exp(-t / 0.7)
    cola = pasa_bajos(rng.uniform(-1, 1, n), 1200) * np.exp(-t / 0.35) * 0.5
    return np.tanh(1.4 * (boom + cola))


def campana(f, dur=2.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / (dur * d))
            for r, a, d in ((1, 1, 0.5), (2.76, 0.45, 0.25), (5.4, 0.25, 0.12), (8.93, 0.1, 0.06)))
    return x * np.minimum(t / 0.003, 1)


def reverb(x, seg=1.6, mezcla=0.28, rng=None):
    rng = rng or np.random.default_rng(3)
    n = int(seg * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t / (seg / 6))
    ir = pasa_bajos(ir, 5000)
    ir /= np.sqrt((ir ** 2).sum())
    return (1 - mezcla) * x + mezcla * fftconvolve(x, ir)[:len(x)] * 3


# ------------------------------------------------------------- pista completa
def pista(raiz=50, progresion=((0, 3, 7), (-4, 0, 3), (3, 7, 10), (-2, 2, 5)), semilla=0,
          ruta="pista.wav"):
    """raiz: nota MIDI de la tónica (50 = Re3).  progresion: acordes en semitonos sobre la raíz."""
    rng = np.random.default_rng(semilla)
    melo = np.zeros(N); arm = np.zeros(N); ritmo = np.zeros(N); grave = np.zeros(N)
    compas = 4 * B
    ncomp = int(np.ceil(DUR / compas))
    # colchón y arpegio
    for c in range(ncomp):
        acorde = progresion[c % len(progresion)]
        t0 = c * compas
        fs = [nota(raiz + s) for s in acorde]
        vol_pad = 0.55 if t0 < DROP_A else (0.4 if t0 < CIERRE else 0.6)
        pon(arm, vol_pad * pad(fs, compas + 0.4), t0)
        # arpegio en corcheas (semicorcheas en el drop B)
        sub_div = 4 if DROP_B <= t0 < CIERRE else 2
        paso = B / sub_div
        notas = [raiz + 12 + s for s in acorde] + [raiz + 24 + acorde[0]]
        patron = [0, 1, 2, 3, 2, 1, 2, 3]
        for k in range(int(compas / paso)):
            tk = t0 + k * paso
            if tk >= CIERRE + 1.6:
                break
            brillo = 0.35 if tk < DROP_A else (0.6 if tk < DROP_B else 0.85)
            amp = 0.22 if tk < DROP_A else 0.26
            pon(melo, amp * pluck(nota(notas[patron[k % len(patron)]]), 0.5, brillo, rng), tk)
        # sub-bajo en los drops
        if DROP_A <= t0 < CIERRE:
            pon(grave, 0.55 * sub(nota(raiz - 24 + acorde[0]), compas), t0)
    # batería
    k_bombo = bombo()
    nb = int(DUR / B)
    duck = np.ones(N)
    for b in range(nb):
        tb = b * B
        if DROP_A <= tb < CIERRE:
            pon(ritmo, 0.9 * k_bombo, tb)
            i = int(tb * SR); m = int(0.22 * SR)
            duck[i:i + m] = np.minimum(duck[i:i + m], 0.25 + 0.75 * (np.arange(min(m, N - i)) / m) ** 1.5)
            if b % 2 == 1:
                pon(ritmo, 0.55 * palmada(rng), tb)
            div = 4 if tb >= DROP_B else 2
            for s in range(div):
                if s == 0 and div == 2:
                    continue
                pon(ritmo, (0.16 if s % 2 else 0.11) * charles(rng), tb + s * B / div)
        elif tb < DROP_A and b >= 8:
            pon(ritmo, 0.08 * charles(rng, 0.03), tb + B / 2)
    # efectos
    fx = np.zeros(N)
    pon(fx, 0.5 * subida(4 * B, rng), DROP_A - 4 * B)
    pon(fx, 0.95 * impacto(rng), DROP_A)
    pon(fx, 0.35 * subida(2 * B, rng), DROP_B - 2 * B)
    pon(fx, 0.95 * impacto(rng), CIERRE)
    pon(fx, 0.35 * campana(nota(raiz + 24)), CIERRE)
    pon(fx, 0.22 * campana(nota(raiz + 31)), CIERRE + 2 * B)
    # mezcla
    m = reverb(melo, 1.4, 0.32) + reverb(arm, 2.2, 0.35) + grave * duck + ritmo + reverb(fx, 1.8, 0.25)
    m[int(DROP_A * SR):int(CIERRE * SR)] *= 1.0
    # pequeña anchura estéreo
    d = int(0.012 * SR)
    izq = m + 0.25 * np.r_[np.zeros(d), (melo + arm)[:-d]]
    der = m + 0.25 * np.r_[(melo + arm)[d:], np.zeros(d)]
    st = np.stack([izq, der], 1)
    t = np.arange(N) / SR
    st *= np.minimum(t / 0.05, 1)[:, None] * np.clip((DUR - t) / 1.2, 0, 1)[:, None]
    st = np.tanh(1.2 * st / (np.abs(st).max() + 1e-9) * 1.4)
    st = st / np.abs(st).max() * 0.89
    import wave
    with wave.open(ruta, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())
    return ruta


if __name__ == "__main__":
    import sys
    pista(ruta=sys.argv[1] if len(sys.argv) > 1 else "pista.wav")
