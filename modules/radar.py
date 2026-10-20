import streamlit as st
from datetime import date

from services.search_service import buscar_oportunidades


# ============================================================
# INTI PROJECTS AI
# RADAR DE OPORTUNIDADES V2
# ============================================================
#
# Este módulo:
#
# 1. Consulta oportunidades reales.
# 2. Utiliza search_service.py.
# 3. Consulta SECOP II para Colombia.
# 4. Cruza resultados con el ADN INTILED.
# 5. Calcula INTILED Radar Score.
# 6. Ordena oportunidades por afinidad.
# 7. Permite guardar oportunidades.
# 8. Permite enviar oportunidades al análisis INTILED.
#
# IMPORTANTE:
#
# RADAR SCORE != BID SCORE
#
# El Radar Score representa afinidad preliminar.
# No confirma elegibilidad ni cumplimiento del pliego.
# ============================================================


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def obtener_color_score(score):
    """
    Devuelve el semáforo correspondiente al Radar Score.
    """

    if score >= 80:
        return "🟢"

    elif score >= 60:
        return "🟢"

    elif score >= 40:
        return "🟡"

    elif score >= 20:
        return "🟠"

    return "🔴"


def obtener_nivel_score(score):
    """
    Clasifica visualmente el Radar Score.
    """

    if score >= 80:
        return "MUY ALTA"

    elif score >= 60:
        return "ALTA"

    elif score >= 40:
        return "MEDIA"

    elif score >= 20:
        return "BAJA"

    return "MUY BAJA"


def obtener_lista_coincidencias(detalle):
    """
    Obtiene las principales coincidencias entre
    una oportunidad y el ADN INTILED.
    """

    coincidencias = []

    # --------------------------------------------------------
    # PALABRAS PREMIUM
    # --------------------------------------------------------

    for item in detalle.get(
        "premium",
        []
    ):
        coincidencias.append(item)

    # --------------------------------------------------------
    # LÍNEAS PRIORITARIAS
    # --------------------------------------------------------

    for item in detalle.get(
        "lineas_alta",
        []
    ):
        coincidencias.append(item)

    # --------------------------------------------------------
    # TECNOLOGÍAS
    # --------------------------------------------------------

    for item in detalle.get(
        "tecnologias",
        []
    ):
        coincidencias.append(item)

    # --------------------------------------------------------
    # TIPOS DE PROYECTO
    # --------------------------------------------------------

    for item in detalle.get(
        "proyectos_objetivo",
        []
    ):
        coincidencias.append(item)

    # --------------------------------------------------------
    # ELIMINAR DUPLICADOS
    # --------------------------------------------------------

    coincidencias = list(
        dict.fromkeys(
            coincidencias
        )
    )

    return coincidencias


# ============================================================
# GUARDAR OPORTUNIDAD
# ============================================================

def guardar_oportunidad(oportunidad):
    """
    Guarda temporalmente una oportunidad dentro
    de st.session_state.

    Posteriormente esta función será reemplazada
    por almacenamiento persistente en base de datos.
    """

    if "oportunidades_guardadas" not in st.session_state:

        st.session_state[
            "oportunidades_guardadas"
        ] = []

    guardadas = st.session_state[
        "oportunidades_guardadas"
    ]

    # --------------------------------------------------------
    # IDENTIFICADOR
    # --------------------------------------------------------

    id_nuevo = (
        oportunidad.get("id_proceso")
        or oportunidad.get("referencia")
        or oportunidad.get("titulo")
    )

    # --------------------------------------------------------
    # VERIFICAR DUPLICADO
    # --------------------------------------------------------

    for guardada in guardadas:

        id_guardado = (
            guardada.get("id_proceso")
            or guardada.get("referencia")
            or guardada.get("titulo")
        )

        if str(id_guardado) == str(id_nuevo):

            st.info(
                "Esta oportunidad ya se encuentra guardada."
            )

            return

    # --------------------------------------------------------
    # GUARDAR
    # --------------------------------------------------------

    guardadas.append(
        oportunidad
    )

    st.success(
        "Oportunidad guardada correctamente."
    )


# ============================================================
# RESUMEN DEL RADAR
# ============================================================

def mostrar_resumen(oportunidades):
    """
    Muestra indicadores generales de los resultados.
    """

    st.subheader(
        "📊 Resumen del Radar INTILED"
    )

    # --------------------------------------------------------
    # TOTAL
    # --------------------------------------------------------

    total = len(
        oportunidades
    )

    # --------------------------------------------------------
    # MUY ALTA
    # --------------------------------------------------------

    muy_altas = len(
        [
            oportunidad
            for oportunidad in oportunidades
            if oportunidad.get(
                "radar_score",
                0
            ) >= 80
        ]
    )

    # --------------------------------------------------------
    # ALTA
    # --------------------------------------------------------

    altas = len(
        [
            oportunidad
            for oportunidad in oportunidades
            if 60 <= oportunidad.get(
                "radar_score",
                0
            ) < 80
        ]
    )

    # --------------------------------------------------------
    # MEDIA
    # --------------------------------------------------------

    medias = len(
        [
            oportunidad
            for oportunidad in oportunidades
            if 40 <= oportunidad.get(
                "radar_score",
                0
            ) < 60
        ]
    )

    # --------------------------------------------------------
    # BAJA
    # --------------------------------------------------------

    bajas = len(
        [
            oportunidad
            for oportunidad in oportunidades
            if oportunidad.get(
                "radar_score",
                0
            ) < 40
        ]
    )

    # --------------------------------------------------------
    # MÉTRICAS
    # --------------------------------------------------------

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "Procesos",
            total
        )

    with col2:

        st.metric(
            "🟢 Muy alta",
            muy_altas
        )

    with col3:

        st.metric(
            "🟢 Alta",
            altas
        )

    with col4:

        st.metric(
            "🟡 Media",
            medias
        )

    with col5:

        st.metric(
            "🟠 Baja",
            bajas
        )


# ============================================================
# MOSTRAR RESULTADOS
# ============================================================

def mostrar_resultados(oportunidades):
    """
    Renderiza las tarjetas de oportunidades.
    """

    st.subheader(
        "🎯 Oportunidades priorizadas"
    )

    st.caption(
        "Los procesos se encuentran ordenados "
        "automáticamente según su afinidad preliminar "
        "con el ADN empresarial de INTILED."
    )

    # ========================================================
    # RECORRER OPORTUNIDADES
    # ========================================================

    for i, oportunidad in enumerate(
        oportunidades
    ):

        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        score = oportunidad.get(
            "radar_score",
            0
        )

        # ----------------------------------------------------
        # SEMÁFORO
        # ----------------------------------------------------

        semaforo = oportunidad.get(
            "radar_semaforo",
            obtener_color_score(score)
        )

        # ----------------------------------------------------
        # NIVEL
        # ----------------------------------------------------

        nivel = oportunidad.get(
            "radar_nivel",
            obtener_nivel_score(score)
        )

        # ----------------------------------------------------
        # TARJETA
        # ----------------------------------------------------

        with st.container(
            border=True
        ):

            col1, col2 = st.columns(
                [4, 1]
            )

            # =================================================
            # INFORMACIÓN PRINCIPAL
            # =================================================

            with col1:

                titulo = oportunidad.get(
                    "titulo",
                    "Proceso sin título"
                )

                st.markdown(
                    f"### {titulo}"
                )

                # ---------------------------------------------
                # ENTIDAD
                # ---------------------------------------------

                st.write(
                    "**Entidad:** "
                    + str(
                        oportunidad.get(
                            "entidad",
                            "No informada"
                        )
                    )
                )

                # ---------------------------------------------
                # UBICACIÓN
                # ---------------------------------------------

                ciudad = oportunidad.get(
                    "ciudad",
                    ""
                )

                departamento = oportunidad.get(
                    "departamento",
                    ""
                )

                ubicacion = ", ".join(
                    [
                        str(valor)
                        for valor in [
                            ciudad,
                            departamento
                        ]
                        if valor
                        and valor != "No informada"
                        and valor != "No informado"
                    ]
                )

                if ubicacion:

                    st.write(
                        f"**Ubicación:** {ubicacion}"
                    )

                # ---------------------------------------------
                # FUENTE
                # ---------------------------------------------

                st.write(
                    "**Fuente:** "
                    + str(
                        oportunidad.get(
                            "fuente",
                            "No informada"
                        )
                    )
                )

                # ---------------------------------------------
                # SECTOR
                # ---------------------------------------------

                st.write(
                    "**Sector detectado:** "
                    + str(
                        oportunidad.get(
                            "sector",
                            "No identificado"
                        )
                    )
                )

                # ---------------------------------------------
                # MODALIDAD
                # ---------------------------------------------

                st.write(
                    "**Modalidad:** "
                    + str(
                        oportunidad.get(
                            "modalidad",
                            "No informada"
                        )
                    )
                )

                # ---------------------------------------------
                # ESTADO
                # ---------------------------------------------

                st.write(
                    "**Estado:** "
                    + str(
                        oportunidad.get(
                            "estado",
                            "No informado"
                        )
                    )
                )

            # =================================================
            # SCORE
            # =================================================

            with col2:

                st.metric(
                    "INTILED Radar Score",
                    f"{score}/100"
                )

                st.markdown(
                    f"### {semaforo} {nivel}"
                )

                st.caption(
                    "Afinidad preliminar"
                )

                st.caption(
                    "Elegibilidad pendiente "
                    "de revisión documental."
                )

            # =================================================
            # INFORMACIÓN ECONÓMICA Y FECHAS
            # =================================================

            st.divider()

            col3, col4, col5 = st.columns(3)

            # -------------------------------------------------
            # PRESUPUESTO
            # -------------------------------------------------

            with col3:

                st.write(
                    "**💰 Presupuesto estimado**"
                )

                st.write(
                    oportunidad.get(
                        "valor",
                        "No informado"
                    )
                )

            # -------------------------------------------------
            # PUBLICACIÓN
            # -------------------------------------------------

            with col4:

                st.write(
                    "**📅 Publicación**"
                )

                st.write(
                    oportunidad.get(
                        "fecha_publicacion",
                        "No informada"
                    )
                )

            # -------------------------------------------------
            # CIERRE
            # -------------------------------------------------

            with col5:

                st.write(
                    "**⏰ Cierre / recepción**"
                )

                st.write(
                    oportunidad.get(
                        "fecha_cierre",
                        "No informada"
                    )
                )

            # =================================================
            # REFERENCIA
            # =================================================

            referencia = oportunidad.get(
                "referencia",
                ""
            )

            if referencia:

                st.caption(
                    f"Referencia SECOP: {referencia}"
                )

            # =================================================
            # AFINIDAD CON ADN INTILED
            # =================================================

            detalle = oportunidad.get(
                "radar_detalle",
                {}
            )

            coincidencias = (
                obtener_lista_coincidencias(
                    detalle
                )
            )

            with st.expander(
                "🧬 ¿Por qué INTI considera "
                "relevante esta oportunidad?"
            ):

                if coincidencias:

                    st.write(
                        "**Coincidencias con "
                        "el ADN INTILED:**"
                    )

                    for coincidencia in coincidencias[:12]:

                        st.write(
                            f"✓ {coincidencia}"
                        )

                else:

                    st.info(
                        "No se identificaron coincidencias "
                        "específicas adicionales."
                    )

                # ---------------------------------------------
                # DETALLE DEL SCORE
                # ---------------------------------------------

                detalle_score = detalle.get(
                    "detalle",
                    {}
                )

                if detalle_score:

                    st.write("")

                    st.write(
                        "**Composición del Radar Score:**"
                    )

                    col_a, col_b, col_c = st.columns(3)

                    with col_a:

                        st.metric(
                            "Keywords premium",
                            detalle_score.get(
                                "premium",
                                0
                            )
                        )

                        st.metric(
                            "Líneas INTILED",
                            detalle_score.get(
                                "lineas",
                                0
                            )
                        )

                    with col_b:

                        st.metric(
                            "Keywords positivas",
                            detalle_score.get(
                                "positivas",
                                0
                            )
                        )

                        st.metric(
                            "Tecnología",
                            detalle_score.get(
                                "tecnologia",
                                0
                            )
                        )

                    with col_c:

                        st.metric(
                            "Tipo de proyecto",
                            detalle_score.get(
                                "proyecto",
                                0
                            )
                        )

                        st.metric(
                            "Penalización",
                            detalle_score.get(
                                "penalizacion",
                                0
                            )
                        )

                # ---------------------------------------------
                # NEGATIVAS
                # ---------------------------------------------

                negativas = detalle.get(
                    "negativas",
                    []
                )

                if negativas:

                    st.warning(
                        "INTI detectó términos "
                        "no prioritarios: "
                        + ", ".join(
                            negativas
                        )
                    )

            # =================================================
            # AVISO DE ELEGIBILIDAD
            # =================================================

            st.info(
                "⚪ **Elegibilidad:** pendiente de análisis "
                "de pliegos, TDR, experiencia, personal, "
                "requisitos financieros, jurídicos y técnicos."
            )

            # =================================================
            # ACCIONES
            # =================================================

            st.write("")

            col6, col7, col8 = st.columns(3)

            # -------------------------------------------------
            # ANALIZAR
            # -------------------------------------------------

            with col6:

                if st.button(
                    "🧠 Analizar con INTI",
                    key=f"analizar_radar_{i}",
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
                        "Oportunidad seleccionada. "
                        "Puedes continuar desde "
                        "el módulo de Oportunidades."
                    )

            # -------------------------------------------------
            # GUARDAR
            # -------------------------------------------------

            with col7:

                if st.button(
                    "⭐ Guardar oportunidad",
                    key=f"guardar_radar_{i}",
                    use_container_width=True
                ):

                    guardar_oportunidad(
                        oportunidad
                    )

            # -------------------------------------------------
            # FUENTE
            # -------------------------------------------------

            with col8:

                url = oportunidad.get(
                    "url",
                    ""
                )

                if url:

                    st.link_button(
                        "🔗 Ver proceso original",
                        url,
                        use_container_width=True
                    )

                else:

                    st.button(
                        "🔗 Fuente no disponible",
                        key=f"sin_url_{i}",
                        disabled=True,
                        use_container_width=True
                    )


# ============================================================
# RADAR PRINCIPAL
# ============================================================

def mostrar_radar():

    # ========================================================
    # ENCABEZADO
    # ========================================================

    st.title(
        "🔎 Radar de oportunidades"
    )

    st.caption(
        "Búsqueda de oportunidades reales y evaluación "
        "preliminar mediante el ADN empresarial "
        "de INTILED SAS BIC."
    )

    st.divider()

    # ========================================================
    # EXPLICACIÓN
    # ========================================================

    st.info(
        "El **INTILED Radar Score** mide la afinidad "
        "preliminar de cada oportunidad con las líneas, "
        "tecnologías y capacidades estratégicas de INTILED. "
        "Un Score alto no significa todavía que la empresa "
        "cumpla todos los requisitos de participación."
    )

    # ========================================================
    # CONFIGURACIÓN DE BÚSQUEDA
    # ========================================================

    st.subheader(
        "🎯 Configuración de búsqueda"
    )

    # ========================================================
    # PRIMERA FILA
    # ========================================================

    col1, col2, col3 = st.columns(3)

    # --------------------------------------------------------
    # PAÍSES
    # --------------------------------------------------------

    with col1:

        paises = st.multiselect(
            "País",
            [
                "🇨🇴 Colombia",
                "🇪🇨 Ecuador",
                "🇵🇪 Perú",
                "🇧🇴 Bolivia",
                "🇻🇪 Venezuela"
            ],
            default=[
                "🇨🇴 Colombia"
            ],
            help=(
                "Actualmente Colombia está conectado "
                "al motor real mediante SECOP II. "
                "Los demás países serán incorporados "
                "progresivamente."
            )
        )

    # --------------------------------------------------------
    # LÍNEAS DE INTERÉS
    # --------------------------------------------------------

    with col2:

        sectores = st.multiselect(
            "Líneas de interés",
            [
                "Energía solar",
                "Alumbrado público",
                "Transición energética",
                "Eficiencia energética",
                "Infraestructura eléctrica",
                "Smart Cities",
                "IoT y telegestión",
                "Comunidades energéticas",
                "Consultoría",
                "Interventoría",
                "Estudios técnicos",
                "Tecnología e innovación"
            ],
            default=[
                "Energía solar",
                "Alumbrado público",
                "Eficiencia energética"
            ]
        )

    # --------------------------------------------------------
    # PERIODO
    # --------------------------------------------------------

    with col3:

        dias_atras = st.selectbox(
            "Periodo de búsqueda",
            [
                7,
                15,
                30,
                60,
                90,
                180
            ],
            index=4,
            format_func=lambda x: (
                f"Últimos {x} días"
            )
        )

    # ========================================================
    # SEGUNDA FILA
    # ========================================================

    col4, col5, col6 = st.columns(3)

    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    with col4:

        score_minimo = st.slider(
            "Radar Score mínimo",
            min_value=0,
            max_value=100,
            value=20,
            step=5,
            help=(
                "Para las primeras pruebas recomendamos "
                "20. Posteriormente podremos aumentar "
                "el nivel de exigencia."
            )
        )

    # --------------------------------------------------------
    # PRESUPUESTO
    # --------------------------------------------------------

    with col5:

        presupuesto_minimo = st.number_input(
            "Presupuesto mínimo COP",
            min_value=0,
            value=0,
            step=10000000,
            help=(
                "Valor mínimo del proceso. "
                "Déjalo en 0 para no filtrar."
            )
        )

    # --------------------------------------------------------
    # LÍMITE
    # --------------------------------------------------------

    with col6:

        limite_resultados = st.selectbox(
            "Máximo de procesos consultados",
            [
                25,
                50,
                100,
                200
            ],
            index=2
        )

    # ========================================================
    # CONFIGURACIÓN AVANZADA
    # ========================================================

    with st.expander(
        "⚙️ Configuración avanzada"
    ):

        palabras_adicionales = st.text_area(
            "Palabras clave adicionales",
            placeholder=(
                "Ejemplo: luminaria solar, parques, "
                "telegestión, energía renovable"
            ),
            help=(
                "Puedes escribir varias palabras "
                "separadas por comas."
            )
        )

        excluir = st.text_area(
            "Excluir términos",
            placeholder=(
                "Ejemplo: hidrocarburos, minería, "
                "papelería"
            ),
            help=(
                "Los procesos que contengan estos "
                "términos serán descartados."
            )
        )

    # ========================================================
    # INFORMACIÓN DE FUENTES
    # ========================================================

    st.write("")

    with st.expander(
        "🌐 Fuentes de información"
    ):

        st.write(
            "🇨🇴 **Colombia:** SECOP II / "
            "Datos Abiertos Colombia"
        )

        st.write(
            "🇪🇨 **Ecuador:** conector pendiente"
        )

        st.write(
            "🇵🇪 **Perú:** conector pendiente"
        )

        st.write(
            "🇧🇴 **Bolivia:** conector pendiente"
        )

        st.write(
            "🇻🇪 **Venezuela:** conector pendiente"
        )

    # ========================================================
    # BOTÓN BUSCAR
    # ========================================================

    st.write("")

    buscar = st.button(
        "🔎 Buscar oportunidades reales",
        type="primary",
        use_container_width=True
    )

    # ========================================================
    # EJECUTAR BÚSQUEDA
    # ========================================================

    if buscar:

        # ----------------------------------------------------
        # VALIDAR PAÍS
        # ----------------------------------------------------

        if not paises:

            st.warning(
                "Selecciona al menos un país "
                "para realizar la búsqueda."
            )

            return

        # ----------------------------------------------------
        # VALIDAR SECTOR
        # ----------------------------------------------------

        if not sectores:

            st.warning(
                "Selecciona al menos una línea "
                "de interés."
            )

            return

        # ----------------------------------------------------
        # PAÍSES PENDIENTES
        # ----------------------------------------------------

        paises_pendientes = [
            pais
            for pais in paises
            if "Colombia" not in pais
        ]

        if paises_pendientes:

            st.warning(
                "En esta versión el motor real está "
                "conectado únicamente con Colombia. "
                "Los demás países seleccionados todavía "
                "no aportarán resultados."
            )

        # ----------------------------------------------------
        # SPINNER
        # ----------------------------------------------------

        with st.spinner(
            "INTI está consultando fuentes oficiales, "
            "analizando procesos y comparándolos "
            "con el ADN INTILED..."
        ):

            try:

                oportunidades = (
                    buscar_oportunidades(
                        paises=paises,
                        sectores=sectores,
                        palabras_adicionales=
                            palabras_adicionales,
                        excluir=excluir,
                        dias_atras=dias_atras,
                        limite_por_fuente=
                            limite_resultados,
                        score_minimo=
                            score_minimo
                    )
                )

            except Exception as error:

                st.error(
                    "No fue posible completar "
                    "la búsqueda de oportunidades."
                )

                st.exception(
                    error
                )

                return

        # ----------------------------------------------------
        # FILTRO PRESUPUESTO
        # ----------------------------------------------------

        if presupuesto_minimo > 0:

            oportunidades = [
                oportunidad
                for oportunidad
                in oportunidades
                if oportunidad.get(
                    "valor_numerico",
                    0
                ) >= presupuesto_minimo
            ]

        # ----------------------------------------------------
        # GUARDAR RESULTADOS
        # ----------------------------------------------------

        st.session_state[
            "resultados_radar"
        ] = oportunidades

        # ----------------------------------------------------
        # GUARDAR PARÁMETROS DE LA BÚSQUEDA
        # ----------------------------------------------------

        st.session_state[
            "ultima_busqueda_radar"
        ] = {

            "paises":
                paises,

            "sectores":
                sectores,

            "dias_atras":
                dias_atras,

            "score_minimo":
                score_minimo,

            "presupuesto_minimo":
                presupuesto_minimo,

            "limite":
                limite_resultados,

            "fecha":
                str(
                    date.today()
                )
        }

        # ----------------------------------------------------
        # MENSAJE
        # ----------------------------------------------------

        if oportunidades:

            st.success(
                f"INTI identificó "
                f"{len(oportunidades)} "
                "oportunidad(es) compatibles "
                "con los filtros seleccionados."
            )

        else:

            st.warning(
                "No se encontraron oportunidades "
                "que superen los filtros actuales. "
                "Puedes ampliar el periodo, reducir "
                "el Radar Score mínimo o seleccionar "
                "más líneas de interés."
            )

    # ========================================================
    # MOSTRAR RESULTADOS EXISTENTES
    # ========================================================

    if (
        "resultados_radar"
        in st.session_state
    ):

        oportunidades = (
            st.session_state[
                "resultados_radar"
            ]
        )

        if oportunidades:

            st.divider()

            # ------------------------------------------------
            # INFORMACIÓN DE ÚLTIMA BÚSQUEDA
            # ------------------------------------------------

            ultima = st.session_state.get(
                "ultima_busqueda_radar",
                {}
            )

            if ultima:

                st.caption(
                    "Última búsqueda: "
                    f"{ultima.get('fecha', '')} | "
                    f"Periodo: "
                    f"{ultima.get('dias_atras', '')} días | "
                    f"Score mínimo: "
                    f"{ultima.get('score_minimo', '')}"
                )

            # ------------------------------------------------
            # RESUMEN
            # ------------------------------------------------

            mostrar_resumen(
                oportunidades
            )

            st.divider()

            # ------------------------------------------------
            # RESULTADOS
            # ------------------------------------------------

            mostrar_resultados(
                oportunidades
            )

        else:

            st.info(
                "La última búsqueda no produjo "
                "oportunidades compatibles."
            )
