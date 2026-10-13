import requests
from datetime import datetime, timedelta


# =========================================================
# CONFIGURACIÓN SECOP II
# =========================================================

SECOP_DATASET_ID = "p6dx-8zbt"

SECOP_API_URL = (
    f"https://www.datos.gov.co/resource/"
    f"{SECOP_DATASET_ID}.json"
)

TIMEOUT = 30


# =========================================================
# PALABRAS CLAVE POR LÍNEA INTILED
# =========================================================

PALABRAS_SECTOR = {

    "Energía solar": [
        "solar",
        "fotovoltaico",
        "fotovoltaica",
        "panel solar",
        "paneles solares",
        "sistema fotovoltaico",
        "energía solar"
    ],

    "Alumbrado público": [
        "alumbrado público",
        "alumbrado publico",
        "luminaria",
        "luminarias",
        "iluminación pública",
        "iluminacion publica"
    ],

    "Transición energética": [
        "transición energética",
        "transicion energetica",
        "energías renovables",
        "energias renovables",
        "descarbonización",
        "descarbonizacion"
    ],

    "Eficiencia energética": [
        "eficiencia energética",
        "eficiencia energetica",
        "ahorro energético",
        "ahorro energetico",
        "gestión energética",
        "gestion energetica"
    ],

    "Infraestructura eléctrica": [
        "infraestructura eléctrica",
        "infraestructura electrica",
        "red eléctrica",
        "red electrica",
        "subestación",
        "subestacion",
        "instalaciones eléctricas",
        "instalaciones electricas"
    ],

    "Smart Cities": [
        "smart city",
        "smart cities",
        "ciudad inteligente",
        "ciudades inteligentes"
    ],

    "IoT y telegestión": [
        "iot",
        "internet de las cosas",
        "telegestión",
        "telegestion",
        "telemetría",
        "telemetria",
        "monitoreo remoto"
    ],

    "Comunidades energéticas": [
        "comunidad energética",
        "comunidades energéticas",
        "comunidad energetica",
        "comunidades energeticas"
    ],

    "Consultoría": [
        "consultoría",
        "consultoria",
        "estudios",
        "diseños"
    ],

    "Interventoría": [
        "interventoría",
        "interventoria"
    ],

    "Estudios técnicos": [
        "estudio técnico",
        "estudios técnicos",
        "estudio tecnico",
        "estudios tecnicos",
        "diseño eléctrico",
        "diseño electrico"
    ],

    "Tecnología e innovación": [
        "innovación",
        "innovacion",
        "tecnología",
        "tecnologia",
        "transformación digital",
        "transformacion digital"
    ]
}


# =========================================================
# LIMPIAR TEXTO
# =========================================================

def limpiar_texto(texto):

    if texto is None:
        return ""

    return str(texto).strip()


# =========================================================
# NORMALIZAR SECTOR
# =========================================================

def obtener_palabras_sector(sectores):

    palabras = []

    for sector in sectores:

        palabras_sector = PALABRAS_SECTOR.get(
            sector,
            []
        )

        palabras.extend(
            palabras_sector
        )

    # Eliminar duplicados
    return list(dict.fromkeys(palabras))


# =========================================================
# CONSTRUIR FILTRO DE BÚSQUEDA
# =========================================================

def construir_filtro_palabras(palabras):

    condiciones = []

    for palabra in palabras:

        palabra_segura = palabra.replace(
            "'",
            "''"
        )

        condicion = (
            "lower(descripci_n_del_procedimiento) "
            f"like '%{palabra_segura.lower()}%'"
        )

        condiciones.append(
            condicion
        )

    if not condiciones:
        return ""

    return "(" + " OR ".join(condiciones) + ")"


# =========================================================
# CONSULTAR SECOP
# =========================================================

def consultar_secop(
    sectores,
    limite=50,
    dias_atras=120
):

    palabras = obtener_palabras_sector(
        sectores
    )

    if not palabras:
        return []

    filtro_palabras = construir_filtro_palabras(
        palabras
    )

    # Buscar principalmente procesos recientes
    fecha_desde = (
        datetime.now()
        - timedelta(days=dias_atras)
    ).strftime("%Y-%m-%dT00:00:00")

    filtro_fecha = (
        f"fecha_de_publicacion_del >= "
        f"'{fecha_desde}'"
    )

    where = (
        f"{filtro_palabras} "
        f"AND {filtro_fecha}"
    )

    params = {
        "$limit": limite,
        "$where": where,
        "$order": "fecha_de_publicacion_del DESC"
    }

    try:

        respuesta = requests.get(
            SECOP_API_URL,
            params=params,
            timeout=TIMEOUT
        )

        respuesta.raise_for_status()

        datos = respuesta.json()

        return normalizar_resultados(
            datos,
            sectores
        )

    except requests.exceptions.Timeout:

        raise Exception(
            "SECOP tardó demasiado tiempo "
            "en responder."
        )

    except requests.exceptions.ConnectionError:

        raise Exception(
            "No fue posible conectarse con "
            "Datos Abiertos de Colombia."
        )

    except requests.exceptions.HTTPError:

        detalle = ""

        try:
            detalle = respuesta.text[:500]
        except Exception:
            pass

        raise Exception(
            "SECOP respondió con un error HTTP. "
            + detalle
        )

    except Exception as error:

        raise Exception(
            f"Error consultando SECOP: {error}"
        )


# =========================================================
# IDENTIFICAR SECTOR
# =========================================================

def identificar_sector(texto, sectores):

    texto = limpiar_texto(
        texto
    ).lower()

    for sector in sectores:

        palabras = PALABRAS_SECTOR.get(
            sector,
            []
        )

        for palabra in palabras:

            if palabra.lower() in texto:
                return sector

    return (
        sectores[0]
        if sectores
        else "No identificado"
    )


# =========================================================
# FORMATEAR VALOR
# =========================================================

def formatear_valor(valor):

    if valor in [
        None,
        "",
        "No definido"
    ]:
        return "No disponible"

    try:

        numero = float(valor)

        return (
            "$"
            + f"{numero:,.0f}"
            .replace(",", ".")
            + " COP"
        )

    except Exception:

        return str(valor)


# =========================================================
# FORMATEAR FECHA
# =========================================================

def formatear_fecha(fecha):

    if not fecha:
        return "No disponible"

    try:

        fecha_objeto = datetime.fromisoformat(
            fecha.replace(
                "Z",
                "+00:00"
            )
        )

        return fecha_objeto.strftime(
            "%d/%m/%Y"
        )

    except Exception:

        return fecha


# =========================================================
# NORMALIZAR RESULTADOS
# =========================================================

def normalizar_resultados(
    datos,
    sectores
):

    oportunidades = []

    for item in datos:

        descripcion = limpiar_texto(
            item.get(
                "descripci_n_del_procedimiento"
            )
        )

        referencia = limpiar_texto(
            item.get(
                "referencia_del_proceso"
            )
        )

        entidad = limpiar_texto(
            item.get(
                "entidad"
            )
        )

        departamento = limpiar_texto(
            item.get(
                "departamento_entidad"
            )
        )

        ciudad = limpiar_texto(
            item.get(
                "ciudad_entidad"
            )
        )

        modalidad = limpiar_texto(
            item.get(
                "modalidad_de_contratacion"
            )
        )

        estado = limpiar_texto(
            item.get(
                "estado_del_procedimiento"
            )
        )

        valor = item.get(
            "precio_base"
        )

        fecha_publicacion = item.get(
            "fecha_de_publicacion_del"
        )

        fecha_recepcion = item.get(
            "fecha_de_recepcion_de"
        )

        id_proceso = limpiar_texto(
            item.get(
                "id_del_proceso"
            )
        )

        url_proceso = ""

        url_objeto = item.get(
            "urlproceso"
        )

        if isinstance(
            url_objeto,
            dict
        ):

            url_proceso = url_objeto.get(
                "url",
                ""
            )

        elif isinstance(
            url_objeto,
            str
        ):

            url_proceso = url_objeto

        sector = identificar_sector(
            descripcion,
            sectores
        )

        oportunidad = {

            # Compatibilidad con radar.py
            "pais": "Colombia",

            "fuente": "SECOP II",

            "sector": sector,

            "titulo": (
                descripcion
                if descripcion
                else referencia
            ),

            "url": url_proceso,

            "fecha_deteccion": (
                datetime.now()
                .strftime("%d/%m/%Y %H:%M")
            ),

            # Información SECOP
            "entidad": entidad,

            "referencia": referencia,

            "id_proceso": id_proceso,

            "departamento": departamento,

            "ciudad": ciudad,

            "modalidad": modalidad,

            "estado": estado,

            "valor": formatear_valor(
                valor
            ),

            "valor_numerico": valor,

            "fecha_publicacion": (
                formatear_fecha(
                    fecha_publicacion
                )
            ),

            "fecha_cierre": (
                formatear_fecha(
                    fecha_recepcion
                )
            ),

            "descripcion": descripcion
        }

        oportunidades.append(
            oportunidad
        )

    return oportunidades
