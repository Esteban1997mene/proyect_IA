import streamlit as st


OPCIONES_MENU = [
    "Dashboard",
    "Radar de oportunidades",
    "Oportunidades",
    "Análisis INTILED",
    "Analizador de documentos",
    "Portafolio INTILED"
    "Estructuración",
    "Proyectos públicos / MGA",
    "Investigación",
    "Generador de propuestas",
    "Biblioteca INTILED",
    "Seguimiento"
]


def mostrar_menu():

    # ========================================================
    # NAVEGACIÓN SOLICITADA DESDE OTRO MÓDULO
    # ========================================================

    if "navegar_a" in st.session_state:

        destino = st.session_state.pop(
            "navegar_a"
        )

        if destino in OPCIONES_MENU:

            st.session_state[
                "menu_principal"
            ] = destino

    # ========================================================
    # VALOR INICIAL
    # ========================================================

    if "menu_principal" not in st.session_state:

        st.session_state[
            "menu_principal"
        ] = "🏠 Dashboard"

    # ========================================================
    # SIDEBAR
    # ========================================================

    with st.sidebar:

        st.markdown(
            "## ⚡ INTI"
        )

        st.caption(
            "Projects AI"
        )

        st.divider()

        opcion = st.radio(
            "Navegación",
            OPCIONES_MENU,
            key="menu_principal",
            label_visibility="collapsed"
        )

        st.divider()

        st.caption(
            "INTILED SAS BIC"
        )

        st.caption(
            "INTI Projects AI"
        )

    return opcion
