from data.intiled_profile import INTILED_PROFILE


def obtener_adn_intiled():
    """
    Devuelve el perfil empresarial completo de INTILED.
    """
    return INTILED_PROFILE


def obtener_lineas_prioritarias():

    return INTILED_PROFILE[
        "lineas_negocio"
    ]["prioridad_alta"]


def obtener_keywords_busqueda():

    normales = INTILED_PROFILE[
        "keywords_positivas"
    ]

    premium = INTILED_PROFILE[
        "keywords_premium"
    ]

    return list(set(normales + premium))


def obtener_mercados_activos():

    mercados = INTILED_PROFILE["mercados"]

    return [
        pais
        for pais, datos in mercados.items()
        if datos["activo"]
    ]


def es_area_no_prioritaria(texto):

    texto = texto.lower()

    exclusiones = INTILED_PROFILE[
        "areas_no_prioritarias"
    ]

    coincidencias = []

    for termino in exclusiones:

        if termino.lower() in texto:
            coincidencias.append(termino)

    return coincidencias


def detectar_afinidad_basica(texto):

    texto = texto.lower()

    normales = INTILED_PROFILE[
        "keywords_positivas"
    ]

    premium = INTILED_PROFILE[
        "keywords_premium"
    ]

    coincidencias_normales = []
    coincidencias_premium = []

    for palabra in normales:

        if palabra.lower() in texto:
            coincidencias_normales.append(palabra)

    for palabra in premium:

        if palabra.lower() in texto:
            coincidencias_premium.append(palabra)

    return {
        "coincidencias": coincidencias_normales,
        "premium": coincidencias_premium,
        "total": len(coincidencias_normales),
        "total_premium": len(coincidencias_premium)
    }
