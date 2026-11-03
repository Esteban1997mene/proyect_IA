
# services/radar_sources.py

import io
import os
import re
import unicodedata
from datetime import datetime

import pandas as pd
import requests

SECOP_DATASET = os.getenv(
    "INTI_SECOP_DATASET",
    "p6dx-8zbt"
)

SECOP_URL = (
    "https://www.datos.gov.co/resource/"
    f"{SECOP_DATASET}.json"
)

SERCOP_URL = (
    "https://portal.compraspublicas.gob.ec/sercop/"
)

CAMPOS = {
    "titulo": [
        "nombre_del_procedimiento",
        "nombre_del_proceso",
        "nombre_procedimiento",
        "objeto",
        "description",
        "title",
        "titulo",
    ],
    "descripcion": [
        "descripci_n_del_procedimiento",
        "descripcion_del_procedimiento",
        "descripci_n_del_proceso",
        "descripcion",
        "description",
        "objeto_de_contratacion",
        "objeto",
    ],
    "entidad": [
        "entidad",
        "nombre_de_la_entidad",
        "nombre_entidad",
        "buyer_name",
        "comprador",
        "institucion",
        "institucion_contratante",
    ],
    "departamento": [
        "departamento_entidad",
        "departamento",
        "region",
    ],
    "municipio": [
        "ciudad_entidad",
        "municipio_entidad",
        "ciudad",
        "municipio",
    ],
    "provincia": [
        "provincia",
        "province",
        "region",
    ],
    "canton": [
        "canton",
        "cant_n",
        "ciudad",
        "municipio",
    ],
    "presupuesto": [
        "precio_base",
        "valor_del_contrato",
        "valor_estimado",
        "presupuesto_referencial",
        "presupuesto",
        "amount",
        "value",
    ],
    "fecha_cierre": [
        "fecha_de_recepcion_de_respuestas",
        "fecha_de_cierre_del_proceso",
        "fecha_cierre",
        "fecha_limite",
        "tender_period_end_date",
    ],
    "codigo": [
        "id_del_proceso",
        "id_del_procedimiento",
        "codigo",
        "codigo_proceso",
        "ocid",
        "id",
    ],
    "enlace": [
        "urlproceso",
        "url_proceso",
        "url",
        "enlace",
        "link",
    ],
    "estado": [
        "estado_del_procedimiento",
        "estado_del_proceso",
        "estado",
        "status",
    ],
}


def clave(texto):
    texto = str(texto or "").lower().strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")


def valor_campo(fila, nombre):
    for alternativa in CAMPOS.get(nombre, []):
        llave = clave(alternativa)
        valor = fila.get(llave)
        if valor is not None and str(valor).strip():
            return str(valor).strip()
    return ""


def convertir_numero(valor):
    texto = str(valor or "").strip()
    if not texto:
        return None

    texto = re.sub(r"[^\d,.-]", "", texto)
    if not texto:
        return None

    try:
        if "," in texto and "." in texto:
            if texto.rfind(",") > texto.rfind("."):
                texto = texto.replace(".", "").replace(",", ".")
            else:
                texto = texto.replace(",", "")
        elif "," in texto:
            partes = texto.split(",")
            if len(partes[-1]) == 3:
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
            valor, errors="coerce", utc=True
        )
        if pd.isna(fecha):
            return None
        return fecha.strftime("%Y-%m-%d")
    except Exception:
        return None


def normalizar_registro(registro, pais):
    fila = {
        clave(k): v
        for k, v in registro.items()
    }

    region = (
        valor_campo(fila, "departamento")
        if pais == "Colombia"
        else valor_campo(fila, "provincia")
    )

    localidad = (
        valor_campo(fila, "municipio")
        if pais == "Colombia"
        else valor_campo(fila, "canton")
    )

    return {
        "pais": pais,
        "titulo": valor_campo(fila, "titulo"),
        "descripcion": valor_campo(fila, "descripcion"),
        "entidad": valor_campo(fila, "entidad"),
        "region": region or "Sin determinar",
        "localidad": localidad or "Sin determinar",
        "presupuesto": convertir_numero(
            valor_campo(fila, "presupuesto")
        ),
        "moneda": "COP" if pais == "Colombia" else "USD",
        "fecha_cierre": convertir_fecha(
            valor_campo(fila, "fecha_cierre")
        ),
        "codigo": valor_campo(fila, "codigo"),
        "enlace": valor_campo(fila, "enlace"),
        "estado": valor_campo(fila, "estado"),
        "ubicacion_confirmada": False,
        "fuente": (
            "SECOP II - Datos abiertos"
            if pais == "Colombia"
            else "SERCOP - Archivo importado"
        ),
    }


def consultar_colombia(limite=500):
    """
    Consulta una muestra de registros SECOP II.
    No equivale a un barrido exhaustivo de procesos.
    """
    try:
        respuesta = requests.get(
            SECOP_URL,
            params={
                "$limit": min(int(limite), 2000),
            },
            timeout=30,
            headers={
                "Accept": "application/json",
                "User-Agent": "INTI-Projects/1.0",
            },
        )
        respuesta.raise_for_status()
        datos = respuesta.json()

        if not isinstance(datos, list):
            return [], "La fuente no devolvió una lista válida."

        oportunidades = [
            normalizar_registro(item, "Colombia")
            for item in datos
            if isinstance(item, dict)
        ]

        oportunidades = [
            item for item in oportunidades
            if item["titulo"]
        ]

        return oportunidades, None

    except requests.RequestException as error:
        return [], (
            "No fue posible consultar SECOP II: "
            f"{error}"
        )
    except (ValueError, TypeError) as error:
        return [], (
            "La respuesta de SECOP II no pudo interpretarse: "
            f"{error}"
        )


def importar_ecuador(archivo):
    """
    Lee un CSV exportado desde una fuente oficial.
    El usuario debe comprobar el origen del archivo.
    """
    if archivo is None:
        return [], None

    contenido = archivo.getvalue()

    dataframe = None
    ultimo_error = None

    for codificacion in ("utf-8-sig", "latin-1"):
        try:
            dataframe = pd.read_csv(
                io.BytesIO(contenido),
                encoding=codificacion,
                sep=None,
                engine="python",
                dtype=str,
            )
            break
        except Exception as error:
            ultimo_error = error

    if dataframe is None:
        return [], f"No se pudo leer el CSV: {ultimo_error}"

    registros = dataframe.fillna("").to_dict("records")

    oportunidades = [
        normalizar_registro(item, "Ecuador")
        for item in registros
    ]

    oportunidades = [
        item for item in oportunidades
        if item["titulo"]
    ]

    if not oportunidades:
        return [], (
            "El archivo no contiene una columna de objeto "
            "o título reconocida. Revise sus encabezados."
        )

    return oportunidades, None


def opciones_territoriales(oportunidades, campo):
    valores = sorted({
        str(item.get(campo, "")).strip()
        for item in oportunidades
        if str(item.get(campo, "")).strip()
        and item.get(campo) != "Sin determinar"
    })
    return ["Todas"] + valores


def filtrar_oportunidades(
    oportunidades,
    texto="",
    region="Todas",
    localidad="Todas",
    decision="Todas",
):
    texto = str(texto).strip().lower()
    resultado = []

    for item in oportunidades:
        if region != "Todas" and item["region"] != region:
            continue

        if localidad != "Todas" and item["localidad"] != localidad:
            continue

        if decision != "Todas":
            if item.get("evaluacion", {}).get("decision") != decision:
                continue

        contenido = " ".join([
            item.get("titulo", ""),
            item.get("descripcion", ""),
            item.get("entidad", ""),
            item.get("codigo", ""),
        ]).lower()

        if texto and texto not in contenido:
            continue

        resultado.append(item)

    return resultado
