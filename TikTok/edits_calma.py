# -*- coding: utf-8 -*-
r"""
Serie tranquila: los mismos cuatro temas con fundidos, visuales continuos y música ambient.

Uso:
    python3 edits_calma.py todos
    python3 edits_calma.py energia --preview
"""
import os, sys
import plantilla_calma as P
import visuales_calma as VC
import motor as M
import musica

SALIDA = os.path.join(M.AQUI, "videos", "tranquilos")
os.makedirs(SALIDA, exist_ok=True)


def energia():
    return P.construye(dict(
        nombre="01-energia-calma", cabecera="Energía electrostática",
        titulo=["la energía no se queda", "en las cargas"],
        titulo_formula=r"U_e=\frac{\eo}{2}\int E^2\,\dd V",
        capitulos=[
            dict(rotulo="formar el sistema", formula=r"U_e=\frac12\sum_i q_i\,\phi_i", visual=VC.c1_llegada,
                 frase="traer una carga cuesta vencer el campo de las demás"),
            dict(rotulo="densidad de energía", formula=r"u_e=\frac{\eo}{2}\,E^2", visual=VC.c1_dos,
                 frase="donde el campo es intenso, la energía se acumula"),
            dict(rotulo="una esfera cargada", formula=r"U_e=\frac{3Q^2}{20\pi\eo a}", visual=VC.c1_esfera,
                 frase="cinco sextas partes de su energía están fuera de ella"),
            dict(rotulo="dos campos juntos", formula=r"U_e=U_1+U_2+\eo\!\int\vE_1\cdot\vE_2\,\dd V",
                 visual=VC.c1_cruzado, frase="la energía no se suma: los campos se encuentran"),
        ],
        final=r"U_e=\frac{\eo}{2}\int E^2\,\dd V",
        frase=["la energía no está en las cargas,", "vive en el espacio que las rodea"],
    ))


def fuerzas():
    return P.construye(dict(
        nombre="02-earnshaw-calma", cabecera="Teorema de Earnshaw",
        titulo=["nada se sostiene", "solo con cargas"],
        titulo_formula=r"\nabla^2\phi=0",
        capitulos=[
            dict(rotulo="sin valles", formula=r"\nabla^2\phi=0", visual=VC.c2_silla,
                 frase="en el vacío, el potencial no tiene mínimos"),
            dict(rotulo="un punto de silla", formula=r"\partial_x^2\phi>0\quad\Rightarrow\quad\partial_z^2\phi<0",
                 visual=VC.c2_perfiles, frase="lo que sujeta en una dirección, suelta en otra"),
            dict(rotulo="carga constante", formula=r"\vF=-\grad U_e\big|_{Q}", visual=VC.c2_placas,
                 frase="aislado, el sistema busca menos energía"),
            dict(rotulo="potencial constante", formula=r"\vF=+\grad U_e\big|_{\phi}", visual=VC.c2_coaxial,
                 frase="con baterías, busca más capacidad"),
        ],
        final=r"F_\xi=\frac12\,V^2\,\frac{\dd C}{\dd\xi}",
        frase=["no hay equilibrio estable solo con cargas;", "siempre hace falta algo que sujete"],
    ))


def dielectricos():
    return P.construye(dict(
        nombre="03-dielectricos-calma", cabecera="Materiales dieléctricos",
        titulo=["un aislante no conduce,", "pero responde"],
        titulo_formula=r"\vD=\eo\vE+\vP",
        capitulos=[
            dict(rotulo="polarizabilidad", formula=r"\vp=\alpha\,\vE", visual=VC.c3_atomo,
                 frase="cada átomo se estira un poco"),
            dict(rotulo="cargas ligadas", formula=r"\rhoP=-\divg\vP,\qquad\sigmaP=\vP\cdot\nn",
                 visual=VC.c3_red, frase="nadie se mueve, y aun así aparece carga"),
            dict(rotulo="esfera dieléctrica", formula=r"\vE_{\mathrm{int}}=\frac{3}{\er+2}\,\vE_0",
                 visual=VC.c3_barrido, frase="cuanto mayor es la permitividad, más débil es el campo dentro"),
            dict(rotulo="vector desplazamiento", formula=r"\divg\vD=\rhof", visual=VC.c3_D,
                 frase="las líneas de D no se interrumpen"),
        ],
        final=r"\divg\vD=\rhof",
        frase=["el desplazamiento solo ve la carga libre;", "la ligada la pone el material"],
    ))


def cavidades():
    return P.construye(dict(
        nombre="04-cavidades-calma", cabecera="Cavidades en un dieléctrico",
        titulo=["el campo depende", "de la forma del vacío"],
        titulo_formula=r"\vE_{\mathrm{cav}}=\vE_d+N\,\frac{\vP_d}{\eo}",
        capitulos=[
            dict(rotulo="una aguja", formula=r"\vE_{\mathrm{cav}}=\vE_d", visual=VC.c4_aguja,
                 frase="paralela al campo, conserva su componente tangencial"),
            dict(rotulo="una lenteja", formula=r"\vE_{\mathrm{cav}}=\vE_d+\frac{\vP_d}{\eo}", visual=VC.c4_lenteja,
                 frase="atravesada, conserva la normal de D"),
            dict(rotulo="todas las formas", formula=r"\vE_{\mathrm{cav}}=\vE_d+N\,\frac{\vP_d}{\eo}",
                 visual=VC.c4_morfo, frase="de la aguja a la lenteja, N crece de 0 a 1"),
            dict(rotulo="factor de despolarización", formula=r"0\leq N\leq1", visual=VC.c4_curva,
                 frase="en la esfera, N = 1/3: el campo local de Lorentz"),
        ],
        final=r"\vE_{\mathrm{cav}}=\vE_d+N\,\frac{\vP_d}{\eo}",
        frase=["no medimos el campo:", "medimos la forma del hueco desde el que miramos"],
    ))


EDITS = {
    "energia": (energia, dict(raiz=50, semilla=11)),
    "fuerzas": (fuerzas, dict(raiz=45, semilla=12, progresion=((0, 3, 7, 14), (5, 8, 12, 19), (-4, 0, 3, 10),
                                                              (-5, -1, 2, 9), (-2, 2, 5, 12), (0, 3, 7, 14)))),
    "dielectricos": (dielectricos, dict(raiz=52, semilla=13, progresion=((0, 4, 7, 14), (-3, 0, 4, 11), (5, 9, 12, 19),
                                                                        (-5, -1, 2, 9), (2, 5, 9, 16), (0, 4, 7, 14)))),
    "cavidades": (cavidades, dict(raiz=48, semilla=14, progresion=((0, 3, 7, 14), (-5, -2, 2, 9), (-4, 0, 3, 10),
                                                                  (5, 8, 12, 19), (-2, 2, 5, 12), (0, 3, 7, 14)))),
}


def renderiza(nombre, preview=False):
    fn, mus = EDITS[nombre]
    if preview:
        from PIL import Image
        v = fn()
        d = os.path.join(SALIDA, "preview-" + nombre)
        os.makedirs(d, exist_ok=True)
        for t in (1.5, 3.5, 6.0, 8.5, 11.0, 13.5, 16.0, 18.5, 21.0, 23.5, 26.5, 28.5):
            Image.fromarray(v.frame(t)).resize((360, 640)).save(os.path.join(d, "t%05.2f.png" % t))
        return d
    wav = os.path.join(SALIDA, nombre + ".wav")
    musica.pista_calma(ruta=wav, **mus)
    mp4 = os.path.join(SALIDA, "%s.mp4" % fn().nombre)
    M.render(fn, mp4, audio=wav)
    os.remove(wav)
    return mp4


if __name__ == "__main__":
    nombres = list(EDITS) if sys.argv[1] == "todos" else [sys.argv[1]]
    for n in nombres:
        print(renderiza(n, preview="--preview" in sys.argv))
