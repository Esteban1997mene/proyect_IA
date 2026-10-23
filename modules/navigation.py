import streamlit as st


# ============================================================
# INTI PROJECTS AI
# NAVEGACIÓN PRINCIPAL
# INTILED SAS BIC
# ============================================================


# ============================================================
# OPCIONES DEL MENÚ
# ============================================================

OPCIONES_MENU = [

    # --------------------------------------------------------
    # INICIO
    # --------------------------------------------------------

    "🏠 Dashboard",

    # --------------------------------------------------------
    # OPORTUNIDADES
    # --------------------------------------------------------

    "🔎 Radar de oportunidades",
    "🎯 Oportunidades",
    "🧠 Análisis INTILED",
    "📑 Analizador de documentos",

    # --------------------------------------------------------
    # GESTIÓN INTERNA DE PROYECTOS
    # --------------------------------------------------------

    "📊 Portafolio INTILED",
    "📅 Reuniones y avances",

    # --------------------------------------------------------
    # ESTRUCTURACIÓN
    # --------------------------------------------------------

    "🏗️ Estructuración",
    "🇨🇴 Proyectos públicos / MGA",

    # --------------------------------------------------------
    # INTELIGENCIA Y DOCUMENTACIÓN
    # --------------------------------------------------------

    "📚 Investigación",
    "📄 Generador de propuestas",
    "🏢 Biblioteca INTILED",

    # --------------------------------------------------------
    # SEGUIMIENTO
    # --------------------------------------------------------

    "📊 Seguimiento"
]


# ============================================================
# VALIDAR DESTINO
# ============================================================

def validar_destino(destino):

    if destino in OPCIONES_MENU:
        return destino

    return "🏠 Dashboard"


# ============================================================
# NAVEGAR A UNA SECCIÓN
# ============================================================

def navegar_a(destino):

    destino = validar_destino(
        destino
    )

    st.session_state[
        "navegar_a"
    ] = destino

    st.rerun()


# ============================================================
# MOSTRAR MENÚ
# ============================================================

def mostrar_menu():

    # ========================================================
    # PROCESAR REDIRECCIÓN DESDE OTRO MÓDULO
    # ========================================================

    if "navegar_a" in st.session_state:

        destino = st.session_state.pop(
            "navegar_a"
        )

        destino = validar_destino(
            destino
        )

        st.session_state[
            "menu_principal"
        ] = destino


    # ========================================================
    # OPCIÓN INICIAL
    # ========================================================

    if "menu_principal" not in st.session_state:

        st.session_state[
            "menu_principal"
        ] = "🏠 Dashboard"


    # ========================================================
    # CORREGIR OPCIÓN INVÁLIDA
    # ========================================================

    if (
        st.session_state[
            "menu_principal"
        ]
        not in OPCIONES_MENU
    ):

        st.session_state[
            "menu_principal"
        ] = "🏠 Dashboard"


    # ========================================================
    # SIDEBAR
    # ========================================================

    with st.sidebar:

        # ====================================================
        # IDENTIDAD INTI
        # ====================================================

        st.markdown(
            "## ⚡ INTI"
        )

        st.caption(
            "Projects AI"
        )

        st.divider()


        # ====================================================
        # NAVEGACIÓN
        # ====================================================

        opcion = st.radio(
            "Navegación",
            OPCIONES_MENU,
            key="menu_principal",
            label_visibility="collapsed"
        )


        # ====================================================
        # INFORMACIÓN DE CONTEXTO
        # ====================================================

        st.divider()

        st.caption(
            "INTILED SAS BIC"
        )

        st.caption(
            "INTI Projects AI"
        )


        # ====================================================
        # INDICADOR DE MÓDULO PRIVADO
        # ====================================================

        if opcion in [
            "📊 Portafolio INTILED",
            "📅 Reuniones y avances"
        ]:

            st.divider()

            st.caption(
                "🔐 Información interna"
            )

            if st.session_state.get(
                "portfolio_authenticated",
                False
            ):

                usuario = (
                    st.session_state.get(
                        "portfolio_user",
                        "Usuario"
                    )
                )

                st.success(
                    f"🔓 Sesión: {usuario}"
                )

            else:

                st.warning(
                    "🔒 Acceso restringido"
                )


    # ========================================================
    # RETORNAR OPCIÓN SELECCIONADA
    # ========================================================

    return opcion
