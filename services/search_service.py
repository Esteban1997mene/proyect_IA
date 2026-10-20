# ============================================================
# INTI PROJECTS AI
# SEARCH SERVICE V1
# ============================================================
#
# OBJETIVO:
# Centralizar la búsqueda de oportunidades y realizar
# una primera evaluación de afinidad con el ADN INTILED.
#
# ETAPA ACTUAL:
# - Colombia: SECOP II
# - Ecuador: pendiente
# - Perú: pendiente
# - Bolivia: pendiente
# - Venezuela: pendiente
#
# IMPORTANTE:
#
# RADAR SCORE != BID SCORE
#
# Radar Score:
# Afinidad preliminar basada en la información disponible
# en la fuente pública.
#
# Bid Score:
# Se calculará después de analizar pliegos, TDR, anexos,
# experiencia, personal, requisitos financieros, jurídicos
# y técnicos.
# ============================================================


import re
import unicodedata
from datetime import datetime

from services.secop_service import consultar_secop

from data.intiled_profile import INTILED_PROFILE


# ============================================================
# CONFIGURACIÓN
# ============================================================

RADAR_SCORE_MINIMO_INTERNO = 20


# ============================================================
# NORMALIZAR TEXTO
# ============================================================

def normalizar_texto(texto):

    if texto is None:
        return ""

    texto = str(texto).lower()

    # Quitar tildes
    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    # Limpiar caracteres especiales
    texto = re.sub(
        r"[^a-z0-9\s]",
        " ",
        texto
    )

    # Espacios múltiples
    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


# ============================================================
# LIMPIAR NOMBRE DEL PAÍS
# ============================================================

def limpiar_pais(pais):

    texto = normalizar_texto(
        pais
    )

    if "colombia" in texto:
        return "colombia"

    if "ecuador" in texto:
        return "ecuador"

    if "peru" in texto:
        return "peru"

    if "bolivia" in texto:
        return "bolivia"

    if "venezuela" in texto:
        return "venezuela"

    return texto


# ============================================================
# CREAR TEXTO GENERAL DE LA OPORTUNIDAD
# ============================================================

def construir_texto_oportunidad(
    oportunidad
):

    campos = [

        oportunidad.get(
            "titulo",
            ""
        ),

        oportunidad.get(
            "proyecto",
            ""
        ),

        oportunidad.get(
            "descripcion",
            ""
        ),

        oportunidad.get(
            "sector",
            ""
        ),

        oportunidad.get(
            "entidad",
            ""
        ),

        oportunidad.get(
            "modalidad",
            ""
        )
    ]

    return normalizar_texto(
        " ".join(
            str(campo)
            for campo in campos
            if campo
        )
    )


# ============================================================
# BUSCAR COINCIDENCIAS
# ============================================================

def buscar_coincidencias(
    texto,
    palabras
):

    texto_normalizado = normalizar_texto(
        texto
    )

    coincidencias = []

    for palabra in palabras:

        palabra_normalizada = (
            normalizar_texto(
                palabra
            )
        )

        if not palabra_normalizada:
            continue

        if palabra_normalizada in texto_normalizado:

            coincidencias.append(
                palabra
            )

    return list(
        dict.fromkeys(
            coincidencias
        )
    )


# ============================================================
# PALABRAS PREMIUM
# ============================================================

def evaluar_keywords_premium(
    texto
):

    palabras = INTILED_PROFILE.get(
        "keywords_premium",
        []
    )

    return buscar_coincidencias(
        texto,
        palabras
    )


# ============================================================
# PALABRAS POSITIVAS
# ============================================================

def evaluar_keywords_positivas(
    texto
):

    palabras = INTILED_PROFILE.get(
        "keywords_positivas",
        []
    )

    return buscar_coincidencias(
        texto,
        palabras
    )


# ============================================================
# ÁREAS NO PRIORITARIAS
# ============================================================

def evaluar_areas_no_prioritarias(
    texto
):

    palabras = INTILED_PROFILE.get(
        "areas_no_prioritarias",
        []
    )

    return buscar_coincidencias(
        texto,
        palabras
    )


# ============================================================
# LÍNEAS DE NEGOCIO
# ============================================================

def evaluar_lineas_negocio(
    texto
):

    lineas = INTILED_PROFILE.get(
        "lineas_negocio",
        {}
    )

    alta = buscar_coincidencias(
        texto,
        lineas.get(
            "prioridad_alta",
            []
        )
    )

    media = buscar_coincidencias(
        texto,
        lineas.get(
            "prioridad_media",
            []
        )
    )

    exploratorias = buscar_coincidencias(
        texto,
        lineas.get(
            "exploratorias",
            []
        )
    )

    return {
        "alta": alta,
        "media": media,
        "exploratorias": exploratorias
    }


# ============================================================
# TECNOLOGÍAS
# ============================================================

def evaluar_tecnologias(
    texto
):

    tecnologias = INTILED_PROFILE.get(
        "tecnologias",
        []
    )

    return buscar_coincidencias(
        texto,
        tecnologias
    )


# ============================================================
# PROYECTOS OBJETIVO
# ============================================================

def evaluar_proyectos_objetivo(
    texto
):

    proyectos = INTILED_PROFILE.get(
        "proyectos_objetivo",
        []
    )

    return buscar_coincidencias(
        texto,
        proyectos
    )


# ============================================================
# CALCULAR RADAR SCORE
# ============================================================

def calcular_radar_score(
    oportunidad
):

    texto = construir_texto_oportunidad(
        oportunidad
    )

    premium = evaluar_keywords_premium(
        texto
    )

    positivas = evaluar_keywords_positivas(
        texto
    )

    negativas = evaluar_areas_no_prioritarias(
        texto
    )

    lineas = evaluar_lineas_negocio(
        texto
    )

    tecnologias = evaluar_tecnologias(
        texto
    )

    proyectos = evaluar_proyectos_objetivo(
        texto
    )


    # ========================================================
    # SCORE
    # ========================================================

    score = 0


    # --------------------------------------------------------
    # 1. KEYWORDS PREMIUM
    # Máximo 30 puntos
    # --------------------------------------------------------

    score_premium = min(
        len(premium) * 10,
        30
    )

    score += score_premium


    # --------------------------------------------------------
    # 2. KEYWORDS POSITIVAS
    # Máximo 15 puntos
    # --------------------------------------------------------

    score_positivas = min(
        len(positivas) * 3,
        15
    )

    score += score_positivas


    # --------------------------------------------------------
    # 3. LÍNEAS DE NEGOCIO
    # Máximo 25 puntos
    # --------------------------------------------------------

    score_lineas = 0

    score_lineas += min(
        len(lineas["alta"]) * 8,
        16
    )

    score_lineas += min(
        len(lineas["media"]) * 4,
        8
    )

    score_lineas += min(
        len(lineas["exploratorias"]),
        1
    )

    score_lineas = min(
        score_lineas,
        25
    )

    score += score_lineas


    # --------------------------------------------------------
    # 4. TECNOLOGÍA
    # Máximo 15 puntos
    # --------------------------------------------------------

    score_tecnologia = min(
        len(tecnologias) * 5,
        15
    )

    score += score_tecnologia


    # --------------------------------------------------------
    # 5. TIPO DE PROYECTO
    # Máximo 15 puntos
    # --------------------------------------------------------

    score_proyecto = min(
        len(proyectos) * 5,
        15
    )

    score += score_proyecto


    # --------------------------------------------------------
    # PENALIZACIONES
    # --------------------------------------------------------

    penalizacion = min(
        len(negativas) * 20,
        60
    )

    score -= penalizacion


    # --------------------------------------------------------
    # LÍMITES
    # --------------------------------------------------------

    score = max(
        0,
        min(
            round(score, 1),
            100
        )
    )


    # ========================================================
    # RESULTADO
    # ========================================================

    return {

        "score": score,

        "premium": premium,

        "positivas": positivas,

        "negativas": negativas,

        "lineas_alta":
            lineas["alta"],

        "lineas_media":
            lineas["media"],

        "lineas_exploratorias":
            lineas["exploratorias"],

        "tecnologias":
            tecnologias,

        "proyectos_objetivo":
            proyectos,

        "detalle": {

            "premium":
                score_premium,

            "positivas":
                score_positivas,

            "lineas":
                score_lineas,

            "tecnologia":
                score_tecnologia,

            "proyecto":
                score_proyecto,

            "penalizacion":
                penalizacion
        }
    }


# ============================================================
# CLASIFICAR RADAR SCORE
# ============================================================

def clasificar_radar_score(
    score
):

    if score >= 80:

        return {
            "nivel": "MUY ALTA",
            "semaforo": "🟢",
            "recomendacion": "PRIORIDAD ALTA"
        }

    if score >= 60:

        return {
            "nivel": "ALTA",
            "semaforo": "🟢",
            "recomendacion": "ANALIZAR"
        }

    if score >= 40:

        return {
            "nivel": "MEDIA",
            "semaforo": "🟡",
            "recomendacion": "REVISAR"
        }

    if score >= 20:

        return {
            "nivel": "BAJA",
            "semaforo": "🟠",
            "recomendacion": "BAJA PRIORIDAD"
        }

    return {
        "nivel": "MUY BAJA",
        "semaforo": "🔴",
        "recomendacion": "DESCARTAR"
    }


# ============================================================
# EVALUAR OPORTUNIDAD
# ============================================================

def evaluar_oportunidad_radar(
    oportunidad
):

    analisis = calcular_radar_score(
        oportunidad
    )

    clasificacion = (
        clasificar_radar_score(
            analisis["score"]
        )
    )

    oportunidad[
        "radar_score"
    ] = analisis["score"]

    # Compatibilidad temporal con versiones
    # anteriores del Radar.
    oportunidad[
        "score"
    ] = analisis["score"]

    oportunidad[
        "radar_nivel"
    ] = clasificacion[
        "nivel"
    ]

    oportunidad[
        "radar_semaforo"
    ] = clasificacion[
        "semaforo"
    ]

    oportunidad[
        "radar_recomendacion"
    ] = clasificacion[
        "recomendacion"
    ]

    oportunidad[
        "radar_detalle"
    ] = analisis

    oportunidad[
        "elegibilidad"
    ] = "PENDIENTE_ANALISIS"

    oportunidad[
        "score_validado"
    ] = None

    return oportunidad


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

        clave = normalizar_texto(
            clave
        )

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
# FILTRAR TÉRMINOS EXCLUIDOS POR EL USUARIO
# ============================================================

def contiene_exclusion_usuario(
    oportunidad,
    excluir
):

    if not excluir:
        return False

    if isinstance(
        excluir,
        str
    ):

        palabras = [

            palabra.strip()

            for palabra
            in excluir.split(",")

            if palabra.strip()
        ]

    else:

        palabras = excluir

    texto = construir_texto_oportunidad(
        oportunidad
    )

    coincidencias = buscar_coincidencias(
        texto,
        palabras
    )

    return len(coincidencias) > 0


# ============================================================
# CONSULTAR COLOMBIA
# ============================================================

def buscar_colombia(
    sectores,
    palabras_adicionales=None,
    excluir=None,
    dias_atras=90,
    limite=100
):

    resultados = consultar_secop(

        sectores=sectores,

        palabras_adicionales=
            palabras_adicionales,

        dias_atras=dias_atras,

        limite=limite
    )

    oportunidades = []

    for oportunidad in resultados:

        if contiene_exclusion_usuario(
            oportunidad,
            excluir
        ):

            continue

        oportunidad = (
            evaluar_oportunidad_radar(
                oportunidad
            )
        )

        oportunidades.append(
            oportunidad
        )

    return oportunidades


# ============================================================
# MOTOR GENERAL DE BÚSQUEDA
# ============================================================

def buscar_oportunidades(
    paises,
    sectores,
    palabras_adicionales=None,
    excluir=None,
    dias_atras=90,
    limite_por_fuente=100,
    score_minimo=0
):

    oportunidades = []


    # ========================================================
    # RECORRER PAÍSES
    # ========================================================

    for pais in paises:

        pais_limpio = limpiar_pais(
            pais
        )


        # ----------------------------------------------------
        # COLOMBIA
        # ----------------------------------------------------

        if pais_limpio == "colombia":

            resultados = buscar_colombia(

                sectores=sectores,

                palabras_adicionales=
                    palabras_adicionales,

                excluir=excluir,

                dias_atras=dias_atras,

                limite=limite_por_fuente
            )

            oportunidades.extend(
                resultados
            )


        # ----------------------------------------------------
        # ECUADOR
        # ----------------------------------------------------

        elif pais_limpio == "ecuador":

            # Conector oficial pendiente.
            pass


        # ----------------------------------------------------
        # PERÚ
        # ----------------------------------------------------

        elif pais_limpio == "peru":

            # Conector oficial pendiente.
            pass


        # ----------------------------------------------------
        # BOLIVIA
        # ----------------------------------------------------

        elif pais_limpio == "bolivia":

            # Conector oficial pendiente.
            pass


        # ----------------------------------------------------
        # VENEZUELA
        # ----------------------------------------------------

        elif pais_limpio == "venezuela":

            # Conector oficial pendiente.
            pass


    # ========================================================
    # DUPLICADOS
    # ========================================================

    oportunidades = eliminar_duplicados(
        oportunidades
    )


    # ========================================================
    # FILTRO SCORE MÍNIMO
    # ========================================================

    oportunidades = [

        oportunidad

        for oportunidad
        in oportunidades

        if oportunidad.get(
            "radar_score",
            0
        ) >= score_minimo
    ]


    # ========================================================
    # ORDENAR POR SCORE
    # ========================================================

    oportunidades.sort(

        key=lambda oportunidad:
            oportunidad.get(
                "radar_score",
                0
            ),

        reverse=True
    )


    # ========================================================
    # FECHA DE PROCESAMIENTO
    # ========================================================

    fecha_procesamiento = (
        datetime.now().isoformat()
    )

    for oportunidad in oportunidades:

        oportunidad[
            "fecha_procesamiento_inti"
        ] = fecha_procesamiento


    return oportunidades
