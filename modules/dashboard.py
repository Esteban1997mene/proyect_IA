import streamlit as st


def mostrar_dashboard():

    # -----------------------------
    # ENCABEZADO
    # -----------------------------

    col1, col2 = st.columns([5, 1])

    with col1:
        st.title("⚡ INTI Projects AI")
        st.caption(
            "Inteligencia para identificar, analizar "
            "y estructurar oportunidades."
        )

    with col2:
        st.write("")
        st.write("")
        st.markdown("**INTILED SAS BIC**")

    st.divider()

    # -----------------------------
    # BIENVENIDA
    # -----------------------------

    st.subheader("Centro de Inteligencia de Proyectos")

    st.write(
        "Monitorea oportunidades, analiza convocatorias "
        "y gestiona la estructuración de proyectos desde "
        "un solo lugar."
    )

    st.write("")

    # -----------------------------
    # INDICADORES
    # -----------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🔎 Detectadas",
            value="0"
        )

    with col2:
        st.metric(
            label="🎯 Viables",
            value="0"
        )

    with col3:
        st.metric(
            label="🏗️ En preparación",
            value="0"
        )

    with col4:
        st.metric(
            label="🚀 Presentadas",
            value="0"
        )

    st.write("")
    st.divider()

    # -----------------------------
    # OPORTUNIDADES
    # -----------------------------

    st.subheader("🔥 Oportunidades prioritarias")

    st.info(
        "El Radar INTI todavía no ha realizado "
        "su primera búsqueda de oportunidades."
    )

    st.write("")

    # -----------------------------
    # ALERTAS
    # -----------------------------

    col1, col2 = st.columns([2, 1])

    with col1:

        st.subheader("⚠️ Alertas")

        st.write(
            "Cuando el Radar detecte oportunidades "
            "relevantes aparecerán aquí."
        )

    with col2:

        st.subheader("🤖 INTI")

        st.success(
            "Sistema preparado para iniciar "
            "el monitoreo de oportunidades."
        )
