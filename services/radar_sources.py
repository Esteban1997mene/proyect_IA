
# ============================================================
# INTI PROJECTS ENTERPRISE
# INTILED SAS BIC
# Archivo: services/radar_sources.py
# Radar de oportunidades: Colombia y Ecuador
# ============================================================

import io
import re
import unicodedata
from datetime import date, timedelta

import pandas as pd
import requests


# ============================================================
# FUENTES OFICIALES
# ============================================================

SECOP_URL = (
    "https://www.datos.gov.co/resource/"
    "p6dx-8zbt.json"
)

SERCOP_API = (
    "https://datosabiertos.compraspublicas.gob.ec/"
    "PLATAFORMA/api/search_ocds"
)

SERCOP_RECORD = (
    "https://datosabiertos.compraspublicas.gob.ec/"
    "PLATAFORMA/api/record"
)

SERCOP_URL = (
    "https://datosabiertos.compraspublicas.gob.ec/"
    "PLATAFORMA/busqueda"
)


# ============================================================
# CATEGORÍAS DE PROYECTOS INTILED
# ============================================================

CATEGORIAS = {
    "Alumbrado público": [
        "alumbrado publico",
        "luminarias",
        "iluminacion vial",
        "iluminacion publica",
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
        "instalaciones electricas",
        "redes electricas",
        "electrificacion",
    ],
    "Consultoría e interventoría": [
        "interventoria",
        "consultoria",
        "estudios y disenos",
        "formulacion de proyectos",
    ],
    "Tecnología y monitoreo": [
        "telemetria",
        "automatizacion",
        "monitoreo remoto",
        "ciudad inteligente",
    ],
}


# Palabras utilizadas para consultar las fuentes.

CONSULTAS = {
    "Alumbrado público": [
        "alumbrado",
        "luminarias",
        "iluminacion",
    ],
    "Energía solar": [
        "fotovoltaico",
        "solar",
    ],
    "Eficiencia energética": [
        "eficiencia energetica",
        "energetica",
    ],
    "Ingeniería eléctrica": [
        "subestacion",
        "electrica",
    ],
    "Consultoría e interventoría": [
        "interventoria",
        "consultoria",
    ],
    "Tecnología y monitoreo": [
        "telemetria",
        "automatizacion",
    ],
}


# ============================================================
# PROVINCIAS DE ECUADOR
# ============================================================

PROVINCIAS_ECUADOR = [
    "Azuay",
    "Bolívar",
    "Cañar",
    "Carchi",
    "Chimborazo",
    "Cotopaxi",
    "El Oro",
    "Esmeraldas",
    "Galápagos",
    "Guayas",
    "Imbabura",
    "Loja",
    "Los Ríos",
    "Manabí",
    "Morona Santiago",
    "Napo",
    "Orellana",
    "Pastaza",
    "Pichincha",
    "Santa Elena",
    "Santo Domingo de los Tsáchilas",
    "Sucumbíos",
    "Tungurahua",
    "Zamora Chinchipe",
]


# ============================================================
# FUNCIONES GENERALES
# ============================================================

def normalizar_texto(valor):

    texto = unicodedata.normalize(
        "NFKD",
        str(valor or "").lower()
    )

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    return re.sub(
        r"\s+",
        " ",
        texto
    ).strip()


def clave(valor):

    return re.sub(
        r"[^a-z0-9]+",
        "_",
        normalizar_texto(valor)
    ).strip("_")


def campo(fila, *nombres):

    for nombre in nombres:

        valor = fila.get(clave(nombre))

        if (
            valor is not None
            and str(valor).strip()
        ):
            return str(valor).strip()

    return ""


def convertir_numero(valor):

    texto = re.sub(
        r"[^\d,.-]",
        "",
        str(valor or "")
    )

    if not texto:
        return None

    try:

        if "," in texto and "." in texto:

            if texto.rfind(",") > texto.rfind("."):

                texto = texto.replace(".", "")
                texto = texto.replace(",", ".")

            else:
                texto = texto.replace(",", "")

        elif "," in texto:

            if len(texto.split(",")[-1]) == 3:
                texto = texto.replace(",", "")
            else:
                texto = texto.replace(",", ".")

        elif texto.count(".") > 1:

            texto = texto.replace(".", "")

        return float(texto)

    except ValueError:
        return None


def convertir_fecha(valor):

    if not valor:
        return None

    try:

        fecha = pd.to_datetime(
            valor,
            errors="coerce",
            utc=True
        )

        if pd.isna(fecha):
            return None

        return fecha.strftime("%Y-%m-%d")

    except (TypeError, ValueError):
        return None


# ============================================================
# CLASIFICACIÓN DE PROYECTOS
# ============================================================

def clasificar_categoria(titulo, descripcion):

    texto = normalizar_texto(
        f"{titulo} {descripcion}"
    )

    encontradas = []

    for nombre, terminos in CATEGORIAS.items():

        if any(
            normalizar_texto(termino) in texto
            for termino in terminos
        ):
            encontradas.append(nombre)

    return encontradas


# ============================================================
# NORMALIZACIÓN COLOMBIA
# ============================================================

def normalizar_colombia(fila):

    datos = {
        clave(k): v
        for k, v in fila.items()
    }

    titulo = campo(
        datos,
        "nombre_del_procedimiento",
        "nombre_del_proceso",
        "objeto",
    )

    descripcion = campo(
        datos,
        "descripci_n_del_procedimiento",
        "descripcion_del_procedimiento",
        "descripcion",
    )

    enlace_original = (
        fila.get("urlproceso")
        or fila.get("url_proceso")
        or ""
    )

    if isinstance(enlace_original, dict):

        enlace = enlace_original.get(
            "url",
            ""
        )

    else:

        enlace = str(enlace_original)

    return {
        "pais": "Colombia",

        "titulo": titulo,

        "descripcion": descripcion,

        "entidad": campo(
            datos,
            "entidad",
            "nombre_de_la_entidad",
        ),

        "region": campo(
            datos,
            "departamento_entidad",
            "departamento",
        ) or "Sin determinar",

        "localidad": campo(
            datos,
            "ciudad_entidad",
            "municipio_entidad",
        ) or "Sin determinar",

        "presupuesto": convertir_numero(
            campo(
                datos,
                "precio_base",
                "valor_del_contrato",
            )
        ),

        "moneda": "COP",

        "fecha_cierre": convertir_fecha(
            campo(
                datos,
                "fecha_de_recepcion_de_respuestas",
                "fecha_de_cierre_del_proceso",
            )
        ),

        "fecha_publicacion": convertir_fecha(
            campo(
                datos,
                "fecha_de_publicacion_del",
                "fecha_de_publicacion_del_proceso",
            )
        ),

        "codigo": campo(
            datos,
            "id_del_proceso",
            "referencia_del_proceso",
        ),

        "enlace": enlace,

        "estado": campo(
            datos,
            "estado_del_procedimiento",
            "estado_del_proceso",
        ),

        "fuente": "SECOP II",

        "ubicacion_confirmada": False,

        "tipo_ubicacion": (
            "Sede de entidad contratante"
        ),

        "categorias": clasificar_categoria(
            titulo,
            descripcion,
        ),
    }


# ============================================================
# NORMALIZACIÓN ECUADOR
# ============================================================

def normalizar_ecuador(fila):

    titulo = str(
        fila.get("description")
        or fila.get("title")
        or ""
    )

    descripcion = str(
        fila.get("description")
        or ""
    )

    codigo = str(
        fila.get("ocid")
        or fila.get("id")
        or ""
    )

    return {
        "pais": "Ecuador",

        "titulo": titulo,

        "descripcion": descripcion,

        "entidad": str(
            fila.get("buyerName")
            or ""
        ),

        "region": "Sin determinar",

        "localidad": "Sin determinar",

        "presupuesto": None,

        "moneda": "USD",

        "fecha_cierre": None,

        "fecha_publicacion": convertir_fecha(
            fila.get("date")
        ),

        "codigo": codigo,

        "enlace": "",

        "estado": "No verificado",

        "fuente": "SERCOP - OCDS",

        "ubicacion_confirmada": False,

        "tipo_ubicacion": "No determinada",

        "categorias": clasificar_categoria(
            titulo,
            descripcion,
        ),

        "ocid": codigo,

        "tipo_procedimiento": str(
            fila.get("internal_type")
            or ""
        ),
    }


# ============================================================
# CONSULTAR COLOMBIA - SECOP II
# ============================================================

def consultar_colombia(
    categoria="Todas",
    busqueda="",
    dias=180,
    limite=300,
):

    desde = (
        date.today()
        - timedelta(days=int(dias))
    )

    if categoria != "Todas":

        palabras = list(
            CONSULTAS.get(
                categoria,
                []
            )
        )

    else:

        palabras = [
            palabra
            for grupo in CONSULTAS.values()
            for palabra in grupo
        ]

    if busqueda.strip():

        palabras.insert(
            0,
            busqueda.strip()
        )

    palabras = list(
        dict.fromkeys(palabras)
    )

    condiciones = []

    for palabra in palabras:

        palabra = normalizar_texto(
            palabra
        ).replace("'", "''")

        condiciones.append(
            "("
            "lower(nombre_del_procedimiento) "
            f"like '%{palabra}%' "
            "OR "
            "lower(descripci_n_del_procedimiento) "
            f"like '%{palabra}%'"
            ")"
        )

    where = (
        "fecha_de_publicacion_del >= "
        f"'{desde.isoformat()}T00:00:00'"
    )

    if condiciones:

        where += (
            " AND ("
            + " OR ".join(condiciones)
            + ")"
        )

    try:

        respuesta = requests.get(
            SECOP_URL,

            params={
                "$where": where,

                "$order": (
                    "fecha_de_publicacion_del DESC"
                ),

                "$limit": min(
                    int(limite),
                    1000
                ),
            },

            timeout=(7, 25),

            headers={
                "Accept": "application/json",

                "User-Agent": (
                    "INTI-Projects/2.1"
                ),
            },
        )

        respuesta.raise_for_status()

        datos = respuesta.json()

        if not isinstance(datos, list):

            return [], (
                "SECOP II devolvió "
                "un formato inesperado."
            )

        registros = []

        for fila in datos:

            if not isinstance(fila, dict):
                continue

            registro = normalizar_colombia(
                fila
            )

            if registro["titulo"]:
                registros.append(registro)

        return registros, None

    except requests.RequestException as error:

        return [], (
            "No fue posible consultar SECOP II: "
            f"{type(error).__name__}: {error}"
        )

    except (ValueError, TypeError) as error:

        return [], (
            "No se pudo interpretar la "
            f"respuesta SECOP II: {error}"
        )


# ============================================================
# CONSULTAR ECUADOR - SERCOP
# CONTROL DE TIMEOUT Y ERRORES
# ============================================================

def consultar_ecuador(
    categoria="Todas",
    busqueda="",
    anio=None,
    paginas=2,
):

    """
    Consulta limitada de la API oficial SERCOP.

    Evita realizar múltiples solicitudes
    prolongadas cuando el servidor no responde.

    Conserva los parámetros utilizados
    por modules/radar.py.

    No garantiza que la API esté disponible
    desde Streamlit Cloud.
    """

    anio = int(
        anio or date.today().year
    )

    palabras = []

    if busqueda.strip():

        palabras.append(
            busqueda.strip()
        )

    if categoria != "Todas":

        palabras.extend(
            CONSULTAS.get(
                categoria,
                []
            )
        )

    if not palabras:

        palabras = [
            "alumbrado",
            "solar",
            "fotovoltaico",
            "electrica",
        ]

    # Evita consultas repetidas.
    palabras = list(
        dict.fromkeys(palabras)
    )

    # Máximo tres términos por ejecución.
    palabras = palabras[:3]

    resultados = []
    vistos = set()
    errores = []

    consultas_exitosas = 0

    with requests.Session() as sesion:

        sesion.headers.update({
            "Accept": "application/json",

            "User-Agent": (
                "INTI-Projects/2.1"
            ),
        })

        for palabra in palabras:

            try:

                respuesta = sesion.get(
                    SERCOP_API,

                    params={
                        "year": anio,
                        "search": palabra,
                        "page": 1,
                    },

                    # 5 segundos para conectar.
                    # 12 segundos para recibir datos.
                    timeout=(5, 12),
                )

                respuesta.raise_for_status()

                contenido = respuesta.json()

                if not isinstance(
                    contenido,
                    dict
                ):

                    errores.append(
                        "SERCOP devolvió un "
                        "formato inesperado."
                    )

                    continue

                datos = contenido.get(
                    "data",
                    []
                )

                if not isinstance(
                    datos,
                    list
                ):

                    errores.append(
                        "SERCOP devolvió registros "
                        "con formato inesperado."
                    )

                    continue

                consultas_exitosas += 1

                for fila in datos:

                    if not isinstance(
                        fila,
                        dict
                    ):
                        continue

                    item = normalizar_ecuador(
                        fila
                    )

                    codigo = item.get(
                        "codigo"
                    )

                    if not codigo:
                        continue

                    if codigo in vistos:
                        continue

                    vistos.add(
                        codigo
                    )

                    resultados.append(
                        item
                    )

            except requests.exceptions.ConnectTimeout:

                errores.append(
                    "El servidor oficial SERCOP "
                    "no aceptó la conexión a tiempo."
                )

                # No insistimos con otros términos.
                break

            except requests.exceptions.ReadTimeout:

                errores.append(
                    "SERCOP aceptó la conexión, "
                    "pero no respondió a tiempo."
                )

                break

            except requests.exceptions.RequestException as error:

                errores.append(
                    "Error de comunicación "
                    "con SERCOP "
                    f"({type(error).__name__})."
                )

                break

            except ValueError:

                errores.append(
                    "SERCOP no devolvió "
                    "JSON válido."
                )

                break

    resultados.sort(
        key=lambda item: (
            item.get(
                "fecha_publicacion"
            ) or ""
        ),
        reverse=True,
    )

    # Sin conexión ni consultas exitosas.
    if not consultas_exitosas:

        mensaje = (
            "No fue posible conectar con "
            "la API oficial de SERCOP desde "
            "INTI Projects. Esto no significa "
            "que no existan convocatorias "
            "en Ecuador."
        )

        if errores:
            mensaje += " " + errores[0]

        return [], mensaje

    # Se obtuvieron algunos datos.
    if errores:

        return resultados, (
            "Consulta parcial: algunas "
            "solicitudes a SERCOP "
            "no se completaron."
        )

    return resultados, None


# ============================================================
# DETALLE DE PROCESOS ECUADOR
# ============================================================

def consultar_detalle_ecuador(ocid):

    if not ocid:

        return None, (
            "OCID no disponible."
        )

    try:

        respuesta = requests.get(
            SERCOP_RECORD,

            params={
                "ocid": ocid
            },

            timeout=(5, 12),
        )

        respuesta.raise_for_status()

        return respuesta.json(), None

    except (
        requests.RequestException,
        ValueError
    ) as error:

        return None, (
            "No fue posible recuperar "
            "el detalle SERCOP: "
            f"{type(error).__name__}"
        )


# ============================================================
# ENRIQUECER DATOS ECUADOR
# ============================================================

def enriquecer_ecuador(item, detalle):

    item = dict(item)

    if not isinstance(
        detalle,
        dict
    ):
        return item

    registros = detalle.get(
        "records",
        []
    )

    if not isinstance(
        registros,
        list
    ):
        return item

    for registro in registros:

        entregas = registro.get(
            "releases",
            []
        )

        for entrega in entregas:

            tender = (
                entrega.get(
                    "tender",
                    {}
                ) or {}
            )

            item["estado"] = (
                tender.get("status")
                or item["estado"]
            )

            valor = (
                tender.get(
                    "value",
                    {}
                ) or {}
            )

            if isinstance(
                valor,
                dict
            ):

                if valor.get("amount") is not None:

                    item["presupuesto"] = (
                        convertir_numero(
                            valor["amount"]
                        )
                    )

                item["moneda"] = (
                    valor.get(
                        "currency"
                    )
                    or item["moneda"]
                )

            periodo = (
                tender.get(
                    "tenderPeriod",
                    {}
                ) or {}
            )

            fecha_cierre = convertir_fecha(
                periodo.get(
                    "endDate"
                )
            )

            if fecha_cierre:

                item["fecha_cierre"] = (
                    fecha_cierre
                )

            documentos = tender.get(
                "documents",
                []
            ) or []

            for documento in documentos:

                if not isinstance(
                    documento,
                    dict
                ):
                    continue

                enlace = documento.get(
                    "url",
                    ""
                )

                if (
                    isinstance(enlace, str)
                    and enlace.startswith(
                        ("https://", "http://")
                    )
                ):

                    item["enlace"] = enlace
                    break

    return item


# ============================================================
# IMPORTACIÓN CSV ECUADOR
# ============================================================

def importar_ecuador(archivo):

    if archivo is None:
        return [], None

    contenido = archivo.getvalue()

    for codificacion in (
        "utf-8-sig",
        "latin-1"
    ):

        try:

            df = pd.read_csv(
                io.BytesIO(
                    contenido
                ),

                encoding=codificacion,

                sep=None,

                engine="python",

                dtype=str,
            )

            registros = []

            filas = (
                df.fillna("")
                .to_dict("records")
            )

            for fila in filas:

                datos = {
                    clave(k): v
                    for k, v in fila.items()
                }

                item = normalizar_ecuador({
                    "title": campo(
                        datos,
                        "title",
                        "titulo",
                        "objeto",
                    ),

                    "description": campo(
                        datos,
                        "description",
                        "descripcion",
                        "objeto",
                    ),

                    "buyerName": campo(
                        datos,
                        "buyername",
                        "entidad",
                    ),

                    "ocid": campo(
                        datos,
                        "ocid",
                        "codigo",
                    ),

                    "date": campo(
                        datos,
                        "date",
                        "fecha_publicacion",
                    ),
                })

                item["region"] = (
                    campo(
                        datos,
                        "provincia"
                    )
                    or "Sin determinar"
                )

                item["localidad"] = (
                    campo(
                        datos,
                        "canton",
                        "ciudad"
                    )
                    or "Sin determinar"
                )

                item["fuente"] = (
                    "Archivo CSV importado"
                )

                if item["titulo"]:

                    registros.append(
                        item
                    )

            return registros, None

        except (
            pd.errors.ParserError,
            UnicodeError,
            ValueError
        ):

            continue

    return [], (
        "No se pudo interpretar "
        "el archivo CSV."
    )


# ============================================================
# FILTROS TERRITORIALES
# ============================================================

def opciones_territoriales(
    oportunidades,
    campo_nombre,
):

    valores = set()

    for item in oportunidades:

        valor = str(
            item.get(
                campo_nombre,
                ""
            )
        ).strip()

        if valor and valor != "Sin determinar":

            valores.add(
                valor
            )

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

        if (
            categoria != "Todas"
            and categoria not in item.get(
                "categorias",
                []
            )
        ):
            continue

        if decision != "Todas":

            evaluacion = item.get(
                "evaluacion",
                {}
            )

            if (
                evaluacion.get(
                    "decision"
                ) != decision
            ):
                continue

        contenido = normalizar_texto(
            " ".join(
                str(
                    item.get(
                        campo_nombre,
                        ""
                    ) or ""
                )
                for campo_nombre in (
                    "titulo",
                    "descripcion",
                    "entidad",
                    "codigo",
                )
            )
        )

        if texto and texto not in contenido:
            continue

        resultado.append(
            item
        )

    return resultado


# ============================================================
# DETERMINAR VIGENCIA
# ============================================================

def estado_vigencia(item):

    estado = normalizar_texto(
        item.get(
            "estado",
            ""
        )
    )

    estados_cerrados = [
        "adjudicado",
        "cancelado",
        "desierto",
        "terminado",
        "cerrado",
        "awarded",
        "cancelled",
        "complete",
    ]

    if any(
        palabra in estado
        for palabra in estados_cerrados
    ):

        return "No vigente"

    cierre = item.get(
        "fecha_cierre"
    )

    if cierre:

        try:

            fecha = date.fromisoformat(
                cierre
            )

            if fecha < date.today():

                return "Plazo vencido"

        except ValueError:
            pass

    return "Por verificar"
