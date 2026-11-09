# -*- coding: utf-8 -*-
r"""
Contenido de la serie de edits.  Cada función devuelve un Video listo para
renderizar con motor.render(...).

Uso:
    python3 edits.py energia            # renderiza un edit
    python3 edits.py todos              # renderiza la serie completa
    python3 edits.py energia --preview  # fotogramas de control
"""
import os, sys
import numpy as np
import plantilla as P
import visuales as V
import motor as M
import musica

SALIDA = os.path.join(M.AQUI, "videos")
os.makedirs(SALIDA, exist_ok=True)


# =================================================================== 1. Energía
def energia():
    return P.construye(dict(
        nombre="01-energia",
        cabecera="Energía electrostática",
        intro_formula=r"U_e=\frac12\sum_{i}q_i\,\phi_i",
        intro_visual=V.v1_intro,
        intro_pregunta="¿dónde se guarda la energía?",
        pasos=[
            ("cargas puntuales", r"U_e=\frac12\sum_{i}q_i\,\phi_i"),
            ("distribución continua", r"U_e=\frac12\int_V\rho\,\phi\,\dd V"),
            ("ley de Gauss", r"\rho=\eo\,\divg\vE"),
            ("por partes", r"\phi\,\divg\vE=\divg(\phi\vE)+E^2"),
            ("teorema de la divergencia", r"\oiint_{S_R}\phi\,\vE\cdot\dd\vec S\;\sim\;\frac1R\;\to\;0"),
            ("energía del campo", r"U_e=\frac{\eo}{2}\int_{\mathbb R^3}E^2\,\dd V"),
            ("densidad de energía", r"u_e=\frac{\eo}{2}\,E^2"),
            ("esfera cargada", r"U_e=\frac{3Q^2}{20\pi\eo a}"),
        ],
        visual_A=V.v1_opuestas, visual_B=V.v1_esfera,
        rafaga=[
            ("f", r"E^2\geq0", "texto"),
            ("w", r"U_e\geq0"),
            ("v", V.v1_esfera),
            ("f", r"\tfrac16\ \text{dentro}", "violeta", 110),
            ("f", r"\tfrac56\ \text{fuera}", "cian", 110),
            ("v", V.v1_dUdr),
            ("w", r"U_e\neq U_1+U_2"),
            ("f", r"+\,\eo\!\int\vE_1\!\cdot\vE_2\,\dd V", "ambar", 96),
            ("v", V.v1_iguales),
            ("v", V.v1_opuestas),
            ("f", r"u_e\propto r^{-4}", "texto"),
            ("n", "50\\% \\ en\\ r>2a"),
            ("v", V.v1_esfera),
            ("w", r"\tfrac{\eo}{2}E^2"),
            ("n", "[J/m\\textsuperscript{3}]", "cian"),
            ("f", r"\frac{Q^2}{8\pi\eo a}", "violeta"),
        ],
        final=r"U_e=\frac{\eo}{2}\int E^2\,\dd V",
        frase=["la energía no está en las cargas:", "vive en el campo"],
    ))


# =================================================================== 2. Earnshaw y fuerzas
def fuerzas():
    return P.construye(dict(
        nombre="02-earnshaw-fuerzas",
        cabecera="Teorema de Earnshaw",
        intro_formula=r"\nabla^2\phi=0",
        intro_extra=None,
        intro_visual=V.v2_intro,
        intro_pregunta="¿se puede levitar una carga solo con cargas?",
        pasos=[
            ("equilibrio", r"\grad\phi(\vr_0)=\vcero"),
            ("estable exige un mínimo", r"\partial_x^2\phi>0,\ \ \partial_y^2\phi>0,\ \ \partial_z^2\phi>0"),
            ("pero sin cargas", r"\partial_x^2\phi+\partial_y^2\phi+\partial_z^2\phi=0"),
            ("valor medio", r"\phi(\vr_0)=\frac{1}{4\pi R^2}\oiint_{S_R}\phi\,\dd S"),
            ("trabajos virtuales", r"\dd W_{\mathrm{mec}}+\dd U_e=0"),
            ("sistema aislado", r"\vF=-\grad U_e\big|_{Q}"),
            ("con baterías", r"\vF=+\grad U_e\big|_{\phi}"),
            ("condensador", r"F_\xi=\frac12\,V^2\,\frac{\dd C}{\dd\xi}"),
        ],
        visual_A=V.v2_silla, visual_B=V.v2_perfiles,
        rafaga=[
            ("w", r"\nabla^2\phi=0"),
            ("v", V.v2_silla),
            ("f", r"\text{punto de silla}", "ambar", 110),
            ("v", V.v2_perfiles),
            ("f", r"-\,\partial_\xi U_e\big|_{Q}", "cian"),
            ("f", r"+\,\partial_\xi U_e\big|_{\phi}", "violeta"),
            ("w", r"-\partial_\xi U_e\big|_{Q}=+\partial_\xi U_e\big|_{\phi}"),
            ("v", V.v2_placas),
            ("f", r"F=-\frac{Q^2}{2\eo S}", "texto"),
            ("n", "dW\\textsubscript{bat} = 2 dU\\textsubscript{e}", "oro"),
            ("v", V.v2_placas),
            ("f", r"P=\frac{\sigma^2}{2\eo}", "ambar"),
            ("v", V.v2_silla),
            ("w", r"C\nearrow"),
            ("f", r"\frac{Q^2}{2C^2}\frac{\dd C}{\dd\xi}", "cian"),
            ("n", "Earnshaw, 1842", "oro"),
        ],
        final=r"F_\xi=\frac12\,V^2\,\frac{\dd C}{\dd\xi}",
        frase=["no hay equilibrio estable solo con cargas:", "el sistema siempre busca más capacidad"],
    ))


# =================================================================== 3. Dieléctricos
def dielectricos():
    return P.construye(dict(
        nombre="03-dielectricos",
        cabecera="Materiales dieléctricos",
        intro_formula=r"\vp=\alpha\,\vE",
        intro_extra=None,
        intro_visual=V.v3_intro,
        intro_pregunta="¿qué le hace un campo a un aislante?",
        pasos=[
            ("polarizabilidad", r"\vp=\alpha\,\vE,\qquad \alpha=4\pi\eo a^3"),
            ("vector polarización", r"\vP=\frac{\dd\vp}{\dd V}"),
            ("aproximación dipolar", r"\phi=\frac{1}{4\pi\eo}\int_{V'}\frac{\vP\cdot\hat u_R}{R^2}\,\dd V'"),
            ("cargas ligadas", r"\rhoP=-\divg\vP,\qquad \sigmaP=\vP\cdot\nn"),
            ("neutralidad", r"\int_V\rhoP\,\dd V+\oiint_S\sigmaP\,\dd S=0"),
            ("vector desplazamiento", r"\vD=\eo\vE+\vP"),
            ("ley de Gauss", r"\divg\vD=\rhof"),
            ("medio lineal", r"\vD=\varepsilon\vE,\qquad \varepsilon=\eo(1+\chi)"),
        ],
        visual_A=V.v3_red, visual_B=V.v3_e4,
        rafaga=[
            ("w", r"\rhoP=-\divg\vP"),
            ("v", V.v3_red),
            ("f", r"\sigmaP=P\cos\theta", "ambar"),
            ("v", V.v3_e1),
            ("v", V.v3_e4),
            ("v", V.v3_e20),
            ("f", r"\vE_{\mathrm{int}}=\frac{3}{\er+2}\,\vE_0", "cian"),
            ("w", r"\rot\vD=\rot\vP"),
            ("v", V.v3_d4),
            ("f", r"\frac{\tan\theta_2}{\varepsilon_2}=\frac{\tan\theta_1}{\varepsilon_1}", "violeta"),
            ("n", "D\\textsubscript{n} continua", "violeta"),
            ("n", "E\\textsubscript{t} continua", "cian"),
            ("v", V.v3_e20),
            ("f", r"\er(\mathrm{agua})\simeq80", "texto"),
            ("w", r"\vE=\frac{\vE_0}{\er}"),
            ("v", V.v3_d4),
        ],
        final=r"\divg\vD=\rhof",
        frase=["el desplazamiento solo ve la carga libre:", "la ligada la pone el material"],
    ))


# =================================================================== 4. Cavidades
def cavidades():
    return P.construye(dict(
        nombre="04-cavidades",
        cabecera="Cavidades en un dieléctrico",
        intro_formula=r"\vE_{\mathrm{cav}}\overset{?}{=}\vE_d",
        intro_extra=None,
        intro_visual=V.v4_intro,
        intro_pregunta="¿qué campo mide una carga dentro de un hueco?",
        pasos=[
            ("superposición", r"\vE_{\mathrm{cav}}=\vE_d+\vE\big[-\vP_d\big]"),
            ("aguja", r"E_t\ \text{continua}\ \Rightarrow\ \vE_{\mathrm{cav}}=\vE_d"),
            ("lenteja", r"D_n\ \text{continua}\ \Rightarrow\ \vD_{\mathrm{cav}}=\vD_d"),
            ("lenteja", r"\vE_{\mathrm{cav}}=\vE_d+\frac{\vP_d}{\eo}"),
            ("esfera", r"\vE_{\mathrm{cav}}=\vE_d+\frac{\vP_d}{3\eo}"),
            ("factor de despolarización", r"\vE_{\mathrm{cav}}=\vE_d+N\,\frac{\vP_d}{\eo}"),
            ("campo local de Lorentz", r"\vp=\alpha\Big(\vE+\frac{\vP}{3\eo}\Big)"),
            ("Clausius--Mossotti", r"\frac{\er-1}{\er+2}=\frac{n\,\alpha}{3\eo}"),
        ],
        visual_A=V.v4_aguja, visual_B=V.v4_lenteja,
        rafaga=[
            ("f", r"N=0", "cian"),
            ("v", V.v4_aguja),
            ("f", r"N=\tfrac13", "oro"),
            ("v", V.v4_esfera),
            ("f", r"N=1", "violeta"),
            ("v", V.v4_lenteja),
            ("w", r"\vE_{\mathrm{cav}}=\vE_d"),
            ("w", r"\vD_{\mathrm{cav}}=\vD_d"),
            ("v", V.v4_curva),
            ("n", "aguja $\\to$ E", "cian"),
            ("n", "lenteja $\\to$ D/$\\varepsilon_0$", "violeta"),
            ("f", r"+\frac{\vP_d}{\eo}", "ambar"),
            ("v", V.v4_curva),
            ("f", r"\frac{\er-1}{\er+2}", "violeta"),
            ("w", r"0\leq N\leq1"),
            ("v", V.v4_esfera),
        ],
        final=r"\vE_{\mathrm{cav}}=\vE_d+N\,\frac{\vP_d}{\eo}",
        frase=["la forma del hueco decide qué mides:", "aguja, $\\vec E$; \\ lenteja, $\\vec D/\\varepsilon_0$"],
    ))


EDITS = {
    "energia": (energia, dict(raiz=50, semilla=1)),
    "fuerzas": (fuerzas, dict(raiz=45, semilla=2,
                              progresion=((0, 3, 7), (5, 8, 12), (-4, 0, 3), (-5, -1, 2)))),
    "dielectricos": (dielectricos, dict(raiz=52, semilla=3,
                                        progresion=((0, 3, 7), (-2, 2, 5), (-4, 0, 3), (-2, 2, 5)))),
    "cavidades": (cavidades, dict(raiz=48, semilla=4,
                                  progresion=((0, 3, 7), (-5, -2, 2), (-4, 0, 3), (5, 8, 12)))),
}


def renderiza(nombre, preview=False):
    fn, mus = EDITS[nombre]
    if preview:
        from PIL import Image
        v = fn()
        d = os.path.join(SALIDA, "preview-" + nombre)
        os.makedirs(d, exist_ok=True)
        for t in (0.5, 2.5, 4.3, 5.9, 6.6, 7.4, 9.2, 13.0, 17.7, 19.4, 19.8, 20.2, 21.0, 21.4, 22.3, 23.0, 23.8, 24.2, 25.0, 26.2, 28.0):
            Image.fromarray(v.frame(t)).resize((360, 640)).save(os.path.join(d, "t%05.2f.png" % t))
        return d
    wav = os.path.join(SALIDA, nombre + ".wav")
    musica.pista(ruta=wav, **mus)
    mp4 = os.path.join(SALIDA, "%s.mp4" % fn().nombre)
    M.render(fn, mp4, audio=wav)
    os.remove(wav)
    return mp4


if __name__ == "__main__":
    nombres = list(EDITS) if sys.argv[1] == "todos" else [sys.argv[1]]
    for n in nombres:
        print(renderiza(n, preview="--preview" in sys.argv))
