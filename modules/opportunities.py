import streamlit as st


# ============================================================
# INTI PROJECTS AI
# MÓDULO DE OPORTUNIDADES
# ============================================================
#
# Este módulo recibe oportunidades seleccionadas desde
# el Radar INTILED.
#
# Permite:
#
# 1. Visualizar la oportunidad seleccionada.
# 2. Revisar información proveniente de SECOP.
# 3. Ver el Radar Score.
# 4. Revisar coincidencias con el ADN INTILED.
# 5. Enviar la oportunidad al Análisis INTILED.
# 6. Preparar posteriormente la estructuración.
#
# ============================================================


# ============================================================
# FUNCIÓN AUXILIAR
# ============================================================

def obtener_valor(
    oportunidad,
    campo,
    valor_default="No informado"
):

    valor = oportunidad.get(
        campo
    )

    if valor is None:
        return valor_default

    if valor == "":
        return valor_default

    return valor


# ============================================================
# SCORE
# ============================================================

def obtener_clasificacion_score(score):

    try:
        score = float(score)

    except (
        TypeError,
        ValueError
    ):
        score = 0

    if score >= 80:

        return (
            "🟢",
            "MUY ALTA"
        )

    if score >= 60:

        return (
            "🟢",
            "ALTA"
        )

    if score >= 40:

        return (
            "🟡",
            "MEDIA"
        )

    if score >= 20:

        return (
            "🟠",
            "BAJA"
        )

    return (
        "🔴",
        "MUY BAJA"
    )


# ============================================================
# NORMALIZAR URL
# ============================================================

def normalizar_url(url):

    if not url:
        return ""

    # --------------------------------------------------------
    # URL COMO DICCIONARIO
    # --------------------------------------------------------

    if isinstance(
        url,
        dict
    ):

        url = (
            url.get("url")
            or url.get("href")
            or url.get("link")
            or ""
        )

    # --------------------------------------------------------
    # OTROS TIPOS
    # --------------------------------------------------------

    if not isinstance(
        url,
        str
    ):

        try:

            url = str(
                url
            )

        except Exception:

            return ""

    url = url.strip()

    # --------------------------------------------------------
    # VALIDAR
    # --------------------------------------------------------

    if not (
        url.startswith(
            "http://"
        )
        or url.startswith(
            "https://"
        )
    ):

        return ""

    return url


# ============================================================
# MOSTRAR INFORMACIÓN GENERAL
# ============================================================

def mostrar_informacion_general(
    oportunidad
):

    st.subheader(
        "📋 Información general"
    )

    col1, col2 = st.columns(
        2
    )

    # ========================================================
    # COLUMNA 1
    # ========================================================

    with col1:

        st.write(
            "**País**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "pais"
            )
        )

        st.write(
            "**Entidad**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "entidad"
            )
        )

        st.write(
            "**Departamento**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "departamento"
            )
        )

        st.write(
            "**Ciudad / Municipio**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "ciudad"
            )
        )

    # ========================================================
    # COLUMNA 2
    # ========================================================

    with col2:

        st.write(
            "**Fuente**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "fuente"
            )
        )

        st.write(
            "**Referencia**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "referencia"
            )
        )

        st.write(
            "**Modalidad**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "modalidad"
            )
        )

        st.write(
            "**Estado**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "estado"
            )
        )


# ============================================================
# MOSTRAR INFORMACIÓN ECONÓMICA
# ============================================================

def mostrar_informacion_economica(
    oportunidad
):

    st.subheader(
        "💰 Información económica y fechas"
    )

    col1, col2, col3 = st.columns(
        3
    )

    # --------------------------------------------------------
    # PRESUPUESTO
    # --------------------------------------------------------

    with col1:

        st.metric(
            "Presupuesto",
            obtener_valor(
                oportunidad,
                "valor"
            )
        )

    # --------------------------------------------------------
    # PUBLICACIÓN
    # --------------------------------------------------------

    with col2:

        st.metric(
            "Publicación",
            obtener_valor(
                oportunidad,
                "fecha_publicacion"
            )
        )

    # --------------------------------------------------------
    # CIERRE
    # --------------------------------------------------------

    with col3:

        st.metric(
            "Cierre / recepción",
            obtener_valor(
                oportunidad,
                "fecha_cierre"
            )
        )


# ============================================================
# MOSTRAR RADAR SCORE
# ============================================================

def mostrar_radar_score(
    oportunidad
):

    score = oportunidad.get(
        "radar_score",
        oportunidad.get(
            "score",
            0
        )
    )

    semaforo, nivel = (
        obtener_clasificacion_score(
            score
        )
    )

    st.subheader(
        "🧬 Compatibilidad preliminar INTILED"
    )

    col1, col2, col3 = st.columns(
        [1, 1, 2]
    )

    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    with col1:

        st.metric(
            "Radar Score",
            f"{score}/100"
        )

    # --------------------------------------------------------
    # NIVEL
    # --------------------------------------------------------

    with col2:

        st.metric(
            "Afinidad",
            f"{semaforo} {nivel}"
        )

    # --------------------------------------------------------
    # ELEGIBILIDAD
    # --------------------------------------------------------

    with col3:

        st.write(
            "**Elegibilidad**"
        )

        st.info(
            "Pendiente de análisis documental."
        )

    # --------------------------------------------------------
    # ADVERTENCIA
    # --------------------------------------------------------

    st.caption(
        "El Radar Score mide afinidad temática y "
        "estratégica. No representa todavía el "
        "cumplimiento de requisitos habilitantes."
    )


# ============================================================
# MOSTRAR ADN
# ============================================================

def mostrar_adn(
    oportunidad
):

    detalle = oportunidad.get(
        "radar_detalle",
        {}
    )

    if not detalle:

        return

    st.subheader(
        "🧬 Coincidencias con el ADN INTILED"
    )

    coincidencias = []

    # --------------------------------------------------------
    # PREMIUM
    # --------------------------------------------------------

    for item in detalle.get(
        "premium",
        []
    ):

        coincidencias.append(
            item
        )

    # --------------------------------------------------------
    # LÍNEAS
    # --------------------------------------------------------

    for item in detalle.get(
        "lineas_alta",
        []
    ):

        coincidencias.append(
            item
        )

    # --------------------------------------------------------
    # TECNOLOGÍA
    # --------------------------------------------------------

    for item in detalle.get(
        "tecnologias",
        []
    ):

        coincidencias.append(
            item
        )

    # --------------------------------------------------------
    # PROYECTOS
    # --------------------------------------------------------

    for item in detalle.get(
        "proyectos_objetivo",
        []
    ):

        coincidencias.append(
            item
        )

    # --------------------------------------------------------
    # ELIMINAR DUPLICADOS
    # --------------------------------------------------------

    coincidencias = list(
        dict.fromkeys(
            coincidencias
        )
    )

    # --------------------------------------------------------
    # MOSTRAR
    # --------------------------------------------------------

    if coincidencias:

        for coincidencia in coincidencias:

            st.write(
                f"✓ {coincidencia}"
            )

    else:

        st.info(
            "No existen coincidencias adicionales "
            "registradas."
        )


# ============================================================
# MOSTRAR DESCRIPCIÓN
# ============================================================

def mostrar_descripcion(
    oportunidad
):

    descripcion = obtener_valor(
        oportunidad,
        "descripcion",
        ""
    )

    if not descripcion:
        return

    st.subheader(
        "📝 Descripción del proceso"
    )

    st.write(
        descripcion
    )


# ============================================================
# MOSTRAR FUENTE
# ============================================================

def mostrar_fuente(
    oportunidad
):

    url = normalizar_url(
        oportunidad.get(
            "url",
            ""
        )
    )

    if not url:
        return

    st.subheader(
        "🌐 Fuente oficial"
    )

    try:

        st.link_button(
            "🔗 Abrir proceso original",
            url,
            use_container_width=True
        )

    except Exception:

        st.info(
            "La fuente no proporciona una URL "
            "compatible para este proceso."
        )


# ============================================================
# ACCIONES
# ============================================================

def mostrar_acciones(
    oportunidad
):

    st.subheader(
        "🚀 Siguiente paso"
    )

    st.write(
        "Selecciona qué quieres hacer con esta oportunidad."
    )

    col1, col2, col3 = st.columns(
        3
    )

    # ========================================================
    # ANÁLISIS INTILED
    # ========================================================

    with col1:

        if st.button(
            "🧠 Análisis estratégico",
            use_container_width=True,
            type="primary"
        ):

            st.session_state[
                "oportunidad_seleccionada"
            ] = oportunidad

            st.session_state[
                "solicitar_analisis"
            ] = True

            st.success(
                "La oportunidad está preparada "
                "para el Análisis INTILED."
            )

            st.info(
                "Abre '🧠 Análisis INTILED' "
                "desde el menú lateral."
            )

    # ========================================================
    # DOCUMENTOS
    # ========================================================

    with col2:

        if st.button(
            "📑 Analizar documentos",
            use_container_width=True
        ):

            st.session_state[
                "oportunidad_seleccionada"
            ] = oportunidad

            st.session_state[
                "analizar_documentos"
            ] = True

            st.info(
                "La oportunidad está preparada "
                "para el Analizador de documentos."
            )

    # ========================================================
    # ESTRUCTURACIÓN
    # ========================================================

    with col3:

        if st.button(
            "🏗️ Iniciar estructuración",
            use_container_width=True
        ):

            st.session_state[
                "oportunidad_seleccionada"
            ] = oportunidad

            st.session_state[
                "iniciar_estructuracion"
            ] = True

            st.warning(
                "Antes de estructurar la propuesta "
                "se recomienda completar el análisis "
                "de requisitos."
            )


# ============================================================
# MÓDULO PRINCIPAL
# ============================================================

def mostrar_oportunidades():

    # ========================================================
    # ENCABEZADO
    # ========================================================

    st.title(
        "🎯 Oportunidades seleccionadas"
    )

    st.caption(
        "Oportunidades identificadas por INTI "
        "para evaluación y estructuración."
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
            "Todavía no has seleccionado una oportunidad."
        )

        st.write(
            "Ve al **🔎 Radar de oportunidades**, "
            "realiza una búsqueda y selecciona "
            "**🧠 Analizar con INTI**."
        )

        return

    # ========================================================
    # OBTENER OPORTUNIDAD
    # ========================================================

    oportunidad = st.session_state[
        "oportunidad_seleccionada"
    ]

    # ========================================================
    # TÍTULO
    # ========================================================

    titulo = obtener_valor(
        oportunidad,
        "titulo",
        "Oportunidad sin título"
    )

    with st.container(
        border=True
    ):

        st.markdown(
            f"## {titulo}"
        )

        # ----------------------------------------------------
        # SECTOR
        # ----------------------------------------------------

        sector = oportunidad.get(
            "sector"
        )

        if sector:

            st.caption(
                f"Sector detectado: {sector}"
            )

    # ========================================================
    # INFORMACIÓN GENERAL
    # ========================================================

    mostrar_informacion_general(
        oportunidad
    )

    st.divider()

    # ========================================================
    # INFORMACIÓN ECONÓMICA
    # ========================================================

    mostrar_informacion_economica(
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
    # DESCRIPCIÓN
    # ========================================================

    mostrar_descripcion(
        oportunidad
    )

    # ========================================================
    # ADN
    # ========================================================

    mostrar_adn(
        oportunidad
    )

    st.divider()

    # ========================================================
    # FUENTE
    # ========================================================

    mostrar_fuente(
        oportunidad
    )

    # ========================================================
    # ACCIONES
    # ========================================================

    mostrar_acciones(
        oportunidad
    )
