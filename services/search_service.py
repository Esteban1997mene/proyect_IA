from services.secop_service import consultar_secop


# =========================================================
# LIMPIAR NOMBRE DEL PAÍS
# =========================================================

def limpiar_pais(pais):

    reemplazos = [
        "🇨🇴 ",
        "🇪🇨 ",
        "🇵🇪 ",
        "🇧🇴 ",
        "🇻🇪 "
    ]

    pais_limpio = pais

    for elemento in reemplazos:

        pais_limpio = pais_limpio.replace(
            elemento,
            ""
        )

    return pais_limpio.strip()


# =========================================================
# ELIMINAR DUPLICADOS
# =========================================================

def eliminar_duplicados(
    oportunidades
):

    resultado = []
    identificadores = set()

    for oportunidad in oportunidades:

        identificador = (
            oportunidad.get("id_proceso")
            or oportunidad.get("url")
            or oportunidad.get("titulo")
        )

        if identificador in identificadores:
            continue

        identificadores.add(
            identificador
        )

        resultado.append(
            oportunidad
        )

    return resultado


# =========================================================
# RADAR GENERAL INTI
# =========================================================

def ejecutar_radar(
    paises,
    sectores
):

    oportunidades = []

    paises_limpios = [
        limpiar_pais(pais)
        for pais in paises
    ]

    # =====================================================
    # COLOMBIA
    # =====================================================

    if "Colombia" in paises_limpios:

        resultados_colombia = consultar_secop(
            sectores=sectores,
            limite=50,
            dias_atras=120
        )

        oportunidades.extend(
            resultados_colombia
        )

    # =====================================================
    # OTROS PAÍSES
    # =====================================================

    # Ecuador, Perú, Bolivia y Venezuela
    # serán incorporados mediante sus respectivos
    # conectores oficiales.

    return eliminar_duplicados(
        oportunidades
    )
