import streamlit as st
from datetime import date


def mostrar_radar():

    # =====================================================
    # ENCABEZADO
    # =====================================================

    st.title("🔎 Radar de oportunidades")

    st.caption(
        "Identificación y análisis de convocatorias, "
        "licitaciones y oportunidades de proyectos."
    )

    st.divider()

    # =====================================================
    # FILTROS
    # =====================================================

    st.subheader("🎯 Configuración de búsqueda")

    col1, col2, col3 = st.columns(3)

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
                "🇨🇴 Colombia",
                "🇪🇨 Ecuador",
                "🇵🇪 Perú",
                "🇧🇴 Bolivia"
            ]
        )

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
                "Transición energética"
            ]
        )

    with col3:
        financiacion = st.multiselect(
            "Tipo de oportunidad",
            [
                "Recursos públicos",
                "Recursos privados",
                "Cooperación internacional",
                "Banca multilateral",
                "Convocatorias de innovación"
            ]
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        score_minimo = st.slider(
            "INTILED Score mínimo",
            min_value=0,
            max_value=100,
            value=60,
            step=5
        )

    with col5:
        presupuesto_minimo = st.number_input(
            "Presupuesto mínimo",
            min_value=0,
            value=0,
            step=10000000,
            help="Valor de referencia. Posteriormente se manejará por moneda."
        )

    with col6:
        fecha_busqueda = st.date_input(
            "Fecha de búsqueda",
            value=date.today()
        )

    st.write("")

    # =====================================================
    # PALABRAS CLAVE
    # =====================================================

    with st.expander("⚙️ Configuración avanzada"):

        palabras = st.text_area(
            "Palabras clave adicionales",
            placeholder=(
                "Ejemplo: luminarias solares, sistemas fotovoltaicos, "
                "telegestión, eficiencia energética..."
            )
        )

        excluir = st.text_area(
            "Excluir términos",
            placeholder=(
                "Ejemplo: hidrocarburos, minería, combustibles..."
            )
        )

    st.write("")

    # =====================================================
    # BOTÓN DE BÚSQUEDA
    # =====================================================

    buscar = st.button(
        "🔎 Buscar oportunidades",
        type="primary",
        use_container_width=True
    )

    # =====================================================
    # BÚSQUEDA
    # =====================================================

    if buscar:

        if not paises:

            st.warning(
                "Selecciona al menos un país para realizar la búsqueda."
            )

            return

        if not sectores:

            st.warning(
                "Selecciona al menos una línea de interés."
            )

            return

        with st.spinner(
            "INTI está buscando oportunidades..."
        ):

            # En la siguiente fase esta información
            # vendrá del motor de búsqueda real.

            oportunidades_demo = [
                {
                    "pais": "🇨🇴 Colombia",
                    "proyecto": "Modernización de alumbrado público",
                    "entidad": "Entidad pública",
                    "tipo": "Recursos públicos",
                    "presupuesto": "$2.800 millones COP",
                    "cierre": "28/10/2026",
                    "score": 92
                },
                {
                    "pais": "🇪🇨 Ecuador",
                    "proyecto": "Sistema solar fotovoltaico institucional",
                    "entidad": "Entidad contratante",
                    "tipo": "Recursos públicos",
                    "presupuesto": "USD 620.000",
                    "cierre": "04/11/2026",
                    "score": 87
                },
                {
                    "pais": "🇵🇪 Perú",
                    "proyecto": "Sistemas de eficiencia energética",
                    "entidad": "Entidad regional",
                    "tipo": "Cooperación internacional",
                    "presupuesto": "USD 410.000",
                    "cierre": "12/11/2026",
                    "score": 78
                }
            ]

        st.success(
            f"Se identificaron {len(oportunidades_demo)} "
            "oportunidades preliminares."
        )

        st.divider()

        mostrar_resultados(
            oportunidades_demo,
            score_minimo
        )


def mostrar_resultados(oportunidades, score_minimo):

    st.subheader("📋 Oportunidades identificadas")

    oportunidades_filtradas = [
        oportunidad
        for oportunidad in oportunidades
        if oportunidad["score"] >= score_minimo
    ]

    if not oportunidades_filtradas:

        st.warning(
            "No existen oportunidades que cumplan "
            "el Score mínimo seleccionado."
        )

        return

    for i, oportunidad in enumerate(
        oportunidades_filtradas
    ):

        score = oportunidad["score"]

        if score >= 80:
            estado = "🟢 Alta oportunidad"

        elif score >= 60:
            estado = "🟡 Analizar"

        elif score >= 40:
            estado = "🟠 Baja compatibilidad"

        else:
            estado = "🔴 No recomendada"

        with st.container(border=True):

            col1, col2 = st.columns([4, 1])

            with col1:

                st.subheader(
                    oportunidad["proyecto"]
                )

                st.write(
                    f"**País:** {oportunidad['pais']}"
                )

                st.write(
                    f"**Entidad:** {oportunidad['entidad']}"
                )

                st.write(
                    f"**Financiación:** {oportunidad['tipo']}"
                )

                st.write(
                    f"**Presupuesto:** {oportunidad['presupuesto']}"
                )

                st.write(
                    f"**Fecha de cierre:** {oportunidad['cierre']}"
                )

            with col2:

                st.metric(
                    "INTILED Score",
                    f"{score}/100"
                )

                st.write(f"**{estado}**")

                if st.button(
                    "🧠 Analizar",
                    key=f"analizar_{i}",
                    use_container_width=True
                ):

                    st.session_state[
                        "oportunidad_seleccionada"
                    ] = oportunidad

                    st.success(
                        "Oportunidad seleccionada "
                        "para análisis."
                    )
