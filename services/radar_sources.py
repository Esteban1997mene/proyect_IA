
# ============================================================
# INTI PROJECTS ENTERPRISE
# INTILED SAS BIC
#
# services/radar_sources.py
#
# RADAR SECOP II - COLOMBIA
# Version 5.0
#
# Mantiene las funciones utilizadas por radar.py.
#
# Mejoras:
# - Elimina $select para evitar errores de columnas.
# - Usa busqueda textual simple mediante $q.
# - Reduce el tamaño de cada consulta.
# - Añade reintentos controlados.
# - Almacena resultados exitosos en cache.
# - Informa el detalle de errores HTTP 400.
# ============================================================

import re
import time
import unicodedata
from datetime import date, timedelta

import pandas as pd
import requests
import streamlit as st


SECOP_URL = (
    "https://www.datos.gov.co/resource/"
    "p6dx-8zbt.json"
)

CACHE_SEGUNDOS = 600
TIMEOUT = (8, 25)

# Cada búsqueda representa una muestra,
# no una consulta exhaustiva de SECOP II.

BUSQUEDAS = {
    "Alumbrado público": [
        "alumbrado",
        "luminarias",
        "iluminación pública",
    ],
    "Energía solar": [
        "fotovoltaico",
        "energía solar",
        "paneles solares",
    ],
    "Eficiencia energética": [
        "eficiencia energética",
        "ahorro energético",
    ],
    "Ingeniería eléctrica": [
        "subestación",
        "instalaciones eléctricas",
        "redes eléctricas",
    ],
    "Consultoría e interventoría": [
        "interventoría",
        "consultoría",
        "estudios eléctricos",
    ],
    "Tecnología y monitoreo": [
        "automatización",
        "telemetría",
        "monitoreo",
    ],
}

CATEGORIAS = {
    "Alumbrado público": [
        "alumbrado",
        "luminaria",
        "iluminacion publica",
        "iluminacion vial",
    ],
    "Energía solar": [
        "fotovoltaic",
        "energia solar",
        "paneles solares",
        "sistema solar",
    ],
    "Eficiencia energética": [
        "eficiencia energetica",
        "ahorro energetico",
        "gestion energetica",
    ],
    "Ingeniería eléctrica": [
        "subestacion",
        "redes electricas",
        "instalaciones electricas",
        "electrificacion",
    ],
    "Consultoría e interventoría": [
        "interventoria",
        "consultoria",
        "estudios y disenos",
        "formulacion de proyectos",
    ],
    "Tecnología y monitoreo": [
        "automatizacion",
        "telemetria",
        "monitoreo remoto",
        "sensores",
    ],
}

BUSQUEDAS_GENERALES = [
    "alumbrado",
    "fotovoltaico",
    "instalaciones eléctricas",
    "interventoría",
]


# ============================================================
# NORMALIZACIÓN
# ============================================================

def normalizar_texto(valor):
    texto = unicodedata.normalize(
        "NFKD",
        str(valor or "").lower()
    )

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(
            caracter
        )
    )

    return re.sub(
        r"\s+", " ", texto
    ).strip()


def convertir_fecha(valor):
    if not valor:
        return None

    try:
        fecha = pd.to_datetime(
            valor,
            errors="coerce",
        )

        if pd.isna(fecha):
            return None

        return fecha.strftime(
            "%Y-%m-%d"
        )

    except (ValueError, TypeError):
        return None


def convertir_numero(valor):
    if valor is None:
        return None

    try:
        return float(valor)

    except (ValueError, TypeError):
        return None


def clasificar_categoria(
    titulo,
    descripcion
):
    texto = normalizar_texto(
        f"{titulo} {descripcion}"
    )

    resultado = []

    for categoria, palabras in (
        CATEGORIAS.items()
    ):
        if any(
            normalizar_texto(
                palabra
            ) in texto
            for palabra in palabras
        ):
            resultado.append(
                categoria
            )

    return resultado


def obtener_enlace(valor):
    if isinstance(valor, dict):
        return str(
            valor.get("url")
            or valor.get("href")
            or ""
        )

    if isinstance(valor, str):
        if valor.startswith(
            ("http://", "https://")
        ):
            return valor

    return ""


# ============================================================
# NORMALIZAR REGISTRO SECOP
# ============================================================

def normalizar_colombia(fila):
    titulo = str(
        fila.get(
            "nombre_del_procedimiento"
        )
        or ""
    )

    descripcion = str(
        fila.get(
            "descripci_n_del_procedimiento"
        )
        or ""
    )

    return {
        "pais": "Colombia",
        "titulo": titulo,
        "descripcion": descripcion,

        "entidad": str(
            fila.get("entidad")
            or ""
        ),

        "region": str(
            fila.get(
                "departamento_entidad"
            )
            or "Sin determinar"
        ),

        "localidad": str(
            fila.get(
                "ciudad_entidad"
            )
            or "Sin determinar"
        ),

        "presupuesto": convertir_numero(
            fila.get("precio_base")
        ),

        "moneda": "COP",

        "fecha_publicacion": convertir_fecha(
            fila.get(
                "fecha_de_publicacion_del"
            )
        ),

        "fecha_cierre": convertir_fecha(
            fila.get(
                "fecha_de_recepcion_de_respuestas"
            )
        ),

        "codigo": str(
            fila.get("id_del_proceso")
            or fila.get(
                "referencia_del_proceso"
            )
            or ""
        ),

        "enlace": obtener_enlace(
            fila.get("urlproceso")
        ),

        "estado": str(
            fila.get(
                "estado_del_procedimiento"
            )
            or ""
        ),

        "fuente": (
            "SECOP II - Datos abiertos"
        ),

        "tipo_ubicacion": (
            "Ubicación registrada "
            "de la entidad"
        ),

        "ubicacion_confirmada": False,

        "categorias": clasificar_categoria(
            titulo,
            descripcion,
        ),
    }


# ============================================================
# ERRORES SECOP
# ============================================================

class ErrorSECOP(Exception):
    pass


def detalle_error(respuesta):
    """
    Recupera información del HTTP 400
    sin mostrar datos de autenticación.
    """

    codigo = respuesta.status_code

    try:
        datos = respuesta.json()
    except ValueError:
        datos = {}

    if not isinstance(datos, dict):
        datos = {}

    mensaje = str(
        datos.get("message")
        or datos.get("error")
        or ""
    )

    codigo_error = str(
        datos.get("code")
        or ""
    )

    # Evitar mensajes excesivamente largos.
    mensaje = mensaje[:350]

    if codigo == 400:
        return (
            "SECOP rechazó la consulta "
            "(HTTP 400). "
            f"Código: {codigo_error or 'N/D'}. "
            f"Detalle: {mensaje or 'No disponible'}"
        )

    if codigo == 429:
        return (
            "SECOP está limitando "
            "temporalmente las solicitudes "
            "(HTTP 429)."
        )

    if codigo in (401, 403):
        return (
            "SECOP rechazó el acceso "
            f"(HTTP {codigo})."
        )

    if codigo >= 500:
        return (
            "SECOP presenta una falla "
            f"del servidor (HTTP {codigo})."
        )

    return (
        "SECOP respondió con "
        f"HTTP {codigo}."
    )


# ============================================================
# REALIZAR SOLICITUD HTTP
# ============================================================

def peticion_secop(parametros):
    ultimo_error = None

    for intento in range(2):

        try:
            respuesta = requests.get(
                SECOP_URL,
                params=parametros,
                timeout=TIMEOUT,
                headers={
                    "Accept": (
                        "application/json"
                    ),
                    "User-Agent": (
                        "INTI-Projects/5.0"
                    ),
                },
            )

            if respuesta.ok:
                datos = respuesta.json()

                if not isinstance(
                    datos, list
                ):
                    raise ErrorSECOP(
                        "SECOP devolvió un "
                        "formato inesperado."
                    )

                return datos

            ultimo_error = detalle_error(
                respuesta
            )

            # Un HTTP 400 no mejora
            # repitiendo la misma consulta.
            if respuesta.status_code in (
                400, 401, 403, 404
            ):
                raise ErrorSECOP(
                    ultimo_error
                )

        except requests.exceptions.Timeout:
            ultimo_error = (
                "SECOP agotó el tiempo "
                "de respuesta."
            )

        except requests.exceptions.ConnectionError:
            ultimo_error = (
                "No se pudo establecer "
                "conexión con SECOP."
            )

        except requests.exceptions.RequestException:
            ultimo_error = (
                "Error de red al "
                "consultar SECOP."
            )

        except ValueError:
            raise ErrorSECOP(
                "SECOP devolvió un JSON "
                "que no pudo interpretarse."
            )

        if intento == 0:
            time.sleep(1)

    raise ErrorSECOP(
        ultimo_error
        or "SECOP no respondió."
    )


# ============================================================
# CONSULTA CON CACHE
# ============================================================

@st.cache_data(
    ttl=CACHE_SEGUNDOS,
    show_spinner=False,
    max_entries=50,
)
def consulta_cache(
    palabra,
    desde,
    limite,
):
    """
    No utiliza $select ni filtros
    complejos de texto.

    $q realiza búsqueda textual.
    $where limita la publicación
    por fecha.
    """

    parametros = {
        "$where": (
            "fecha_de_publicacion_del >= "
            f"'{desde}T00:00:00'"
        ),

        "$order": (
            "fecha_de_publicacion_del DESC"
        ),

        "$limit": int(limite),
    }

    if palabra:
        parametros["$q"] = palabra

    return peticion_secop(
        parametros
    )


# ============================================================
# CONSULTAR COLOMBIA
# ============================================================

def consultar_colombia(
    categoria="Todas",
    busqueda="",
    dias=180,
    limite=300,
):
    """
    Firma compatible con modules/radar.py.

    Devuelve:
      (resultados, None)
      ([], mensaje_error)

    Las búsquedas son muestras limitadas,
    no coberturas exhaustivas.
    """

    try:
        dias = max(
            1,
            min(int(dias), 3650)
        )

        limite = max(
            1,
            min(int(limite), 500)
        )

    except (ValueError, TypeError):
        return [], (
            "Los parámetros de búsqueda "
            "no son válidos."
        )

    desde = (
        date.today()
        - timedelta(days=dias)
    ).isoformat()

    busqueda = str(
        busqueda or ""
    ).strip()

    if busqueda:
        terminos = [busqueda]

    elif categoria in BUSQUEDAS:
        terminos = BUSQUEDAS[
            categoria
        ]

    else:
        terminos = (
            BUSQUEDAS_GENERALES
        )

    # Distribuir los resultados entre
    # las búsquedas.
    #
    # No consultar miles de registros
    # de una sola vez.

    cantidad_por_termino = max(
        30,
        min(
            100,
            (limite // len(terminos)) + 10,
        ),
    )

    registros = []
    errores = []
    consultas_exitosas = 0

    for termino in terminos:

        try:
            datos = consulta_cache(
                termino,
                desde,
                cantidad_por_termino,
            )

            consultas_exitosas += 1

            registros.extend(datos)

        except ErrorSECOP as error:
            errores.append(
                f"{termino}: {error}"
            )

    if consultas_exitosas == 0:
        return [], (
            errores[0]
            if errores
            else (
                "No fue posible consultar "
                "SECOP II."
            )
        )

    resultados = []
    identificadores = set()

    for fila in registros:

        if not isinstance(fila, dict):
            continue

        item = normalizar_colombia(
            fila
        )

        if not item["titulo"]:
            continue

        identificador = (
            item["codigo"]
            or (
                item["titulo"]
                + item["entidad"]
            )
        )

        if identificador in identificadores:
            continue

        identificadores.add(
            identificador
        )

        resultados.append(item)

    # Ordenar de más reciente a más antiguo.
    resultados.sort(
        key=lambda item: (
            item.get(
                "fecha_publicacion"
            )
            or ""
        ),
        reverse=True,
    )

    return resultados[:limite], None


# ============================================================
# OPCIONES TERRITORIALES
# ============================================================

def opciones_territoriales(
    datos,
    campo,
):
    valores = {
        str(
            item.get(campo, "")
        ).strip()

        for item in datos

        if item.get(campo)
        and item.get(campo)
        != "Sin determinar"
    }

    return ["Todas"] + sorted(
        valores
    )


# ============================================================
# FILTROS LOCALES
# ============================================================

def filtrar_oportunidades(
    oportunidades,
    texto="",
    region="Todas",
    localidad="Todas",
    decision="Todas",
    categoria="Todas",
):
    texto = normalizar_texto(
        texto
    )

    resultados = []

    for item in oportunidades:

        if (
            region != "Todas"
            and item.get("region") != region
        ):
            continue

        if (
            localidad != "Todas"
            and item.get("localidad") != localidad
        ):
            continue

        if categoria != "Todas":

            if categoria not in item.get(
                "categorias", []
            ):
                continue

        if decision != "Todas":

            evaluacion = item.get(
                "evaluacion", {}
            )

            if not isinstance(
                evaluacion, dict
            ):
                evaluacion = {}

            if evaluacion.get(
                "decision"
            ) != decision:
                continue

        contenido = normalizar_texto(
            " ".join([
                str(
                    item.get("titulo")
                    or ""
                ),
                str(
                    item.get("descripcion")
                    or ""
                ),
                str(
                    item.get("entidad")
                    or ""
                ),
                str(
                    item.get("codigo")
                    or ""
                ),
            ])
        )

        if (
            texto
            and texto not in contenido
        ):
            continue

        resultados.append(item)

    return resultados


# ============================================================
# ESTADO DE VIGENCIA
# ============================================================

def estado_vigencia(item):
    estado = normalizar_texto(
        item.get("estado", "")
    )

    estados_cerrados = (
        "adjudicado",
        "cancelado",
        "desierto",
        "terminado",
        "cerrado",
        "awarded",
        "cancelled",
        "complete",
    )

    if any(
        termino in estado
        for termino in estados_cerrados
    ):
        return "No vigente"

    cierre = item.get(
        "fecha_cierre"
    )

    if cierre:

        try:
            fecha_cierre = (
                date.fromisoformat(
                    str(cierre)
                )
            )

            if (
                fecha_cierre
                < date.today()
            ):
                return "Plazo vencido"

        except ValueError:
            pass

    return "Por verificar"
