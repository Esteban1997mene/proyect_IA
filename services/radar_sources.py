
# services/radar_sources.py
# INTI Projects Enterprise - Colombia

import re
import unicodedata
from datetime import date, timedelta

import pandas as pd
import requests


SECOP_URL = (
    "https://www.datos.gov.co/resource/"
    "p6dx-8zbt.json"
)

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


def normalizar_texto(valor):
    texto = unicodedata.normalize(
        "NFKD",
        str(valor or "").lower(),
    )

    texto = "".join(
        caracter for caracter in texto
        if not unicodedata.combining(caracter)
    )

    return re.sub(
        r"\s+", " ", texto
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
        return str(valor.get("url", ""))

    if isinstance(valor, str):
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
        fila.get("descripci_n_del_procedimiento")
        or ""
    )

    return {
        "pais": "Colombia",
        "titulo": titulo,
        "descripcion": descripcion,
        "entidad": str(
            fila.get("entidad") or ""
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


def consultar_colombia(
    categoria="Todas",
    busqueda="",
    dias=180,
    limite=300,
):
    """
    Consulta SECOP II filtrando en el servidor.

    Los resultados son una muestra limitada por
    cantidad; no garantizan cobertura exhaustiva.
    """
    desde = date.today() - timedelta(
        days=int(dias)
    )

    palabras = []

    if categoria in CATEGORIAS:
        palabras.extend(CATEGORIAS[categoria])

    elif categoria == "Todas":
        for grupo in CATEGORIAS.values():
            palabras.extend(grupo)

    if busqueda.strip():
        palabras.insert(0, busqueda.strip())

    palabras = list(dict.fromkeys(palabras))

    condiciones = []

    for palabra in palabras:
        termino = normalizar_texto(
            palabra
        ).replace("'", "''")

        condiciones.append(
            "("
            "lower(nombre_del_procedimiento) "
            f"like '%{termino}%' "
            "OR "
            "lower(descripci_n_del_procedimiento) "
            f"like '%{termino}%'"
            ")"
        )

    where = (
        "fecha_de_publicacion_del >= "
        f"'{desde.isoformat()}T00:00:00'"
    )

    if condiciones:
        where += (
            " AND (" +
            " OR ".join(condiciones) +
            ")"
        )

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
            timeout=(6, 18),
            headers={
                "Accept": "application/json",
                "User-Agent": "INTI-Projects/3.0",
            },
        )

        respuesta.raise_for_status()
        datos = respuesta.json()

        if not isinstance(datos, list):
            return [], (
                "SECOP II devolvió un formato "
                "de respuesta inesperado."
            )

        resultados = []
        identificadores = set()

        for fila in datos:
            if not isinstance(fila, dict):
                continue

            item = normalizar_colombia(fila)

            if not item["titulo"]:
                continue

            identificador = (
                item["codigo"]
                or (
                    item["titulo"] +
                    item["entidad"]
                )
            )

            if identificador in identificadores:
                continue

            identificadores.add(identificador)
            resultados.append(item)

        return resultados, None

    except requests.exceptions.Timeout:
        return [], (
            "SECOP II no respondió dentro del "
            "tiempo establecido. Vuelve a "
            "intentar más tarde."
        )

    except requests.exceptions.RequestException as error:
        return [], (
            "No se pudo consultar SECOP II: "
            f"{type(error).__name__}. "
            "Revisa la conexión o el servicio."
        )

    except (ValueError, TypeError):
        return [], (
            "No fue posible interpretar los datos "
            "recibidos de SECOP II."
        )


def opciones_territoriales(datos, campo):
    valores = {
        str(item.get(campo, "")).strip()
        for item in datos
        if item.get(campo)
        and item.get(campo) != "Sin determinar"
    }

    return ["Todas"] + sorted(valores)


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

        if decision != "Todas":
            evaluacion = item.get(
                "evaluacion", {}
            )

            if evaluacion.get("decision") != decision:
                continue

        contenido = normalizar_texto(
            " ".join([
                str(item.get("titulo") or ""),
                str(item.get("descripcion") or ""),
                str(item.get("entidad") or ""),
                str(item.get("codigo") or ""),
            ])
        )

        if texto and texto not in contenido:
            continue

        resultado.append(item)

    return resultado


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

    cierre = item.get("fecha_cierre")

    if cierre:
        try:
            if date.fromisoformat(cierre) < date.today():
                return "Plazo vencido"
        except ValueError:
            pass

    return "Por verificar"

