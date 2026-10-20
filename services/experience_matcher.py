# ============================================================
# INTI PROJECTS AI
# MOTOR DE COMPATIBILIDAD DE EXPERIENCIA
# ============================================================

from data.intiled_experience import (
    obtener_experiencia_intiled
)

from data.intiled_team import (
    obtener_equipo_intiled
)


# ============================================================
# EXPERIENCIA EMPRESARIAL
# ============================================================

def buscar_experiencia_empresa(componentes_requeridos):

    experiencias = obtener_experiencia_intiled()

    resultados = []

    for experiencia in experiencias:

        componentes_contrato = experiencia.get(
            "componentes",
            []
        )

        coincidencias = []

        for componente in componentes_requeridos:

            if componente in componentes_contrato:

                coincidencias.append(
                    componente
                )

        if coincidencias:

            resultados.append({

                "contrato": experiencia,

                "coincidencias": coincidencias,

                "cantidad_coincidencias": len(
                    coincidencias
                ),

                "verificado": experiencia.get(
                    "verificado",
                    False
                )
            })

    return resultados


# ============================================================
# EXPERIENCIA PROFESIONAL
# ============================================================

def buscar_equipo_por_componentes(
    componentes_requeridos
):

    profesionales = obtener_equipo_intiled()

    resultados = []

    for profesional in profesionales:

        areas = profesional.get(
            "areas_experiencia",
            []
        )

        coincidencias = []

        for componente in componentes_requeridos:

            if componente in areas:

                coincidencias.append(
                    componente
                )

        if coincidencias:

            resultados.append({

                "profesional": profesional,

                "coincidencias": coincidencias,

                "cantidad_coincidencias": len(
                    coincidencias
                )
            })

    return resultados


# ============================================================
# ANÁLISIS GENERAL
# ============================================================

def analizar_experiencia(
    componentes_requeridos
):

    empresa = buscar_experiencia_empresa(
        componentes_requeridos
    )

    profesionales = buscar_equipo_por_componentes(
        componentes_requeridos
    )

    empresa_verificada = [
        item
        for item in empresa
        if item["verificado"]
    ]

    return {

        "componentes_requeridos":
            componentes_requeridos,

        "experiencia_empresa":
            empresa,

        "experiencia_empresa_verificada":
            empresa_verificada,

        "equipo_relacionado":
            profesionales,

        "cantidad_contratos":
            len(empresa),

        "cantidad_contratos_verificados":
            len(empresa_verificada),

        "cantidad_profesionales":
            len(profesionales)
    }
