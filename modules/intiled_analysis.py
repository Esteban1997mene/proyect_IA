import streamlit as st


# ============================================================
# INTI PROJECTS AI
# ANÁLISIS ESTRATÉGICO INTILED
# ============================================================
#
# OBJETIVO:
#
# Analizar preliminarmente una oportunidad seleccionada
# desde el Radar de INTI.
#
# IMPORTANTE:
#
# RADAR SCORE
# = Afinidad preliminar basada en metadata.
#
# BID SCORE
# = Se calculará posteriormente después de analizar
#   TDR, pliegos, anexos y requisitos reales.
#
# Este módulo NO debe inventar requisitos contractuales.
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
        min(
            valor,
            100
        )
    )


def obtener_nivel_score(score):

    score = normalizar_score(
        score
    )

    if score >= 80:
        return "MUY ALTA", "🟢"

    if score >= 60:
        return "ALTA", "🟢"

    if score >= 40:
        return "MEDIA", "🟡"

    if score >= 20:
        return "BAJA", "🟠"

    return "MUY BAJA", "🔴"


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

    if not isinstance(
        detalle,
        dict
    ):
        return []

    coincidencias = []

    categorias = [
        "premium",
        "positivas",
        "lineas_alta",
        "lineas_media",
        "lineas_exploratorias",
        "tecnologias",
        "proyectos_objetivo"
    ]

    for categoria in categorias:

        elementos = detalle.get(
            categoria,
            []
        )

        if not isinstance(
            elementos,
            list
        ):
            continue

        for elemento in elementos:

            if (
                elemento
                and elemento
                not in coincidencias
            ):

                coincidencias.append(
                    elemento
                )

    return coincidencias


# ============================================================
# ENCABEZADO
# ============================================================

def mostrar_encabezado(
    oportunidad
):

    st.title(
        "🧠 Análisis Estratégico INTILED"
    )

    st.caption(
        "Evaluación estratégica preliminar de la "
        "oportunidad frente al ADN empresarial de INTILED."
    )

    st.divider()

    titulo = obtener_valor(
        oportunidad,
        "titulo",
        "Oportunidad sin título"
    )

    st.markdown(
        f"## {titulo}"
    )

    entidad = obtener_valor(
        oportunidad,
        "entidad"
    )

    referencia = obtener_valor(
        oportunidad,
        "referencia"
    )

    fuente = obtener_valor(
        oportunidad,
        "fuente"
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.write(
            "**Entidad contratante**"
        )

        st.write(
            entidad
        )

    with col2:

        st.write(
            "**Referencia**"
        )

        st.write(
            referencia
        )

    with col3:

        st.write(
            "**Fuente**"
        )

        st.write(
            fuente
        )


# ============================================================
# INFORMACIÓN GENERAL
# ============================================================

def mostrar_informacion_general(
    oportunidad
):

    st.subheader(
        "📋 Información de la oportunidad"
    )

    col1, col2 = st.columns(
        2
    )

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
            "**Departamento / región**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "departamento"
            )
        )

        st.write(
            "**Municipio / ciudad**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "ciudad"
            )
        )

        st.write(
            "**Sector detectado**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "sector"
            )
        )

    with col2:

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
            "**Estado del proceso**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "estado"
            )
        )

        st.write(
            "**Presupuesto**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "valor"
            )
        )

        st.write(
            "**Fecha de cierre**"
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

    st.subheader(
        "📡 INTILED Radar Score"
    )

    score = normalizar_score(
        oportunidad.get(
            "radar_score",
            oportunidad.get(
                "score",
                0
            )
        )
    )

    nivel, semaforo = (
        obtener_nivel_score(
            score
        )
    )

    recomendacion = oportunidad.get(
        "radar_recomendacion",
        "REVISAR"
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.metric(
            "Radar Score",
            f"{score:.0f}/100"
        )

    with col2:

        st.metric(
            "Afinidad preliminar",
            f"{semaforo} {nivel}"
        )

    with col3:

        st.metric(
            "Acción preliminar",
            recomendacion
        )

    st.progress(
        score / 100
    )

    st.info(
        "📡 El **Radar Score** mide la afinidad "
        "preliminar entre la oportunidad y el ADN "
        "INTILED utilizando la información disponible "
        "en la fuente de detección."
    )

    st.warning(
        "Este resultado **no confirma que INTILED "
        "cumpla los requisitos habilitantes**. "
        "La elegibilidad solamente podrá determinarse "
        "después de analizar los TDR, pliegos, anexos "
        "y demás documentos contractuales."
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

    if not coincidencias:

        st.info(
            "No se encontraron coincidencias detalladas "
            "adicionales en la información disponible."
        )

        return

    columnas = st.columns(
        2
    )

    for indice, coincidencia in enumerate(
        coincidencias[:20]
    ):

        with columnas[
            indice % 2
        ]:

            st.write(
                f"✓ {coincidencia}"
            )


# ============================================================
# DESCRIPCIÓN
# ============================================================

def mostrar_descripcion(
    oportunidad
):

    descripcion = oportunidad.get(
        "descripcion"
    )

    if not descripcion:
        return

    st.subheader(
        "📝 Descripción disponible"
    )

    st.write(
        descripcion
    )

    st.caption(
        "📥 Fuente: información recuperada "
        "de la oportunidad detectada."
    )


# ============================================================
# BID SCORE
# ============================================================

def mostrar_bid_score(
    oportunidad
):

    st.subheader(
        "🎯 INTILED Bid Score"
    )

    # ========================================================
    # BUSCAR SI YA EXISTE ANÁLISIS DOCUMENTAL
    # ========================================================

    referencia = str(
        oportunidad.get(
            "referencia"
        )
        or oportunidad.get(
            "id_proceso"
        )
        or oportunidad.get(
            "titulo"
        )
        or ""
    )

    analisis_documentales = (
        st.session_state.get(
            "analisis_documentales",
            {}
        )
    )

    analisis = (
        analisis_documentales.get(
            referencia
        )
    )

    # ========================================================
    # TODAVÍA NO EXISTE
    # ========================================================

    if not analisis:

        col1, col2 = st.columns(
            [1, 3]
        )

        with col1:

            st.metric(
                "Bid Score",
                "Pendiente"
            )

        with col2:

            st.warning(
                "📑 Para calcular el Bid Score debemos "
                "analizar primero los documentos oficiales "
                "de la convocatoria."
            )

        st.write(
            "El análisis documental permitirá verificar:"
        )

        elementos = [
            "Experiencia específica exigida.",
            "Personal profesional mínimo.",
            "Capacidad jurídica.",
            "Capacidad financiera.",
            "Indicadores organizacionales.",
            "Especificaciones técnicas.",
            "Certificaciones.",
            "Factores que otorgan puntaje.",
            "Garantías.",
            "Cronograma contractual.",
            "Causales de rechazo.",
            "Posibles brechas de INTILED."
        ]

        columnas = st.columns(
            2
        )

        for indice, elemento in enumerate(
            elementos
        ):

            with columnas[
                indice % 2
            ]:

                st.write(
                    f"⚪ {elemento}"
                )

        return

    # ========================================================
    # FUTURA INTEGRACIÓN
    # ========================================================

    bid_score = analisis.get(
        "bid_score"
    )

    if bid_score is None:

        st.metric(
            "Bid Score",
            "En análisis"
        )

        st.info(
            "Existen documentos asociados a esta "
            "convocatoria, pero el cálculo definitivo "
            "del Bid Score todavía está pendiente."
        )

    else:

        score = normalizar_score(
            bid_score
        )

        nivel, semaforo = (
            obtener_nivel_score(
                score
            )
        )

        col1, col2 = st.columns(
            2
        )

        with col1:

            st.metric(
                "Bid Score",
                f"{score:.0f}/100"
            )

        with col2:

            st.metric(
                "Compatibilidad validada",
                f"{semaforo} {nivel}"
            )

        st.progress(
            score / 100
        )


# ============================================================
# ESTADO DOCUMENTAL
# ============================================================

def mostrar_estado_documental(
    oportunidad
):

    st.subheader(
        "📑 Estado documental"
    )

    referencia = str(
        oportunidad.get(
            "referencia"
        )
        or oportunidad.get(
            "id_proceso"
        )
        or oportunidad.get(
            "titulo"
        )
        or ""
    )

    analisis_documentales = (
        st.session_state.get(
            "analisis_documentales",
            {}
        )
    )

    analisis = (
        analisis_documentales.get(
            referencia
        )
    )

    if not analisis:

        st.warning(
            "⚠️ Los TDR, pliegos y anexos de esta "
            "convocatoria todavía no han sido "
            "analizados por INTI."
        )

        return False

    documentos = analisis.get(
        "documentos",
        []
    )

    st.success(
        "✅ Existe información documental asociada "
        "a esta oportunidad."
    )

    st.metric(
        "Documentos registrados",
        len(documentos)
    )

    return True


# ============================================================
# LECTURA ESTRATÉGICA PRELIMINAR
# ============================================================

def mostrar_lectura_estrategica(
    oportunidad
):

    st.subheader(
        "🎯 Lectura estratégica preliminar"
    )

    score = normalizar_score(
        oportunidad.get(
            "radar_score",
            0
        )
    )

    if score >= 80:

        st.success(
            "La oportunidad presenta una **afinidad "
            "preliminar muy alta** con las líneas "
            "prioritarias de INTILED."
        )

        st.write(
            "Se recomienda priorizar el análisis "
            "de los documentos contractuales para "
            "determinar la viabilidad real de participación."
        )

    elif score >= 60:

        st.success(
            "La oportunidad presenta una **afinidad "
            "preliminar alta** con INTILED."
        )

        st.write(
            "Conviene revisar los documentos contractuales "
            "antes de asignar recursos a la preparación "
            "de la propuesta."
        )

    elif score >= 40:

        st.warning(
            "La oportunidad presenta una **afinidad "
            "preliminar media**."
        )

        st.write(
            "El análisis de los requisitos determinará "
            "si existen razones suficientes para "
            "priorizarla."
        )

    else:

        st.warning(
            "La oportunidad presenta una afinidad "
            "preliminar limitada."
        )

        st.write(
            "No debería priorizarse sin encontrar "
            "elementos adicionales de interés estratégico."
        )


# ============================================================
# DECISIÓN ESTRATÉGICA
# ============================================================

def mostrar_decision(
    oportunidad
):

    st.subheader(
        "🏆 Decisión estratégica INTILED"
    )

    referencia = str(
        oportunidad.get(
            "referencia"
        )
        or oportunidad.get(
            "id_proceso"
        )
        or oportunidad.get(
            "titulo"
        )
        or ""
    )

    analisis_documentales = (
        st.session_state.get(
            "analisis_documentales",
            {}
        )
    )

    analisis = (
        analisis_documentales.get(
            referencia
        )
    )

    if not analisis:

        st.info(
            "La decisión definitiva todavía está pendiente."
        )

        st.write(
            "Después del análisis documental, INTI "
            "deberá recomendar una de las siguientes opciones:"
        )

        col1, col2 = st.columns(
            2
        )

        with col1:

            st.success(
                "🟢 **PRESENTARSE**\n\n"
                "INTILED cumple los requisitos críticos "
                "y presenta condiciones competitivas."
            )

            st.warning(
                "🟡 **PRESENTARSE CON ALIADO**\n\n"
                "La oportunidad es atractiva, pero existe "
                "una brecha que puede resolverse mediante "
                "consorcio, unión temporal o aliado."
            )

        with col2:

            st.warning(
                "🟠 **REVISIÓN ESTRATÉGICA**\n\n"
                "Existen factores que requieren "
                "evaluación adicional."
            )

            st.error(
                "🔴 **NO PRIORIZAR**\n\n"
                "Existe una brecha crítica o la oportunidad "
                "no resulta suficientemente conveniente."
            )

        return

    decision = analisis.get(
        "decision"
    )

    if not decision:

        st.info(
            "Los documentos están registrados, pero "
            "la decisión estratégica todavía está "
            "en proceso de análisis."
        )

        return

    if decision == "PRESENTARSE":

        st.success(
            "🟢 PRESENTARSE"
        )

    elif decision == "PRESENTARSE CON ALIADO":

        st.warning(
            "🟡 PRESENTARSE CON ALIADO"
        )

    elif decision == "REVISIÓN ESTRATÉGICA":

        st.warning(
            "🟠 REVISIÓN ESTRATÉGICA"
        )

    else:

        st.error(
            "🔴 NO PRIORIZAR"
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
        "Continúa con el análisis documental "
        "o con la estructuración del proyecto."
    )

    col1, col2, col3 = st.columns(
        3
    )

    # ========================================================
    # ANALIZAR TDR
    # ========================================================

    with col1:

        if st.button(
            "📑 Analizar pliegos / TDR",
            use_container_width=True,
            type="primary",
            key="btn_analizar_tdr"
        ):

            # Guardar oportunidad
            st.session_state[
                "oportunidad_seleccionada"
            ] = oportunidad

            # Indicar al analizador que viene
            # desde una convocatoria
            st.session_state[
                "analizar_documentos"
            ] = True

            # Solicitar cambio de módulo
            st.session_state[
                "navegar_a"
            ] = "📑 Analizador de documentos"

            st.rerun()

    # ========================================================
    # ESTRUCTURACIÓN
    # ========================================================

    with col2:

        if st.button(
            "🏗️ Ir a estructuración",
            use_container_width=True,
            key="btn_ir_estructuracion"
        ):

            st.session_state[
                "oportunidad_seleccionada"
            ] = oportunidad

            st.session_state[
                "iniciar_estructuracion"
            ] = True

            st.session_state[
                "navegar_a"
            ] = "🏗️ Estructuración"

            st.rerun()

    # ========================================================
    # OPORTUNIDAD
    # ========================================================

    with col3:

        if st.button(
            "🎯 Ver oportunidad",
            use_container_width=True,
            key="btn_ver_oportunidad"
        ):

            st.session_state[
                "oportunidad_seleccionada"
            ] = oportunidad

            st.session_state[
                "navegar_a"
            ] = "🎯 Oportunidades"

            st.rerun()


# ============================================================
# MÓDULO PRINCIPAL
# ============================================================

def mostrar_analisis_intiled():

    # ========================================================
    # SIN OPORTUNIDAD
    # ========================================================

    if (
        "oportunidad_seleccionada"
        not in st.session_state
    ):

        st.title(
            "🧠 Análisis Estratégico INTILED"
        )

        st.caption(
            "Evaluación estratégica de oportunidades."
        )

        st.divider()

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
    # RECUPERAR OPORTUNIDAD
    # ========================================================

    oportunidad = st.session_state[
        "oportunidad_seleccionada"
    ]

    # ========================================================
    # ENCABEZADO
    # ========================================================

    mostrar_encabezado(
        oportunidad
    )

    st.divider()

    # ========================================================
    # INFORMACIÓN GENERAL
    # ========================================================

    mostrar_informacion_general(
        oportunidad
    )

    st.divider()

    # ========================================================
    # RADAR
    # ========================================================

    mostrar_radar_score(
        oportunidad
    )

    st.divider()

    # ========================================================
    # ADN INTILED
    # ========================================================

    mostrar_adn_intiled(
        oportunidad
    )

    st.divider()

    # ========================================================
    # DESCRIPCIÓN
    # ========================================================

    mostrar_descripcion(
        oportunidad
    )

    st.divider()

    # ========================================================
    # ESTADO DOCUMENTAL
    # ========================================================

    mostrar_estado_documental(
        oportunidad
    )

    st.divider()

    # ========================================================
    # BID SCORE
    # ========================================================

    mostrar_bid_score(
        oportunidad
    )

    st.divider()

    # ========================================================
    # LECTURA ESTRATÉGICA
    # ========================================================

    mostrar_lectura_estrategica(
        oportunidad
    )

    st.divider()

    # ========================================================
    # DECISIÓN
    # ========================================================

    mostrar_decision(
        oportunidad
    )

    st.divider()

    # ========================================================
    # ACCIONES
    # ========================================================

    mostrar_acciones(
        oportunidad
    )
