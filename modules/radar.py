import streamlit as st
from datetime import date

from services.search_service import ejecutar_radar


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def obtener_bandera(pais):
    banderas = {
        "Colombia": "🇨🇴",
        "Ecuador": "🇪🇨",
        "Perú": "🇵🇪",
        "Bolivia": "🇧🇴",
        "Venezuela": "🇻🇪"
    }

    return banderas.get(pais, "🌎")


def guardar_para_analisis(oportunidad):
    """
    Guarda la oportunidad seleccionada para que posteriormente
    pueda ser utilizada por el Analizador IA.
    """

    st.session_state["oportunidad_web"] = oportunidad
    st.session_state["solicitar_analisis"] = True


# =========================================================
# TARJETA DE RESULTADO
# =========================================================

def mostrar_tarjeta_oportunidad(oportunidad, indice):

    pais = oportunidad.get(
        "pais",
        "No identificado"
    )

    bandera = obtener_bandera(pais)

    titulo = oportunidad.get(
        "titulo",
        "Oportunidad sin título"
    )

    fuente = oportunidad.get(
        "fuente",
        "Fuente no identificada"
    )

    sector = oportunidad.get(
        "sector",
        "No identificado"
    )

    fecha_deteccion = oportunidad.get(
        "fecha_deteccion",
        "No disponible"
    )

    url = oportunidad.get(
        "url",
        ""
    )

    with st.container(border=True):

        col1, col2 = st.columns(
            [4, 1]
        )

        # =================================================
        # INFORMACIÓN
        # =================================================

        with col1:

            st.subheader(titulo)

            info1, info2, info3 = st.columns(3)

            with info1:
                st.caption("PAÍS")
                st.write(
                    f"{bandera} {pais}"
                )

            with info2:
                st.caption("FUENTE")
                st.write(fuente)

            with info3:
                st.caption("LÍNEA")
                st.write(sector)

            st.write("")

            st.caption(
                f"Detectado por INTI: {fecha_deteccion}"
            )

            if url:

                st.link_button(
                    "🌐 Ver fuente original",
                    url
                )

        # =================================================
        # ACCIONES
        # =================================================

        with col2:

            st.caption(
                "ANÁLISIS INTI"
            )

            st.info(
                "Pendiente de análisis"
            )

            if st.button(
                "🧠 Analizar",
                key=f"analizar_web_{indice}",
                use_container_width=True,
                type="primary"
            ):

                guardar_para_analisis(
                    oportunidad
                )

                st.success(
                    "Enviada al Analizador IA."
                )


# =========================================================
# RESULTADOS
# =========================================================

def mostrar_resultados_radar():

    if "resultados_radar" not in st.session_state:
        return

    oportunidades = st.session_state[
        "resultados_radar"
    ]

    if not oportunidades:
        return

    st.divider()

    # =====================================================
    # RESUMEN
    # =====================================================

    st.subheader(
        "📡 Resultados del Radar"
    )

    total = len(oportunidades)

    paises_detectados = len(
        set(
            oportunidad.get("pais")
            for oportunidad in oportunidades
            if oportunidad.get("pais")
        )
    )

    fuentes_detectadas = len(
        set(
            oportunidad.get("fuente")
            for oportunidad in oportunidades
            if oportunidad.get("fuente")
        )
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Resultados",
            total
        )

    with col2:
        st.metric(
            "Países",
            paises_detectados
        )

    with col3:
        st.metric(
            "Fuentes",
            fuentes_detectadas
        )

    st.write("")

    # =====================================================
    # RESULTADOS
    # =====================================================

    for indice, oportunidad in enumerate(
        oportunidades
    ):

        mostrar_tarjeta_oportunidad(
            oportunidad,
            indice
        )


# =========================================================
# RADAR PRINCIPAL
# =========================================================

def mostrar_radar():

    # =====================================================
    # ENCABEZADO
    # =====================================================

    st.title(
        "🔎 Radar de oportunidades"
    )

    st.caption(
        "Identificación preliminar de convocatorias, "
        "licitaciones y oportunidades relacionadas con "
        "las líneas estratégicas de INTILED."
    )

    st.divider()

    # =====================================================
    # CONFIGURACIÓN
    # =====================================================

    st.subheader(
        "🎯 Configuración de búsqueda"
    )

    col1, col2, col3 = st.columns(3)

    # =====================================================
    # PAÍSES
    # =====================================================

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
                "Selecciona los países en los que "
                "INTI buscará oportunidades."
            )
        )

    # =====================================================
    # SECTORES
    # =====================================================

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
                "Energía solar"
            ],
            help=(
                "Selecciona las líneas estratégicas "
                "que se utilizarán para buscar oportunidades."
            )
        )

    # =====================================================
    # FINANCIACIÓN
    # =====================================================

    with col3:

        financiacion = st.multiselect(
            "Tipo de oportunidad",
            [
                "Recursos públicos",
                "Recursos privados",
                "Cooperación internacional",
                "Banca multilateral",
                "Convocatorias de innovación"
            ],
            help=(
                "Este filtro será utilizado de forma "
                "más avanzada cuando integremos "
                "los conectores oficiales."
            )
        )

    # =====================================================
    # SEGUNDA FILA
    # =====================================================

    col4, col5, col6 = st.columns(3)

    with col4:

        score_minimo = st.slider(
            "INTILED Score mínimo",
            min_value=0,
            max_value=100,
            value=60,
            step=5,
            help=(
                "En la siguiente fase este valor "
                "filtrará automáticamente las "
                "oportunidades analizadas por INTI."
            )
        )

    with col5:

        presupuesto_minimo = st.number_input(
            "Presupuesto mínimo",
            min_value=0,
            value=0,
            step=10000000,
            help=(
                "Filtro preparado para la integración "
                "con fuentes que proporcionen cuantías."
            )
        )

    with col6:

        fecha_busqueda = st.date_input(
            "Fecha de búsqueda",
            value=date.today()
        )

    # =====================================================
    # CONFIGURACIÓN AVANZADA
    # =====================================================

    with st.expander(
        "⚙️ Configuración avanzada"
    ):

        palabras_adicionales = st.text_area(
            "Palabras clave adicionales",
            placeholder=(
                "Ejemplo: luminarias solares, "
                "sistemas fotovoltaicos, RETILAP, "
                "telegestión, microrredes..."
            )
        )

        terminos_excluidos = st.text_area(
            "Excluir términos",
            placeholder=(
                "Ejemplo: hidrocarburos, minería, "
                "combustibles..."
            )
        )

        st.caption(
            "Las palabras adicionales y exclusiones "
            "quedan preparadas para integrarse al "
            "motor semántico en la siguiente fase."
        )

    st.write("")

    # =====================================================
    # INFORMACIÓN DE BÚSQUEDA
    # =====================================================

    with st.container(border=True):

        st.markdown(
            "#### 🤖 Radar INTI"
        )

        st.write(
            "INTI explorará fuentes relacionadas con "
            "los países y líneas seleccionadas para "
            "identificar posibles oportunidades."
        )

        st.caption(
            "Los resultados actuales son preliminares. "
            "Posteriormente serán verificados contra "
            "fuentes oficiales y analizados mediante IA."
        )

    st.write("")

    # =====================================================
    # BOTÓN BUSCAR
    # =====================================================

    buscar = st.button(
        "🔎 Buscar oportunidades",
        type="primary",
        use_container_width=True
    )

    # =====================================================
    # EJECUTAR BÚSQUEDA
    # =====================================================

    if buscar:

        # -------------------------------------------------
        # VALIDAR PAÍSES
        # -------------------------------------------------

        if not paises:

            st.warning(
                "Selecciona al menos un país "
                "para realizar la búsqueda."
            )

            return

        # -------------------------------------------------
        # VALIDAR SECTORES
        # -------------------------------------------------

        if not sectores:

            st.warning(
                "Selecciona al menos una línea "
                "de interés."
            )

            return

        # -------------------------------------------------
        # ESTADO DE BÚSQUEDA
        # -------------------------------------------------

        with st.status(
            "🔎 INTI está explorando oportunidades...",
            expanded=True
        ) as status:

            st.write(
                "🌎 Identificando países seleccionados..."
            )

            st.write(
                "🏛️ Consultando fuentes disponibles..."
            )

            st.write(
                "⚡ Buscando coincidencias con las "
                "líneas estratégicas..."
            )

            # =============================================
            # MOTOR DE BÚSQUEDA
            # =============================================

            try:

                oportunidades = ejecutar_radar(
                    paises,
                    sectores
                )

                # =========================================
                # GUARDAR RESULTADOS
                # =========================================

                st.session_state[
                    "resultados_radar"
                ] = oportunidades

                status.update(
                    label="✅ Búsqueda finalizada",
                    state="complete",
                    expanded=False
                )

            except Exception as error:

                oportunidades = []

                st.session_state[
                    "resultados_radar"
                ] = []

                status.update(
                    label="❌ Error durante la búsqueda",
                    state="error",
                    expanded=True
                )

                st.error(
                    "No fue posible completar "
                    "la búsqueda."
                )

                st.code(
                    str(error)
                )

        # =================================================
        # MENSAJE FINAL
        # =================================================

        if oportunidades:

            st.success(
                f"INTI identificó "
                f"{len(oportunidades)} "
                "resultados preliminares."
            )

        else:

            st.warning(
                "No se encontraron oportunidades "
                "con los parámetros seleccionados."
            )

            st.caption(
                "Puedes intentar seleccionar otra "
                "línea de interés o ampliar los países."
            )

    # =====================================================
    # MOSTRAR RESULTADOS GUARDADOS
    # =====================================================

    mostrar_resultados_radar()
