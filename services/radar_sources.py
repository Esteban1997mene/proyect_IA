
# services/radar_sources.py

import io
import re
import unicodedata
from datetime import date, timedelta

import pandas as pd
import requests


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

# Términos usados para consultar la fuente.
# Son deliberadamente pocos para limitar las solicitudes.
CONSULTAS = {
    "Alumbrado público": [
        "alumbrado", "luminarias", "iluminacion"
    ],
    "Energía solar": [
        "fotovoltaico", "solar"
    ],
    "Eficiencia energética": [
        "eficiencia energetica", "energetica"
    ],
    "Ingeniería eléctrica": [
        "subestacion", "electrica"
    ],
    "Consultoría e interventoría": [
        "interventoria", "consultoria"
    ],
    "Tecnología y monitoreo": [
        "telemetria", "automatizacion"
    ],
}

PROVINCIAS_ECUADOR = [
    "Azuay", "Bolívar", "Cañar", "Carchi",
    "Chimborazo", "Cotopaxi", "El Oro",
    "Esmeraldas", "Galápagos", "Guayas",
    "Imbabura", "Loja", "Los Ríos",
    "Manabí", "Morona Santiago", "Napo",
    "Orellana", "Pastaza", "Pichincha",
    "Santa Elena", "Santo Domingo de los Tsáchilas",
    "Sucumbíos", "Tungurahua",
    "Zamora Chinchipe",
]


def normalizar_texto(valor):
    texto = str(valor or "").lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    return re.sub(r"\s+", " ", texto).strip()


def clave(valor):
    texto = normalizar_texto(valor)
    return re.sub(r"[^a-z0-9]+", "_", texto).strip("_")


def campo(fila, *nombres):
    for nombre in nombres:
        valor = fila.get(clave(nombre))
        if valor is not None and str(valor).strip():
            return str(valor).strip()
    return ""


def convertir_numero(valor):
    texto = re.sub(r"[^\d,.-]", "", str(valor or ""))
    if not texto:
        return None
    try:
        if "," in texto and "." in texto:
            if texto.rfind(",") > texto.rfind("."):
                texto = texto.replace(".", "").replace(",", ".")
            else:
                texto = texto.replace(",", "")
        elif "," in texto:
            texto = texto.replace(",", ".")
        return float(texto)
    except ValueError:
        return None


def convertir_fecha(valor):
    if not valor:
        return None
    try:
        fecha = pd.to_datetime(valor, errors="coerce")
        if pd.isna(fecha):
            return None
        return fecha.strftime("%Y-%m-%d")
    except Exception:
        return None


def clasificar_categoria(titulo, descripcion):
    texto = normalizar_texto(
        f"{titulo} {descripcion}"
    )
    encontradas = []

    for categoria, palabras in CATEGORIAS.items():
        if any(
            normalizar_texto(p) in texto
            for p in palabras
        ):
            encontradas.append(categoria)

    return encontradas


def normalizar_colombia(fila):
    datos = {
        clave(k): v for k, v in fila.items()
    }

    titulo = campo(
        datos, "nombre_del_procedimiento"
    )
    descripcion = campo(
        datos, "descripci_n_del_procedimiento",
        "descripcion_del_procedimiento"
    )

    enlace = campo(
        datos, "urlproceso", "url_proceso"
    )

    # Socrata puede devolver URL como objeto.
    if isinstance(fila.get("urlproceso"), dict):
        enlace = fila["urlproceso"].get("url", "")

    return {
        "pais": "Colombia",
        "titulo": titulo,
        "descripcion": descripcion,
        "entidad": campo(datos, "entidad"),
        "region": campo(
            datos, "departamento_entidad"
        ) or "Sin determinar",
        "localidad": campo(
            datos, "ciudad_entidad"
        ) or "Sin determinar",
        "presupuesto": convertir_numero(
            campo(datos, "precio_base")
        ),
        "moneda": "COP",
        "fecha_cierre": convertir_fecha(
            campo(
                datos,
                "fecha_de_recepcion_de_respuestas",
                "fecha_de_cierre_del_proceso"
            )
        ),
        "fecha_publicacion": convertir_fecha(
            campo(
                datos, "fecha_de_publicacion_del"
            )
        ),
        "codigo": campo(
            datos, "id_del_proceso",
            "referencia_del_proceso"
        ),
        "enlace": enlace,
        "estado": campo(
            datos, "estado_del_procedimiento",
            "estado_del_proceso"
        ),
        "fuente": "SECOP II",
        "ubicacion_confirmada": False,
        "tipo_ubicacion": "Sede de entidad contratante",
        "categorias": clasificar_categoria(
            titulo, descripcion
        ),
    }


def normalizar_ecuador(fila):
    titulo = str(
        fila.get("description")
        or fila.get("title")
        or ""
    )
    codigo = str(
        fila.get("ocid")
        or fila.get("title")
        or ""
    )
    descripcion = str(
        fila.get("description") or ""
    )
    entidad = str(
        fila.get("buyerName") or ""
    )

    return {
        "pais": "Ecuador",
        "titulo": titulo,
        "descripcion": descripcion,
        "entidad": entidad,
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
            titulo, descripcion
        ),
        "ocid": codigo,
        "tipo_procedimiento": str(
            fila.get("internal_type") or ""
        ),
    }


def extraer_error(error):
    return f"{type(error).__name__}: {error}"


def consultar_colombia(
    categoria="Todas",
    busqueda="",
    dias=180,
    limite=300,
):
    """
    Consulta SECOP II mediante SoQL.
    La búsqueda ocurre en el servidor.

    No garantiza que todos los procesos
    recuperados sigan abiertos.
    """

    hoy = date.today()
    desde = hoy - timedelta(days=int(dias))

    palabras = []

    if categoria != "Todas":
        palabras.extend(
            CONSULTAS.get(categoria, [])
        )

    if busqueda.strip():
        palabras.append(busqueda.strip())

    # Si no se especifica categoría, se buscan
    # todas las líneas comerciales de INTILED.
    if not palabras:
        for lista in CONSULTAS.values():
            palabras.extend(lista)

    palabras = list(dict.fromkeys(palabras))

    condiciones = []

    for palabra in palabras:
        limpia = normalizar_texto(palabra)
        limpia = limpia.replace("'", "''")

        condiciones.append(
            "("
            "lower(nombre_del_procedimiento) "
            f"like '%{limpia}%' "
            "OR "
            "lower(descripci_n_del_procedimiento) "
            f"like '%{limpia}%'"
            ")"
        )

    filtro_texto = " OR ".join(condiciones)

    filtro_fecha = (
        "fecha_de_publicacion_del >= "
        f"'{desde.isoformat()}T00:00:00'"
    )

    where = f"({filtro_fecha})"

    if filtro_texto:
        where += f" AND ({filtro_texto})"

    parametros = {
        "$where": where,
        "$order": (
            "fecha_de_publicacion_del DESC"
        ),
        "$limit": min(int(limite), 1000),
    }

    try:
        respuesta = requests.get(
            SECOP_URL,
            params=parametros,
            timeout=40,
            headers={
                "Accept": "application/json",
                "User-Agent": "INTI-Projects/2.0",
            },
        )
        respuesta.raise_for_status()
        datos = respuesta.json()

        if not isinstance(datos, list):
            return [], "Respuesta SECOP no válida."

        registros = [
            normalizar_colombia(item)
            for item in datos
            if isinstance(item, dict)
        ]

        registros = [
            item for item in registros
            if item["titulo"]
        ]

        return registros, None

    except Exception as error:
        return [], (
            "Error consultando SECOP II: "
            + extraer_error(error)
        )


def consultar_ecuador(
    categoria="Todas",
    busqueda="",
    anio=None,
    paginas=2,
):
    """
    Consulta la API oficial OCDS de SERCOP.

    Requiere palabra clave y año.
    La API puede contener procedimientos
    históricos o ya adjudicados.
    """

    anio = int(anio or date.today().year)

    palabras = []

    if categoria != "Todas":
        palabras.extend(
            CONSULTAS.get(categoria, [])
        )

    if busqueda.strip():
        palabras.append(busqueda.strip())

    if not palabras:
        for lista in CONSULTAS.values():
            palabras.extend(lista)

    palabras = list(dict.fromkeys(palabras))

    resultados = []
    errores = []
    vistos = set()

    # Máximo de términos por ejecución para
    # evitar consultas excesivas.
    for palabra in palabras[:8]:
        for pagina in range(
            1, min(int(paginas), 3) + 1
        ):
            try:
                respuesta = requests.get(
                    SERCOP_API,
                    params={
                        "year": anio,
                        "search": palabra,
                        "page": pagina,
                    },
                    timeout=35,
                    headers={
                        "Accept": "application/json",
                        "User-Agent": "INTI-Projects/2.0",
                    },
                )

                respuesta.raise_for_status()
                contenido = respuesta.json()

                if not isinstance(contenido, dict):
                    continue

                datos = contenido.get("data", [])

                if not isinstance(datos, list):
                    continue

                for fila in datos:
                    if not isinstance(fila, dict):
                        continue

                    item = normalizar_ecuador(fila)
                    identificador = item["codigo"]

                    if not identificador:
                        continue

                    if identificador in vistos:
                        continue

                    vistos.add(identificador)
                    resultados.append(item)

                total_paginas = contenido.get(
                    "pages", 1
                )

                try:
                    if pagina >= int(total_paginas):
                        break
                except (ValueError, TypeError):
                    pass

            except Exception as error:
                errores.append(
                    f"{palabra}, página {pagina}: "
                    + extraer_error(error)
                )
                break

    resultados.sort(
        key=lambda x: (
            x.get("fecha_publicacion") or ""
        ),
        reverse=True,
    )

    if not resultados and errores:
        return [], (
            "SERCOP no respondió correctamente. "
            + errores[0]
        )

    if errores:
        return resultados, (
            "Consulta parcial: algunas búsquedas "
            "de SERCOP no respondieron. "
            + errores[0]
        )

    return resultados, None


def consultar_detalle_ecuador(ocid):
    if not ocid:
        return None, "OCID no disponible."

    try:
        respuesta = requests.get(
            SERCOP_RECORD,
            params={"ocid": ocid},
            timeout=35,
        )
        respuesta.raise_for_status()
        return respuesta.json(), None

    except Exception as error:
        return None, extraer_error(error)


def enriquecer_ecuador(item, detalle):
    """
    Obtiene datos disponibles en el registro
    OCDS sin inventar ubicaciones ni fechas.
    """

    item = dict(item)

    if not isinstance(detalle, dict):
        return item

    registros = detalle.get("records", [])

    if not isinstance(registros, list):
        return item

    for registro in registros:
        entregas = registro.get("releases", [])

        for entrega in entregas:
            tender = entrega.get("tender", {}) or {}

            item["estado"] = (
                tender.get("status")
                or item["estado"]
            )

            valor = tender.get("value", {}) or {}

            if isinstance(valor, dict):
                if valor.get("amount") is not None:
                    item["presupuesto"] = (
                        convertir_numero(
                            valor["amount"]
                        )
                    )

                item["moneda"] = (
                    valor.get("currency")
                    or item["moneda"]
                )

            periodo = (
                tender.get("tenderPeriod", {})
                or {}
            )

            fecha = convertir_fecha(
                periodo.get("endDate")
            )

            if fecha:
                item["fecha_cierre"] = fecha

            documentos = tender.get(
                "documents", []
            )

            if isinstance(documentos, list):
                for documento in documentos:
                    enlace = documento.get("url", "")
                    if enlace.startswith(
                        ("https://", "http://")
                    ):
                        item["enlace"] = enlace
                        break

    return item


def importar_ecuador(archivo):
    """
    Compatibilidad con archivos CSV.
    No es el método principal de consulta.
    """

    if archivo is None:
        return [], None

    contenido = archivo.getvalue()

    for encoding in ("utf-8-sig", "latin-1"):
        try:
            df = pd.read_csv(
                io.BytesIO(contenido),
                encoding=encoding,
                sep=None,
                engine="python",
                dtype=str,
            )

            registros = []

            for fila in df.fillna("").to_dict(
                "records"
            ):
                normalizada = {
                    clave(k): v
                    for k, v in fila.items()
                }

                item = normalizar_ecuador({
                    "title": campo(
                        normalizada,
                        "title", "titulo", "objeto"
                    ),
                    "description": campo(
                        normalizada,
                        "description",
                        "descripcion",
                        "objeto"
                    ),
                    "buyerName": campo(
                        normalizada,
                        "buyername",
                        "entidad"
                    ),
                    "ocid": campo(
                        normalizada,
                        "ocid", "codigo"
                    ),
                    "date": campo(
                        normalizada,
                        "date",
                        "fecha_publicacion"
                    ),
                })

                item["region"] = (
                    campo(
                        normalizada,
                        "provincia"
                    ) or "Sin determinar"
                )

                item["localidad"] = (
                    campo(
                        normalizada,
                        "canton", "ciudad"
                    ) or "Sin determinar"
                )

                item["fuente"] = (
                    "Archivo CSV importado"
                )

                if item["titulo"]:
                    registros.append(item)

            return registros, None

        except Exception:
            continue

    return [], "No se pudo interpretar el CSV."


def opciones_territoriales(datos, campo):
    valores = sorted({
        str(item.get(campo, "")).strip()
        for item in datos
        if item.get(campo)
        and item.get(campo) != "Sin determinar"
    })
    return ["Todas"] + valores


def filtrar_oportunidades(
    oportunidades,
    texto="",
    region="Todas",
    localidad="Todas",
    decision="Todas",
    categoria="Todas",
):
    texto = normalizar_texto(texto)
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
                "categorias", []
            )
        ):
            continue

        evaluacion = item.get(
            "evaluacion", {}
        )

        if (
            decision != "Todas"
            and evaluacion.get("decision")
            != decision
        ):
            continue

        contenido = normalizar_texto(
            " ".join([
                item.get("titulo", ""),
                item.get("descripcion", ""),
                item.get("entidad", ""),
                item.get("codigo", ""),
            ])
        )

        if texto and texto not in contenido:
            continue

        resultado.append(item)

    return resultado


def estado_vigencia(item):
    """
    Evita declarar abierto un proceso
    solo por tener fecha futura.
    """

    estado = normalizar_texto(
        item.get("estado", "")
    )

    cerrados = [
        "adjudicado", "cancelado",
        "desierto", "terminado",
        "cerrado", "awarded",
        "cancelled", "complete",
    ]

    if any(p in estado for p in cerrados):
        return "No vigente"

    cierre = item.get("fecha_cierre")

    if cierre:
        try:
            if date.fromisoformat(cierre) < date.today():
                return "Plazo vencido"
        except ValueError:
            pass

    return "Por verificar"
