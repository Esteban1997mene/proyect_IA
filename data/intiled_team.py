# ============================================================
# INTI PROJECTS AI
# BASE DE EQUIPO PROFESIONAL INTILED
# ============================================================
#
# La experiencia registrada aquí pertenece a las PERSONAS.
# No debe utilizarse automáticamente como experiencia
# empresarial de INTILED.
# ============================================================


EQUIPO_INTILED = []


# ============================================================
# PLANTILLA PROFESIONAL
# ============================================================

PLANTILLA_PROFESIONAL = {

    "id": "",

    "nombre": "",

    "profesion": "",

    "matricula_profesional": "",

    "rol_intiled": "",

    "disponible": True,


    # --------------------------------------------------------
    # FORMACIÓN
    # --------------------------------------------------------

    "formacion": [],

    # Ejemplo:
    #
    # {
    #     "nivel": "Especialización",
    #     "titulo": "...",
    #     "institucion": "...",
    #     "estado": "Graduado"
    # }


    # --------------------------------------------------------
    # EXPERIENCIA GENERAL
    # --------------------------------------------------------

    "experiencia_general_anos": None,


    # --------------------------------------------------------
    # ÁREAS DE EXPERIENCIA
    # --------------------------------------------------------

    "areas_experiencia": [],


    # --------------------------------------------------------
    # EXPERIENCIA ESPECÍFICA
    # --------------------------------------------------------

    "experiencia_especifica": [],

    # Ejemplo:
    #
    # {
    #     "empresa": "",
    #     "proyecto": "",
    #     "cargo": "",
    #     "fecha_inicio": "",
    #     "fecha_fin": "",
    #     "componentes": [],
    #     "soporte": False
    # }


    # --------------------------------------------------------
    # DOCUMENTOS
    # --------------------------------------------------------

    "documentos": {

        "hoja_vida": False,

        "diploma": False,

        "tarjeta_profesional": False,

        "certificados_laborales": False
    },


    "verificado": False,

    "observaciones": ""
}


# ============================================================
# FUNCIONES
# ============================================================

def obtener_equipo_intiled():

    return EQUIPO_INTILED


def obtener_profesionales_verificados():

    return [
        profesional
        for profesional in EQUIPO_INTILED
        if profesional.get("verificado") is True
    ]


def buscar_profesionales_por_area(area):

    resultados = []

    for profesional in EQUIPO_INTILED:

        areas = profesional.get(
            "areas_experiencia",
            []
        )

        if area in areas:
            resultados.append(
                profesional
            )

    return resultados
