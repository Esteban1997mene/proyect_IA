
# ============================================================
# INTI PROJECTS ENTERPRISE
# INTILED SAS BIC
#
# Archivo: services/radar_sources.py
#
# RADAR DE OPORTUNIDADES - COLOMBIA
# Fuente: Datos Abiertos SECOP II
#
# Mejoras:
# - Consultas más pequeñas
# - Reintentos controlados
# - Caché de resultados
# - Normalización de textos
# - Manejo de errores
# - Compatibilidad con modules/radar.py
# ============================================================

import os
import re
import time
import unicodedata
from datetime import date, timedelta

import pandas as pd
import requests
import streamlit as st


# ============================================================
# CONFIGURACIÓN
# ============================================================

SECOP_URL = (
    "https://www.datos.gov.co/resource/"
    "p6dx-8zbt.json"
)

MAX_RESULTADOS = 300
MAX_RESULTADOS_CONSULTA = 500
MAX_REINTENTOS = 2

TIMEOUT_CONEXION = 6
TIMEOUT_LECTURA = 25

CACHE_SEGUNDOS = 600

# Palabras por categoría.
# Conservamos las categorías del Radar original.

CATEGORIAS = {
    "Alumbrado público": [
        "alumbrado",
        "luminarias",
        "iluminacion publica",
        "iluminacion vial",
    ],
    "Energía solar": [
        "fotovoltaico",
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

# Consulta compacta cuando el usuario
# selecciona "Todas".
#
# No es una búsqueda exhaustiva.
# Se priorizan términos directamente
# relacionados con los servicios de INTILED.

PALABRAS_GENERALES = [
    "alumbrado",
    "luminaria",
    "solar",
    "fotovoltaic",
    "subestaci",
    "electric",
    "energetic",
    "interventor",
    "consultor",
    "iluminaci",
    "automatiz",
    "telemetria",
]

# Columnas necesarias para construir
# el expediente sin descargar las demás.

COLUMNAS = [
    "entidad",
    "departamento_entidad",
    "ciudad_entidad",
    "nombre_del_procedimiento",
    "descripci_n_del_procedimiento",
    "precio_base",
    "fecha_de_publicacion_del",
    "fecha_de_recepcion_de_respuestas",
    "id_del_proceso",
    "referencia_del_proceso",
    "urlproceso",
    "estado_del_procedimiento",
]


# ============================================================
# UTILIDADES
# ============================================================

def normalizar_texto(valor):
    texto = unicodedata.normalize(
        "NFKD",
        str(valor or "").lower(),
    )

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    return re.sub(
        r"\s+",
        " ",
        texto,
    ).strip()


def convertir_fecha(valor):
    if not valor:
        return None

    fecha = pd.to_datetime(
        valor,
        errors="coerce",
    )

    if pd.isna(fecha):
        return None

    return fecha.strftime("%Y-%m-%d")


def convertir_numero(valor):
    if valor is None:
        return None

    try:
        return float(valor)

    except (ValueError, TypeError):
        return None


def clasificar_categoria(titulo, descripcion):
    texto = normalizar_texto(
        f"{titulo} {descripcion}"
    )

    categorias = []

    for categoria, palabras in CATEGORIAS.items():
        if any(
            normalizar_texto(palabra) in texto
            for palabra in palabras
        ):
            categorias.append(categoria)

    return categorias


def obtener_enlace(valor):
    if isinstance(valor, dict):
        return str(
            valor.get("url")
            or valor.get("href")
            or ""
        )

    if isinstance(valor, str):
        valor = valor.strip()

        if valor.startswith(
            ("https://", "http://")
        ):
            return valor

    return ""


def normalizar_colombia(fila):
    titulo = str(
        fila.get("nombre_del_procedimiento")
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
            fila.get("departamento_entidad")
            or "Sin determinar"
        ),

        "localidad": str(
            fila.get("ciudad_entidad")
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
            or fila.get("referencia_del_proceso")
            or ""
        ),

        "enlace": obtener_enlace(
            fila.get("urlproceso")
        ),

        "estado": str(
            fila.get("estado_del_procedimiento")
            or ""
        ),

        "fuente": "SECOP II - Datos abiertos",

        "tipo_ubicacion": (
            "Ubicación registrada de la entidad"
        ),

        "ubicacion_confirmada": False,

        "categorias": clasificar_categoria(
            titulo,
            descripcion,
        ),
    }


# ============================================================
# CONSTRUCCIÓN DE CONSULTAS
# ============================================================

def escapar_sql(valor):
    """
    Escapa comillas simples para SoQL.

    Los nombres de columnas no proceden
    de entradas del usuario.
    """
    return str(valor).replace(
        "'", "''"
    )


def variantes_palabra(palabra):
    """
    Agrega variantes frecuentes con tilde.

    El SQL lower() de SECOP no elimina
    necesariamente los acentos.
    """
    palabra = normalizar_texto(palabra)

    variantes = [palabra]

    cambios = {
        "energia": "energía",
        "energetica": "energética",
        "iluminacion": "iluminación",
        "subestacion": "subestación",
        "electrificacion": "electrificación",
        "interventoria": "interventoría",
        "consultoria": "consultoría",
        "automatizacion": "automatización",
        "disenos": "diseños",
        "gestion": "gestión",
        "formulacion": "formulación",
    }

    variante = palabra

    for origen, destino in cambios.items():
        variante = variante.replace(
            origen,
            destino,
        )

    if variante not in variantes:
        variantes.append(variante)

    return variantes


def condicion_texto(palabra, columnas):
    """
    Busca el término en las columnas
    permitidas.

    El filtro se ejecuta en el servidor.
    """

    condiciones = []

    variantes = variantes_palabra(
        palabra
    )

    for variante in variantes:
        termino = escapar_sql(
            variante
        )

        for columna in columnas:
            condiciones.append(
                f"lower({columna}) "
                f"like '%{termino}%'"
            )

    return "(" + " OR ".join(
        condiciones
    ) + ")"


def construir_parametros(
    categoria,
    busqueda,
    dias,
    limite,
    modo="normal",
):
    """
    Construye consultas con menos
    condiciones que la versión anterior.
    """

    dias = max(
        1,
        min(int(dias), 3650),
    )

    limite = max(
        1,
        min(
            int(limite),
            MAX_RESULTADOS_CONSULTA,
        ),
    )

    desde = date.today() - timedelta(
        days=dias
    )

    condiciones = [
        (
            "fecha_de_publicacion_del >= "
            f"'{desde.isoformat()}T00:00:00'"
        )
    ]

    busqueda = str(
        busqueda or ""
    ).strip()

    # Si hay búsqueda específica, priorizar
    # la palabra escrita por el usuario.
    #
    # Puede buscar en título y descripción.

    if busqueda:
        condiciones.append(
            condicion_texto(
                busqueda,
                [
                    "nombre_del_procedimiento",
                    "descripci_n_del_procedimiento",
                ],
            )
        )

    elif categoria in CATEGORIAS:

        palabras = CATEGORIAS[categoria]

        condiciones_categoria = [
            condicion_texto(
                palabra,
                [
                    "nombre_del_procedimiento",
                ],
            )
            for palabra in palabras
        ]

        condiciones.append(
            "("
            + " OR ".join(
                condiciones_categoria
            )
            + ")"
        )

    elif categoria == "Todas":

        # Para "Todas" no consultamos
        # las decenas de combinaciones
        # que empleaba la versión anterior.

        palabras = PALABRAS_GENERALES

        if modo == "reducido":
            palabras = [
                "alumbrado",
                "solar",
                "electric",
                "interventor",
            ]

        condiciones_generales = [
            condicion_texto(
                palabra,
                [
                    "nombre_del_procedimiento",
                ],
            )
            for palabra in palabras
        ]

        condiciones.append(
            "("
            + " OR ".join(
                condiciones_generales
            )
            + ")"
        )

    parametros = {
        "$select": ",".join(COLUMNAS),

        "$where": " AND ".join(
            condiciones
        ),

        "$order": (
            "fecha_de_publicacion_del DESC"
        ),

        "$limit": limite,
    }

    return parametros


# ============================================================
# CONSULTA HTTP CON REINTENTOS
# ============================================================

class ErrorSECOP(Exception):
    pass


def ejecutar_consulta(parametros):
    """
    Reintenta únicamente los fallos
    temporales de conexión o servidor.

    No reintenta errores de consultas
    inválidas (HTTP 400).
    """

    ultimo_error = None

    for intento in range(
        MAX_REINTENTOS
    ):

        try:
            respuesta = requests.get(
                SECOP_URL,
                params=parametros,
                timeout=(
                    TIMEOUT_CONEXION,
                    TIMEOUT_LECTURA,
                ),
                headers={
                    "Accept": "application/json",
                    "User-Agent": (
                        "INTI-Projects/4.0"
                    ),
                },
            )

            if respuesta.status_code == 400:
                raise ErrorSECOP(
                    "SECOP rechazó los filtros "
                    "de búsqueda. Revisa la "
                    "estructura de la consulta."
                )

            if respuesta.status_code in (
                401, 403
            ):
                raise ErrorSECOP(
                    "SECOP rechazó la solicitud "
                    "por restricciones de acceso."
                )

            if respuesta.status_code == 429:
                ultimo_error = (
                    "SECOP está limitando "
                    "temporalmente las consultas."
                )

            elif respuesta.status_code >= 500:
                ultimo_error = (
                    "SECOP presenta un error "
                    "temporal del servidor."
                )

            else:
                respuesta.raise_for_status()

                datos = respuesta.json()

                if not isinstance(
                    datos, list
                ):
                    raise ErrorSECOP(
                        "SECOP devolvió un formato "
                        "de respuesta inesperado."
                    )

                return datos

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ):
            ultimo_error = (
                "SECOP II no respondió "
                "dentro del tiempo disponible."
            )

        except (
            requests.exceptions.RequestException
        ):
            raise ErrorSECOP(
                "No se pudo consultar SECOP II. "
                "Revisa la conexión del servicio."
            )

        except ValueError:
            raise ErrorSECOP(
                "SECOP devolvió datos "
                "que no pudieron interpretarse."
            )

        if intento < MAX_REINTENTOS - 1:
            time.sleep(
                1.5 * (intento + 1)
            )

    raise ErrorSECOP(
        ultimo_error
        or "No fue posible conectar con SECOP."
    )


# ============================================================
# CACHÉ DE CONSULTAS
# ============================================================

@st.cache_data(
    ttl=CACHE_SEGUNDOS,
    show_spinner=False,
    max_entries=40,
)
def consultar_api_cache(
    categoria,
    busqueda,
    dias,
    limite,
    dia_consulta,
):
    """
    Cachea solo respuestas exitosas.
    Los errores no se almacenan en caché.
    """

    parametros = construir_parametros(
        categoria,
        busqueda,
        dias,
        limite,
    )

    return ejecutar_consulta(
        parametros
    )


# ============================================================
# CONSULTA PRINCIPAL COLOMBIA
# ============================================================

def consultar_colombia(
    categoria="Todas",
    busqueda="",
    dias=180,
    limite=300,
):
    """
    Firma compatible con modules/radar.py.

    Retorna:
        (lista_oportunidades, None)

    En caso de fallo:
        ([], mensaje_error)
    """

    try:
        dias = max(
            1,
            min(int(dias), 3650),
        )

        limite = max(
            1,
            min(
                int(limite),
                MAX_RESULTADOS,
            ),
        )

        busqueda = str(
            busqueda or ""
        ).strip()

        datos = consultar_api_cache(
            categoria,
            busqueda,
            dias,
            limite,
            date.today().isoformat(),
        )

    except ErrorSECOP as error:

        return [], str(error)

    except (
        TypeError,
        ValueError,
    ):

        return [], (
            "Los parámetros de búsqueda "
            "no son válidos."
        )

    except requests.exceptions.RequestException:

        return [], (
            "Ocurrió un problema de conexión "
            "al consultar SECOP II."
        )

    except Exception:

        return [], (
            "Ocurrió un error inesperado "
            "al consultar SECOP II. "
            "Revisa los registros de Streamlit."
        )

    resultados = []
    identificadores = set()

    for fila in datos:

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

    return resultados, None


# ============================================================
# OPCIONES TERRITORIALES
# ============================================================

def opciones_territoriales(datos, campo):
    valores = {
        str(
            item.get(campo, "")
        ).strip()
        for item in datos
        if item.get(campo)
        and item.get(campo)
        != "Sin determinar"
    }

    return [
        "Todas"
    ] + sorted(valores)


# ============================================================
# FILTRAR OPORTUNIDADES
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

    resultado = []

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

        resultado.append(item)

    return resultado


# ============================================================
# VIGENCIA DE LOS PROCESOS
# ============================================================

def estado_vigencia(item):
    """
    Clasificación conservadora.

    El estado debe confirmarse
    en el proceso oficial de SECOP II.
    """

    estado = normalizar_texto(
        item.get(
            "estado", ""
        )
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
            fecha_cierre = date.fromisoformat(
                str(cierre)
            )

            if fecha_cierre < date.today():
                return "Plazo vencido"

        except ValueError:
            pass

    return "Por verificar"
