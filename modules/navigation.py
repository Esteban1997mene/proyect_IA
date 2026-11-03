
import streamlit as st

# ============================================================
# INTI PROJECTS AI
# NAVEGACIÓN CORPORATIVA
# INTILED SAS BIC
# ============================================================

GRUPOS_MENU = [
    {
        "titulo": "GENERAL",
        "opciones": [
            ("🏠 Dashboard", "Inicio", "⌂"),
        ],
    },
    {
        "titulo": "CONVOCATORIAS",
        "opciones": [
            (
                "🔎 Radar de oportunidades",
                "Radar de convocatorias",
                "◎",
            ),
            (
                "🎯 Oportunidades",
                "Oportunidades",
                "◈",
            ),
            (
                "🧠 Análisis INTILED",
                "Análisis de viabilidad",
                "◇",
            ),
            (
                "📑 Analizador de documentos",
                "Análisis documental",
                "▤",
            ),
        ],
    },
    {
        "titulo": "PROYECTOS",
        "opciones": [
            (
                "📊 Portafolio INTILED",
                "Portafolio",
                "▦",
            ),
            (
                "📅 Reuniones y avances",
                "Reuniones y avances",
                "▣",
            ),
            (
                "🏗️ Estructuración",
                "Estructuración",
                "▥",
            ),
            (
                "🇨🇴 Proyectos públicos / MGA",
                "Proyectos públicos / MGA",
                "◉",
            ),
            (
                "📄 Generador de propuestas",
                "Generador de propuestas",
                "▧",
            ),
        ],
    },
    {
        "titulo": "INTELIGENCIA",
        "opciones": [
            (
                "📚 Investigación",
                "Investigación",
                "◫",
            ),
            (
                "🏢 Biblioteca INTILED",
                "Biblioteca",
                "▤",
            ),
        ],
    },
    {
        "titulo": "GESTIÓN",
        "opciones": [
            (
                "📊 Seguimiento",
                "Seguimiento",
                "◷",
            ),
        ],
    },
]

OPCIONES_MENU = [
    opcion[0]
    for grupo in GRUPOS_MENU
    for opcion in grupo["opciones"]
]

ALIASES = {}

for grupo in GRUPOS_MENU:
    for destino, nombre, icono in grupo["opciones"]:
        ALIASES[destino] = destino
        ALIASES[nombre] = destino

ALIASES.update({
    "Dashboard": "🏠 Dashboard",
    "Inicio": "🏠 Dashboard",
    "Convocatorias": "🔎 Radar de oportunidades",
    "Radar de oportunidades": "🔎 Radar de oportunidades",
    "Análisis INTILED": "🧠 Análisis INTILED",
    "Analizador de documentos": "📑 Analizador de documentos",
    "Portafolio INTILED": "📊 Portafolio INTILED",
    "Estructuración": "🏗️ Estructuración",
    "Proyectos públicos / MGA": "🇨🇴 Proyectos públicos / MGA",
    "Generador de propuestas": "📄 Generador de propuestas",
    "Biblioteca INTILED": "🏢 Biblioteca INTILED",
})


def cambiar_pagina(destino):
    st.session_state["inti_menu_actual"] = destino
    st.session_state["menu_principal"] = destino
    st.rerun()


def mostrar_menu():

    # Compatibilidad con redirecciones entre módulos
    destino_pendiente = st.session_state.pop(
        "navegar_a",
        None
    )

    if destino_pendiente:
        destino = ALIASES.get(
            destino_pendiente,
            destino_pendiente
        )
        if destino in OPCIONES_MENU:
            st.session_state["inti_menu_actual"] = destino

    # Compatibilidad con navegación anterior
    if "inti_menu_actual" not in st.session_state:
        anterior = st.session_state.get(
            "menu_principal",
            "🏠 Dashboard"
        )
        st.session_state["inti_menu_actual"] = (
            ALIASES.get(anterior, "🏠 Dashboard")
        )

    actual = st.session_state["inti_menu_actual"]

    if actual not in OPCIONES_MENU:
        actual = "🏠 Dashboard"
        st.session_state["inti_menu_actual"] = actual

    st.session_state["menu_principal"] = actual

    with st.sidebar:

        # Marca
        st.markdown(
            """
            <div class="inti-brand">
                <div class="inti-brand-icon">⚡</div>
                <div>
                    <div class="inti-brand-name">INTI</div>
                    <div class="inti-brand-subtitle">
                        PROJECTS ENTERPRISE
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="inti-sidebar-divider"></div>',
            unsafe_allow_html=True
        )

        # Navegación por grupos
        for grupo in GRUPOS_MENU:

            st.markdown(
                '<div class="inti-menu-heading">'
                + grupo["titulo"]
                + '</div>',
                unsafe_allow_html=True
            )

            for destino, nombre, icono in grupo["opciones"]:

                seleccionado = destino == actual

                # Identificador visual para CSS
                marcador = (
                    "inti-nav-active"
                    if seleccionado
                    else "inti-nav-normal"
                )

                with st.container(key=marcador):

                    etiqueta = f"{icono}   {nombre}"

                    if st.button(
                        etiqueta,
                        key="nav_" + destino,
                        use_container_width=True,
                        type="tertiary"
                    ):
                        cambiar_pagina(destino)

        st.markdown(
            '<div class="inti-sidebar-divider"></div>',
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="inti-sidebar-footer">
                <div class="inti-company">
                    INTILED SAS BIC
                </div>
                <div class="inti-version">
                    Plataforma de inteligencia de proyectos
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    return actual
