# ============================================================
# INTI PROJECTS AI
# BASE DE EXPERIENCIA ACREDITABLE - INTILED
# ============================================================
#
# OBJETIVO:
# Registrar exclusivamente experiencia que pueda ser utilizada
# para evaluar requisitos de convocatorias.
#
# REGLA FUNDAMENTAL:
# Experiencia de la empresa != experiencia del profesional.
#
# Los contratos reales se incorporarán progresivamente a esta
# base cuando exista información y soporte suficiente.
# ============================================================


EXPERIENCIA_INTILED = []


# ============================================================
# PLANTILLA OFICIAL DE EXPERIENCIA
# ============================================================

PLANTILLA_EXPERIENCIA = {

    # --------------------------------------------------------
    # IDENTIFICACIÓN
    # --------------------------------------------------------

    "id": "",

    "tipo_experiencia": "empresa",
    # empresa
    # consorcio
    # union_temporal
    # profesional

    "empresa": "INTILED S.A.S. BIC",

    "numero_contrato": "",

    "cliente": "",

    "entidad_tipo": "",
    # publica
    # privada
    # cooperacion
    # multilateral

    "objeto": "",


    # --------------------------------------------------------
    # UBICACIÓN
    # --------------------------------------------------------

    "pais": "Colombia",

    "departamento": "",

    "municipio": "",


    # --------------------------------------------------------
    # FECHAS
    # --------------------------------------------------------

    "fecha_inicio": "",

    "fecha_fin": "",

    "estado": "",
    # ejecutado
    # liquidado
    # en_ejecucion


    # --------------------------------------------------------
    # INFORMACIÓN ECONÓMICA
    # --------------------------------------------------------

    "valor_contrato": 0,

    "moneda": "COP",

    "porcentaje_participacion": 100,

    "valor_acreditable": 0,


    # --------------------------------------------------------
    # COMPONENTES TÉCNICOS
    # --------------------------------------------------------

    "componentes": [],

    # Ejemplos:
    #
    # alumbrado_publico
    # iluminacion_led
    # energia_solar
    # sistemas_fotovoltaicos
    # redes_electricas
    # eficiencia_energetica
    # telegestion
    # automatizacion
    # smart_cities
    # interventoria
    # consultoria
    # estudios_tecnicos
    # disenos_electricos


    # --------------------------------------------------------
    # ALCANCE
    # --------------------------------------------------------

    "alcance": [],

    # Ejemplos:
    #
    # suministro
    # instalacion
    # diseno
    # construccion
    # mantenimiento
    # puesta_en_operacion
    # legalizacion
    # consultoria
    # interventoria
    # supervision
    # estructuracion


    # --------------------------------------------------------
    # MAGNITUDES
    # --------------------------------------------------------

    "magnitudes": {

        "numero_luminarias": None,

        "potencia_fotovoltaica_kwp": None,

        "numero_paneles": None,

        "numero_puntos": None,

        "longitud_red_km": None
    },


    # --------------------------------------------------------
    # SOPORTES
    # --------------------------------------------------------

    "soportes": {

        "contrato": False,

        "certificado_experiencia": False,

        "acta_recibo": False,

        "acta_liquidacion": False,

        "factura": False,

        "rup": False
    },


    # --------------------------------------------------------
    # VERIFICACIÓN
    # --------------------------------------------------------

    "verificado": False,

    "nivel_confianza": "pendiente",

    # verificado
    # alto
    # medio
    # bajo
    # pendiente

    "observaciones": ""
}


# ============================================================
# FUNCIONES
# ============================================================

def obtener_experiencia_intiled():
    """
    Retorna toda la experiencia empresarial registrada.
    """
    return EXPERIENCIA_INTILED


def obtener_experiencia_verificada():
    """
    Retorna únicamente experiencia marcada como verificada.
    """

    return [
        experiencia
        for experiencia in EXPERIENCIA_INTILED
        if experiencia.get("verificado") is True
    ]


def obtener_experiencia_por_componente(componente):
    """
    Busca contratos relacionados con un componente técnico.
    """

    resultados = []

    for experiencia in EXPERIENCIA_INTILED:

        componentes = experiencia.get(
            "componentes",
            []
        )

        if componente in componentes:
            resultados.append(experiencia)

    return resultados


def calcular_valor_acreditable(
    valor_contrato,
    porcentaje_participacion
):
    """
    Calcula el valor correspondiente a la participación
    de INTILED en un contrato asociativo.
    """

    if not valor_contrato:
        return 0

    if not porcentaje_participacion:
        return 0

    return (
        valor_contrato
        * porcentaje_participacion
        / 100
    )
