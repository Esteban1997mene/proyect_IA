# ============================================================
# INTI PROJECTS AI
# SERVICIO SECOP II - COLOMBIA
# ============================================================
#
# Consulta procesos publicados en SECOP II mediante
# Datos Abiertos Colombia / API Socrata.
#
# Este módulo:
# 1. Consulta oportunidades reales.
# 2. Busca por líneas estratégicas INTILED.
# 3. Normaliza los resultados.
# 4. Elimina duplicados.
# 5. Entrega información al Radar INTI.
#
# IMPORTANTE:
# Este módulo NO determina todavía si INTILED cumple
# los requisitos habilitantes de una convocatoria.
# ============================================================


import requests
from datetime import datetime, timedelta


# ============================================================
# CONFIGURACIÓN SECOP
# ============================================================

SECOP_URL = (
    "https://www.datos.gov.co/resource/"
    "p6dx-8zbt.json"
)

TIMEOUT = 30


# ============================================================
# PALABRAS DE BÚSQUEDA POR SECTOR
# ============================================================

PALABRAS_SECTOR = {

    "Energía solar": [
        "solar",
        "fotovoltaico",
        "fotovoltaica",
        "panel solar",
        "paneles solares",
        "sistema solar",
        "sistemas solares"
    ],

    "Alumbrado público": [
        "alumbrado publico",
        "alumbrado público",
        "luminaria",
        "luminarias",
        "iluminacion exterior",
        "iluminación exterior",
        "luminaria solar",
        "luminarias solares"
    ],

    "Transición energética": [
        "transicion energetica",
        "transición energética",
        "energias renovables",
        "energías renovables",
        "descarbonizacion",
        "descarbonización"
    ],

    "Eficiencia energética": [
        "eficiencia energetica",
        "eficiencia energética",
        "ahorro energetico",
        "ahorro energético",
        "gestion energetica",
        "gestión energética"
    ],

    "Infraestructura eléctrica": [
        "infraestructura electrica",
        "infraestructura eléctrica",
        "red electrica",
        "red eléctrica",
        "redes electricas",
        "redes eléctricas",
        "subestacion",
        "subestación",
        "media tension",
        "media tensión",
        "baja tension",
        "baja tensión"
    ],

    "Smart Cities": [
        "smart city",
        "smart cities",
        "ciudad inteligente",
        "ciudades inteligentes"
    ],

    "IoT y telegestión": [
        "iot",
        "telegestion",
        "telegestión",
        "telemetria",
        "telemetría",
        "monitoreo remoto",
        "control remoto"
    ],

    "Comunidades energéticas": [
        "comunidad energetica",
        "comunidad energética",
        "comunidades energeticas",
        "comunidades energéticas"
    ],

    "Consultoría": [
        "consultoria",
        "consultoría"
    ],

    "Interventoría": [
        "interventoria",
        "interventoría"
    ],

    "Estudios técnicos": [
        "estudio tecnico",
        "estudio técnico",
        "estudios tecnicos",
        "estudios técnicos",
        "diagnostico energetico",
        "diagnóstico energético"
    ],

    "Tecnología e innovación": [
        "innovacion",
        "innovación",
        "tecnologia",
        "tecnología",
        "automatizacion",
        "automatización"
    ]
}


# ============================================================
# LIMPIAR TEXTO PARA CONSULTAS SOCRATA
# ============================================================

def limpiar_texto_socrata(texto):

    if not texto:
        return ""

    return str(texto).replace(
        "'",
        "''"
    ).strip()


# ============================================================
# CONSTRUIR CONSULTA DE PALABRAS
# ============================================================

def construir_filtro_palabras(palabras):

    condiciones = []

    for palabra in palabras:

        palabra = limpiar_texto_socrata(
            palabra
        ).lower()

        if not palabra:
            continue

        condiciones.append(
            "lower(descripci_n_del_procedimiento) "
            f"like '%{palabra}%'"
        )

    if not condiciones:
        return ""

    return "(" + " OR ".join(
        condiciones
    ) + ")"


# ============================================================
# OBTENER PALABRAS DE LOS SECTORES SELECCIONADOS
# ============================================================

def obtener_palabras_busqueda(
    sectores,
    palabras_adicionales=None
):

    palabras = []

    for sector in sectores:

        palabras.extend(
            PALABRAS_SECTOR.get(
                sector,
                []
            )
        )

    if palabras_adicionales:

        if isinstance(
            palabras_adicionales,
            str
        ):

            adicionales = [
                palabra.strip()
                for palabra
                in palabras_adicionales.split(",")
                if palabra.strip()
            ]

            palabras.extend(
                adicionales
            )

        elif isinstance(
            palabras_adicionales,
            list
        ):

            palabras.extend(
                palabras_adicionales
            )

    # Eliminar duplicados conservando orden

    return list(
        dict.fromkeys(
            palabras
        )
    )


# ============================================================
# CONVERTIR VALORES NUMÉRICOS
# ============================================================

def convertir_numero(valor):

    if valor is None:
        return 0

    try:
        return float(valor)

    except (
        TypeError,
        ValueError
    ):
        return 0


# ============================================================
# FORMATEAR DINERO
# ============================================================

def formatear_cop(valor):

    numero = convertir_numero(
        valor
    )

    if numero <= 0:
        return "No informado"

    return (
        "$"
        + f"{numero:,.0f}"
        .replace(",", ".")
        + " COP"
    )


# ============================================================
# FORMATEAR FECHA
# ============================================================

def formatear_fecha(fecha):

    if not fecha:
        return "No informada"

    try:

        fecha_obj = datetime.fromisoformat(
            fecha.replace(
                "Z",
                "+00:00"
            )
        )

        return fecha_obj.strftime(
            "%d/%m/%Y"
        )

    except (
        ValueError,
        TypeError
    ):

        return str(fecha)


# ============================================================
# DETECTAR SECTOR DEL RESULTADO
# ============================================================

def detectar_sector(texto):

    texto = (
        texto
        or ""
    ).lower()

    mejores_sectores = []

    mejor_puntaje = 0

    for sector, palabras in (
        PALABRAS_SECTOR.items()
    ):

        puntaje = 0

        for palabra in palabras:

            if palabra.lower() in texto:
                puntaje += 1

        if puntaje > mejor_puntaje:

            mejor_puntaje = puntaje

            mejores_sectores = [
                sector
            ]

        elif (
            puntaje > 0
            and puntaje == mejor_puntaje
        ):

            mejores_sectores.append(
                sector
            )

    if not mejores_sectores:
        return "Otros"

    return ", ".join(
        mejores_sectores
    )


# ============================================================
# NORMALIZAR RESULTADO SECOP
# ============================================================

def normalizar_proceso(
    proceso
):

    descripcion = proceso.get(
        "descripci_n_del_procedimiento",
        ""
    )

    entidad = proceso.get(
        "entidad",
        "No informada"
    )

    referencia = proceso.get(
        "referencia_del_proceso",
        "Sin referencia"
    )

    id_proceso = (
        proceso.get(
            "id_del_proceso"
        )
        or proceso.get(
            "proceso_de_compra"
        )
        or referencia
    )

    valor = convertir_numero(
        proceso.get(
            "precio_base",
            0
        )
    )

    fecha_publicacion = proceso.get(
        "fecha_de_publicacion_del"
    )

    fecha_cierre = (
        proceso.get(
            "fecha_de_recepcion_de"
        )
        or proceso.get(
            "fecha_de_recepcion_de_respuestas"
        )
    )

    url = (
        proceso.get(
            "urlproceso"
        )
        or proceso.get(
            "url_proceso"
        )
        or ""
    )

    texto_sector = (
        f"{descripcion} "
        f"{proceso.get('modalidad_de_contratacion', '')}"
    )

    return {

        "pais":
            "🇨🇴 Colombia",

        "fuente":
            "SECOP II",

        "id_proceso":
            str(id_proceso),

        "referencia":
            referencia,

        "titulo":
            descripcion
            if descripcion
            else referencia,

        "proyecto":
            descripcion
            if descripcion
            else referencia,

        "descripcion":
            descripcion,

        "entidad":
            entidad,

        "sector":
            detectar_sector(
                texto_sector
            ),

        "departamento":
            proceso.get(
                "departamento_entidad",
                "No informado"
            ),

        "ciudad":
            proceso.get(
                "ciudad_entidad",
                "No informada"
            ),

        "modalidad":
            proceso.get(
                "modalidad_de_contratacion",
                "No informada"
            ),

        "estado":
            proceso.get(
                "estado_del_procedimiento",
                "No informado"
            ),

        "valor_numerico":
            valor,

        "valor":
            formatear_cop(
                valor
            ),

        "presupuesto":
            formatear_cop(
                valor
            ),

        "fecha_publicacion":
            formatear_fecha(
                fecha_publicacion
            ),

        "fecha_publicacion_raw":
            fecha_publicacion,

        "fecha_cierre":
            formatear_fecha(
                fecha_cierre
            ),

        "cierre":
            formatear_fecha(
                fecha_cierre
            ),

        "fecha_cierre_raw":
            fecha_cierre,

        "url":
            url,

        "fecha_deteccion":
            datetime.now().isoformat(),

        # Todavía NO afirmamos elegibilidad

        "elegibilidad":
            "PENDIENTE_ANALISIS",

        "score_validado":
            None
    }


# ============================================================
# ELIMINAR DUPLICADOS
# ============================================================

def eliminar_duplicados(
    oportunidades
):

    resultados = []

    vistos = set()

    for oportunidad in oportunidades:

        clave = (
            oportunidad.get(
                "id_proceso"
            )
            or oportunidad.get(
                "url"
            )
            or oportunidad.get(
                "referencia"
            )
            or oportunidad.get(
                "titulo"
            )
        )

        clave = str(
            clave
        ).strip().lower()

        if not clave:
            continue

        if clave in vistos:
            continue

        vistos.add(
            clave
        )

        resultados.append(
            oportunidad
        )

    return resultados


# ============================================================
# CONSULTAR SECOP
# ============================================================

def consultar_secop(
    sectores,
    palabras_adicionales=None,
    dias_atras=90,
    limite=100
):

    # --------------------------------------------------------
    # OBTENER PALABRAS
    # --------------------------------------------------------

    palabras = obtener_palabras_busqueda(
        sectores,
        palabras_adicionales
    )

    if not palabras:

        return []


    # --------------------------------------------------------
    # FILTRO DE PALABRAS
    # --------------------------------------------------------

    filtro_palabras = (
        construir_filtro_palabras(
            palabras
        )
    )


    # --------------------------------------------------------
    # FECHA MÍNIMA
    # --------------------------------------------------------

    fecha_minima = (
        datetime.now()
        - timedelta(
            days=dias_atras
        )
    ).strftime(
        "%Y-%m-%dT00:00:00.000"
    )


    # --------------------------------------------------------
    # CONSULTA WHERE
    # --------------------------------------------------------

    condiciones = [

        filtro_palabras,

        (
            "fecha_de_publicacion_del "
            f">= '{fecha_minima}'"
        )
    ]

    where = " AND ".join(
        condicion
        for condicion in condiciones
        if condicion
    )


    # --------------------------------------------------------
    # PARÁMETROS SOCRATA
    # --------------------------------------------------------

    params = {

        "$limit":
            limite,

        "$order":
            "fecha_de_publicacion_del DESC",

        "$where":
            where
    }


    # --------------------------------------------------------
    # SOLICITUD
    # --------------------------------------------------------

    try:

        response = requests.get(
            SECOP_URL,
            params=params,
            timeout=TIMEOUT
        )

        response.raise_for_status()

        datos = response.json()

    except requests.exceptions.Timeout:

        print(
            "INTI: SECOP no respondió "
            "dentro del tiempo esperado."
        )

        return []

    except requests.exceptions.RequestException as error:

        print(
            "INTI: Error consultando SECOP:",
            error
        )

        return []

    except ValueError:

        print(
            "INTI: SECOP devolvió una "
            "respuesta no válida."
        )

        return []


    # --------------------------------------------------------
    # NORMALIZACIÓN
    # --------------------------------------------------------

    oportunidades = []

    for proceso in datos:

        try:

            oportunidad = (
                normalizar_proceso(
                    proceso
                )
            )

            oportunidades.append(
                oportunidad
            )

        except Exception as error:

            print(
                "INTI: Error normalizando "
                "proceso SECOP:",
                error
            )


    # --------------------------------------------------------
    # DUPLICADOS
    # --------------------------------------------------------

    oportunidades = eliminar_duplicados(
        oportunidades
    )

    return oportunidades


# ============================================================
# PRUEBA DIRECTA
# ============================================================

if __name__ == "__main__":

    resultados = consultar_secop(

        sectores=[
            "Energía solar",
            "Alumbrado público",
            "Eficiencia energética"
        ],

        dias_atras=60,

        limite=20
    )

    print(
        "\nOportunidades encontradas:",
        len(resultados)
    )

    for oportunidad in resultados[:5]:

        print("\n")

        print(
            oportunidad[
                "entidad"
            ]
        )

        print(
            oportunidad[
                "titulo"
            ]
        )

        print(
            oportunidad[
                "valor"
            ]
        )

        print(
            oportunidad[
                "fecha_cierre"
            ]
        )
