import streamlit as st

from services.requirements_engine import (
    analizar_requisitos,
    generar_resumen_requisitos
)

from services.scoring import (
    evaluar_oportunidad
)


# ============================================================
# INTI PROJECTS AI
# ANÁLISIS ESTRATÉGICO INTILED
# ============================================================
#
# Recibe una oportunidad real seleccionada desde el Radar.
#
# ETAPAS:
#
# 1. Lee la oportunidad.
# 2. Recupera Radar Score y ADN detectado.
# 3. Evalúa únicamente la información disponible.
# 4. NO inventa requisitos del pliego.
# 5. Identifica información pendiente.
# 6. Prepara la oportunidad para análisis documental.
#
# Radar Score != Bid Score
#
# ============================================================


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def obtener_valor(
    oportunidad,
    campo,
    default="No informado"
):

    valor = oportunidad.get(campo)

    if valor is None:
        return default

    if valor == "":
        return default

    return valor


def normalizar_score(valor):

    try:

        valor = float(valor)

    except (TypeError, ValueError):

        return 0

    return max(
        0,
        min(valor, 100)
    )


def icono_estado(estado):

    iconos = {

        "CUMPLE":
            "✅",

        "CUMPLE_PARCIAL":
            "🟡",

        "NO_CUMPLE":
            "❌",

        "PENDIENTE":
            "⚪"
    }

    return iconos.get(
        estado,
        "⚪"
    )


# ============================================================
# OBTENER COINCIDENCIAS ADN
# ============================================================

def obtener_coincidencias_adn(
    oportunidad
):

    detalle = oportunidad.get(
        "radar_detalle",
        {}
    )

    coincidencias = []

    categorias = [

        "premium",

        "positivas",

        "lineas_alta",

        "lineas_media",

        "tecnologias",

        "proyectos_objetivo"
    ]

    for categoria in categorias:

        for elemento in detalle.get(
            categoria,
            []
        ):

            if elemento not in coincidencias:

                coincidencias.append(
                    elemento
                )

    return coincidencias


# ============================================================
# DETERMINAR FACTORES PRELIMINARES
# ============================================================

def construir_factores_preliminares(
    oportunidad
):

    """
    IMPORTANTE:

    Estos factores NO representan todavía
    cumplimiento del pliego.

    Únicamente utilizamos información que puede
    inferirse de la metadata de la oportunidad.

    Experiencia, personal, habilitantes y capacidad
    financiera quedan deliberadamente sin validar.
    """

    radar_score = normalizar_score(
        oportunidad.get(
            "radar_score",
            0
        )
    )

    detalle = oportunidad.get(
        "radar_detalle",
        {}
    )

    tecnologias = detalle.get(
        "tecnologias",
        []
    )

    lineas = detalle.get(
        "lineas_alta",
        []
    )

    premium = detalle.get(
        "premium",
        []
    )

    # --------------------------------------------------------
    # AFINIDAD
    # --------------------------------------------------------

    afinidad = radar_score

    # --------------------------------------------------------
    # TECNOLOGÍA
    # --------------------------------------------------------

    if len(tecnologias) >= 3:

        tecnologia = 95

    elif len(tecnologias) == 2:

        tecnologia = 80

    elif len(tecnologias) == 1:

        tecnologia = 65

    elif premium or lineas:

        tecnologia = 50

    else:

        tecnologia = 25

    # --------------------------------------------------------
    # UBICACIÓN
    # --------------------------------------------------------

    pais = str(
        oportunidad.get(
            "pais",
            ""
        )
    ).lower()

    if "colombia" in pais:

        ubicacion = 90

    else:

        ubicacion = 60

    # --------------------------------------------------------
    # FACTORES PENDIENTES
    # --------------------------------------------------------
    #
    # 50 significa NEUTRO / NO VALIDADO.
    #
    # NO significa que INTILED cumpla 50%.
    #
    # Más adelante estos valores serán sustituidos
    # por el análisis real del pliego.
    # --------------------------------------------------------

    experiencia = 50

    personal = 50

    habilitantes = 50

    economico = 50

    tiempo = 50

    competitividad = 50

    return {

        "afinidad":
            afinidad,

        "experiencia":
            experiencia,

        "personal":
            personal,

        "tecnologia":
            tecnologia,

        "habilitantes":
            habilitantes,

        "economico":
            economico,

        "ubicacion":
            ubicacion,

        "tiempo":
            tiempo,

        "competitividad":
            competitividad
    }


# ============================================================
# REQUISITOS PRELIMINARES
# ============================================================

def construir_requisitos_preliminares(
    oportunidad
):

    """
    Mientras no tengamos los pliegos/TDR,
    NO fabricamos requisitos específicos.

    Creamos únicamente controles de validación
    para indicar qué debe revisarse.
    """

    requisitos = [

        {
            "id":
                "EXP-01",

            "nombre":
                "Experiencia específica de la empresa",

            "tipo":
                "experiencia_empresa",

            "componentes":
                [],

            "cantidad_minima":
                1,

            "valor_minimo":
                0,

            "critico":
                True
        },

        {
            "id":
                "FIN-01",

            "nombre":
                "Capacidad financiera y organizacional",

            "tipo":
                "financiero",

            "critico":
                True
        }
    ]

    return requisitos


# ============================================================
# INFORMACIÓN GENERAL
# ============================================================

def mostrar_encabezado_oportunidad(
    oportunidad
):

    titulo = obtener_valor(
        oportunidad,
        "titulo",
        "Oportunidad sin título"
    )

    st.markdown(
        f"## {titulo}"
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.write(
            "**Entidad**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "entidad"
            )
        )

    with col2:

        st.write(
            "**Ubicación**"
        )

        ciudad = obtener_valor(
            oportunidad,
            "ciudad",
            ""
        )

        departamento = obtener_valor(
            oportunidad,
            "departamento",
            ""
        )

        ubicacion = ", ".join(
            [
                str(x)
                for x in [
                    ciudad,
                    departamento
                ]
                if x
            ]
        )

        st.write(
            ubicacion
            if ubicacion
            else "No informada"
        )

    with col3:

        st.write(
            "**Fuente**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "fuente"
            )
        )

    st.write("")

    col4, col5, col6 = st.columns(
        3
    )

    with col4:

        st.write(
            "**Presupuesto**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "valor"
            )
        )

    with col5:

        st.write(
            "**Modalidad**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "modalidad"
            )
        )

    with col6:

        st.write(
            "**Cierre**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "fecha_cierre"
            )
        )


# ============================================================
# RADAR SCORE
# ============================================================

def mostrar_radar_score(
    oportunidad
):

    score = normalizar_score(
        oportunidad.get(
            "radar_score",
            0
        )
    )

    nivel = oportunidad.get(
        "radar_nivel",
        "PENDIENTE"
    )

    recomendacion = oportunidad.get(
        "radar_recomendacion",
        "REVISAR"
    )

    st.subheader(
        "📡 Evaluación preliminar del Radar"
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.metric(
            "INTILED Radar Score",
            f"{score:.0f}/100"
        )

    with col2:

        st.metric(
            "Afinidad",
            nivel
        )

    with col3:

        st.metric(
            "Acción preliminar",
            recomendacion
        )

    st.progress(
        score / 100
    )

    st.caption(
        "Este indicador mide afinidad preliminar. "
        "No confirma elegibilidad contractual."
    )


# ============================================================
# ADN INTILED
# ============================================================

def mostrar_adn_intiled(
    oportunidad
):

    st.subheader(
        "🧬 Coincidencias con el ADN INTILED"
    )

    coincidencias = (
        obtener_coincidencias_adn(
            oportunidad
        )
    )

    if coincidencias:

        columnas = st.columns(
            2
        )

        for indice, coincidencia in enumerate(
            coincidencias[:16]
        ):

            with columnas[
                indice % 2
            ]:

                st.write(
                    f"✓ {coincidencia}"
                )

    else:

        st.info(
            "El Radar no registró coincidencias "
            "detalladas adicionales."
        )


# ============================================================
# FACTORES ESTRATÉGICOS
# ============================================================

def mostrar_factores(
    factores
):

    st.subheader(
        "📊 Factores estratégicos preliminares"
    )

    st.caption(
        "Los factores marcados como no validados "
        "serán reemplazados por datos reales después "
        "del análisis de los pliegos y de la "
        "Biblioteca INTILED."
    )

    nombres = {

        "afinidad":
            "Afinidad estratégica",

        "experiencia":
            "Experiencia empresarial",

        "personal":
            "Equipo profesional",

        "tecnologia":
            "Compatibilidad tecnológica",

        "habilitantes":
            "Requisitos habilitantes",

        "economico":
            "Capacidad económica",

        "ubicacion":
            "Capacidad territorial",

        "tiempo":
            "Tiempo de preparación",

        "competitividad":
            "Competitividad probable"
    }

    no_validados = [

        "experiencia",

        "personal",

        "habilitantes",

        "economico",

        "tiempo",

        "competitividad"
    ]

    for clave, nombre in nombres.items():

        valor = normalizar_score(
            factores.get(
                clave,
                0
            )
        )

        col1, col2 = st.columns(
            [3, 1]
        )

        with col1:

            st.write(
                f"**{nombre}**"
            )

            st.progress(
                valor / 100
            )

        with col2:

            if clave in no_validados:

                st.write(
                    "⚪ Pendiente"
                )

            else:

                st.write(
                    f"**{valor:.0f}/100**"
                )


# ============================================================
# VALIDACIONES PENDIENTES
# ============================================================

def mostrar_validaciones_pendientes():

    st.subheader(
        "⚠️ Información que debemos validar"
    )

    st.warning(
        "INTI todavía no ha leído los documentos "
        "contractuales completos de esta oportunidad. "
        "Por tanto, no puede afirmar que INTILED "
        "cumpla los siguientes requisitos."
    )

    pendientes = [

        "Experiencia contractual específica exigida.",

        "Número y valor de contratos acreditables.",

        "Experiencia específica del personal clave.",

        "Indicadores financieros y organizacionales.",

        "Requisitos jurídicos y habilitantes.",

        "RUP, clasificaciones o códigos exigidos.",

        "Especificaciones técnicas obligatorias.",

        "Certificaciones requeridas.",

        "Cronograma real del proceso.",

        "Factores que otorgan puntaje.",

        "Causales de rechazo.",

        "Necesidad de consorcio, unión temporal o aliado."
    ]

    for pendiente in pendientes:

        st.write(
            f"⚪ {pendiente}"
        )


# ============================================================
# ESTRATEGIA PRELIMINAR
# ============================================================

def mostrar_estrategia_preliminar(
    oportunidad
):

    score = normalizar_score(
        oportunidad.get(
            "radar_score",
            0
        )
    )

    st.subheader(
        "🎯 Lectura estratégica preliminar"
    )

    if score >= 80:

        st.success(
            "La oportunidad presenta una afinidad "
            "temática MUY ALTA con el ADN INTILED. "
            "Se recomienda priorizar la obtención y "
            "análisis de los documentos del proceso."
        )

    elif score >= 60:

        st.success(
            "La oportunidad presenta una afinidad "
            "ALTA con INTILED. Conviene realizar "
            "revisión documental antes de decidir "
            "la participación."
        )

    elif score >= 40:

        st.warning(
            "La oportunidad presenta afinidad MEDIA. "
            "Debe revisarse el pliego antes de dedicar "
            "recursos importantes a la preparación."
        )

    else:

        st.warning(
            "La oportunidad presenta afinidad limitada. "
            "No debería priorizarse sin una razón "
            "estratégica adicional."
        )

    st.info(
        "La decisión definitiva "
        "**PRESENTARSE / PRESENTARSE CON ALIADO / "
        "REVISIÓN ESTRATÉGICA / NO PRIORIZAR** "
        "se generará cuando INTI tenga los requisitos "
        "reales del proceso."
    )


# ============================================================
# ACCIONES
# ============================================================

def mostrar_acciones(
    oportunidad
):

    st.subheader(
        "🚀 Siguiente etapa"
    )

    col1, col2, col3 = st.columns(
        3
    )

    # ========================================================
    # DOCUMENTOS
    # ========================================================

    with col1:

        if st.button(
            "📑 Analizar pliegos / TDR",
            use_container_width=True,
            type="primary"
        ):

            st.session_state[
                "oportunidad_seleccionada"
            ] = oportunidad

            st.session_state[
                "analizar_documentos"
            ] = True

            st.success(
                "Oportunidad preparada para "
                "el Analizador de documentos."
            )

            st.info(
                "Abre '📑 Analizador de documentos' "
                "desde el menú lateral."
            )

    # ========================================================
    # ALIANZA
    # ========================================================

    with col2:

        if st.button(
            "🤝 Evaluar posible alianza",
            use_container_width=True
        ):

            st.info(
                "La necesidad de un aliado se determinará "
                "después de identificar las brechas "
                "contractuales reales."
            )

    # ========================================================
    # ESTRUCTURACIÓN
    # ========================================================

    with col3:

        if st.button(
            "🏗️ Preparar estructuración",
            use_container_width=True
        ):

            st.session_state[
                "iniciar_estructuracion"
            ] = True

            st.warning(
                "Se recomienda completar primero "
                "el análisis documental."
            )


# ============================================================
# MÓDULO PRINCIPAL
# ============================================================

def mostrar_analisis_intiled():

    # ========================================================
    # ENCABEZADO
    # ========================================================

    st.title(
        "🧠 Análisis Estratégico INTILED"
    )

    st.caption(
        "Evaluación estratégica de oportunidades "
        "mediante el ADN empresarial de INTILED."
    )

    st.divider()

    # ========================================================
    # VERIFICAR OPORTUNIDAD
    # ========================================================

    if (
        "oportunidad_seleccionada"
        not in st.session_state
    ):

        st.info(
            "No existe una oportunidad seleccionada."
        )

        st.write(
            "Ve al **🔎 Radar de oportunidades**, "
            "selecciona un proceso y pulsa "
            "**🧠 Analizar con INTI**."
        )

        return

    # ========================================================
    # OPORTUNIDAD REAL
    # ========================================================

    oportunidad = st.session_state[
        "oportunidad_seleccionada"
    ]

    # ========================================================
    # INFORMACIÓN
    # ========================================================

    mostrar_encabezado_oportunidad(
        oportunidad
    )

    st.divider()

    # ========================================================
    # RADAR SCORE
    # ========================================================

    mostrar_radar_score(
        oportunidad
    )

    st.divider()

    # ========================================================
    # ADN
    # ========================================================

    mostrar_adn_intiled(
        oportunidad
    )

    st.divider()

    # ========================================================
    # FACTORES
    # ========================================================

    factores = (
        construir_factores_preliminares(
            oportunidad
        )
    )

    mostrar_factores(
        factores
    )

    st.divider()

    # ========================================================
    # VALIDACIONES
    # ========================================================

    mostrar_validaciones_pendientes()

    st.divider()

    # ========================================================
    # ESTRATEGIA
    # ========================================================

    mostrar_estrategia_preliminar(
        oportunidad
    )

    st.divider()

    # ========================================================
    # ACCIONES
    # ========================================================

    mostrar_acciones(
        oportunidad
    )
