import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from datetime import datetime


# =========================================================
# CONFIGURACIÓN
# =========================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120 Safari/537.36"
    )
}


# =========================================================
# PALABRAS CLAVE INTILED
# =========================================================

PALABRAS_INTILED = [
    "energía solar",
    "energia solar",
    "fotovoltaico",
    "fotovoltaica",
    "alumbrado público",
    "alumbrado publico",
    "luminarias",
    "transición energética",
    "transicion energetica",
    "eficiencia energética",
    "eficiencia energetica",
    "infraestructura eléctrica",
    "infraestructura electrica",
    "smart city",
    "smart cities",
    "telegestión",
    "telegestion",
    "iot",
    "comunidades energéticas",
    "comunidades energeticas",
    "energías renovables",
    "energias renovables"
]


# =========================================================
# FUENTES
# =========================================================

FUENTES_OFICIALES = {

    "Colombia": [
        {
            "nombre": "SECOP",
            "dominio": "secop.gov.co"
        },
        {
            "nombre": "Colombia Compra Eficiente",
            "dominio": "colombiacompra.gov.co"
        }
    ],

    "Ecuador": [
        {
            "nombre": "SERCOP",
            "dominio": "compraspublicas.gob.ec"
        }
    ],

    "Perú": [
        {
            "nombre": "SEACE",
            "dominio": "seace.gob.pe"
        },
        {
            "nombre": "OSCE",
            "dominio": "gob.pe"
        }
    ],

    "Bolivia": [
        {
            "nombre": "SICOES",
            "dominio": "sicoes.gob.bo"
        }
    ],

    "Venezuela": [
        {
            "nombre": "SNC",
            "dominio": "snc.gob.ve"
        }
    ]
}


# =========================================================
# GENERADOR DE CONSULTAS
# =========================================================

def generar_consultas(paises, sectores):

    consultas = []

    for pais in paises:

        pais_limpio = (
            pais
            .replace("🇨🇴 ", "")
            .replace("🇪🇨 ", "")
            .replace("🇵🇪 ", "")
            .replace("🇧🇴 ", "")
            .replace("🇻🇪 ", "")
        )

        fuentes = FUENTES_OFICIALES.get(
            pais_limpio,
            []
        )

        for fuente in fuentes:

            for sector in sectores:

                consulta = (
                    f'site:{fuente["dominio"]} '
                    f'"{sector}" '
                    f'convocatoria OR licitación OR proyecto'
                )

                consultas.append({
                    "pais": pais_limpio,
                    "fuente": fuente["nombre"],
                    "dominio": fuente["dominio"],
                    "sector": sector,
                    "consulta": consulta
                })

    return consultas


# =========================================================
# BÚSQUEDA
# =========================================================

def buscar_web(consulta):

    """
    Búsqueda web preliminar.

    IMPORTANTE:
    Esta función será sustituida posteriormente
    por APIs y conectores oficiales.
    """

    resultados = []

    url = (
        "https://www.google.com/search?q="
        + quote_plus(consulta)
    )

    try:

        respuesta = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

        if respuesta.status_code != 200:
            return resultados

        soup = BeautifulSoup(
            respuesta.text,
            "html.parser"
        )

        elementos = soup.select("div.tF2Cxc")

        for elemento in elementos[:5]:

            titulo_tag = elemento.select_one("h3")
            enlace_tag = elemento.select_one("a")

            if not titulo_tag or not enlace_tag:
                continue

            titulo = titulo_tag.get_text(
                strip=True
            )

            enlace = enlace_tag.get(
                "href"
            )

            resultados.append({
                "titulo": titulo,
                "url": enlace
            })

    except Exception:

        return []

    return resultados


# =========================================================
# RADAR GENERAL
# =========================================================

def ejecutar_radar(paises, sectores):

    consultas = generar_consultas(
        paises,
        sectores
    )

    oportunidades = []

    for item in consultas:

        resultados = buscar_web(
            item["consulta"]
        )

        for resultado in resultados:

            oportunidad = {
                "pais": item["pais"],
                "fuente": item["fuente"],
                "sector": item["sector"],
                "titulo": resultado["titulo"],
                "url": resultado["url"],
                "fecha_deteccion": (
                    datetime.now()
                    .strftime("%d/%m/%Y %H:%M")
                )
            }

            oportunidades.append(
                oportunidad
            )

    return eliminar_duplicados(
        oportunidades
    )


# =========================================================
# DUPLICADOS
# =========================================================

def eliminar_duplicados(oportunidades):

    vistos = set()
    resultado = []

    for oportunidad in oportunidades:

        url = oportunidad["url"]

        if url not in vistos:

            vistos.add(url)
            resultado.append(
                oportunidad
            )

    return resultado
