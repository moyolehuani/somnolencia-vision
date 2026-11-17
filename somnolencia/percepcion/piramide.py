"""
Pirámide gaussiana y banda laplaciana (práctica 6).

La pirámide es la misma imagen a varios tamaños, cada uno la mitad del
anterior. Sirve para buscar el rostro de grueso a fino: primero en la
imagen más pequeña, donde hay pocos pixeles que revisar, y después se
afina la posición en la imagen siguiente.

La banda laplaciana es la imagen menos su versión suavizada. Conserva los
bordes y los detalles y descarta los cambios lentos de brillo, así que
depende poco de la iluminación.
"""

from somnolencia.percepcion.preproceso import suavizar_binomial


def reducir(img):
    """
    Reduce la imagen a la mitad de ancho y de alto.

    Primero se suaviza con el filtro binomial y después se conserva un
    pixel de cada dos en cada dirección. El suavizado va primero para que
    los detalles finos no aparezcan como patrones falsos al quitar pixeles.
    """
    return suavizar_binomial(img)[::2, ::2]


def piramide_gaussiana(img, niveles):
    """
    Entrega una lista con la imagen a varios tamaños, de la más grande a la
    más pequeña. El primer elemento es la imagen original.

    Ejemplo con 3 niveles y una imagen de 640x360: 640x360, 320x180, 160x90.
    """
    piramide = [img]
    for _ in range(niveles - 1):
        piramide.append(reducir(piramide[-1]))
    return piramide


def banda_laplaciana(img):
    """La imagen menos su versión suavizada: bordes y detalles, sin el brillo general."""
    return img - suavizar_binomial(img)
