
import streamlit as st

# ============================================================
# INTI PROJECTS AI
# NAVEGACIÓN CORPORATIVA
# INTILED SAS BIC
# ============================================================

MENU = [
    (
        "GENERAL",
        [
            ("🏠 Dashboard", "Inicio"),
        ]
    ),
    (
        "CONVOCATORIAS",
        [
            ("🔎 Radar de oportunidades", "Radar de convocatorias"),
            ("🎯 Oportunidades", "Oportunidades"),
            ("🧠 Análisis INTILED", "Análisis de viabilidad"),
            ("📑 Analizador de documentos", "Análisis documental"),
        ]
    ),
    (
        "PROYECTOS",
        [
            ("📊 Portafolio INTILED", "Portafolio INTILED"),
            ("📅 Reuniones y avances", "Reuniones y avances"),
            ("🏗️ Estructuración", "Estructuración"),
            ("🇨🇴 Proyectos públicos / MGA", "Proyectos públicos / MGA"),
            ("📄 Generador de propuestas", "Generador de propuestas"),
        ]
    ),
    (
        "INTELIGENCIA",
        [
            ("📚 Investigación", "Investigación"),
            ("🏢 Biblioteca INTILED", "Biblioteca INTILED"),
        ]
    ),
    (
        "GESTIÓN",
        [
            ("📊 Seguimiento", "Seguimiento"),
        ]
    ),
]

OPCIONES_MENU = [
    destino
    for _, opciones in MENU
    for destino, _ in opciones
]

ALIASES = {}

for _, opciones in MENU:
    for destino, nombre in opciones:
        ALIASES[destino] = destino
        ALIASES[nombre] = destino

ALIASES.update({
    "Dashboard": "🏠 Dashboard",
    "Inicio": "🏠 Dashboard",
    "Radar de oportunidades": "🔎 Radar de oportunidades",
    "Convocatorias": "🔎 Radar de oportunidades",
    "Análisis INTILED": "🧠 Análisis INTILED",
    "Analizador de documentos": "📑 Analizador de documentos",
    "Portafolio INTILED": "📊 Portafolio INTILED",
    "Estructuración": "🏗️ Estructuración",
    "Proyectos públicos / MGA": "🇨🇴 Proyectos públicos / MGA",
    "Generador de propuestas": "📄 Generador de propuestas",
    "Biblioteca INTILED": "🏢 Biblioteca INTILED",
    "Seguimiento": "📊 Seguimiento",
})


def cambiar_pagina(destino):
    destino = ALIASES.get(destino, destino)

    if destino not in OPCIONES_MENU:
        return

    st.session_state["inti_menu_actual"] = destino
    st.session_state["menu_principal"] = destino
    st.rerun()


def mostrar_menu():

    destino_pendiente = st.session_state.pop(
        "navegar_a", None
    )

    if destino_pendiente:
        destino = ALIASES.get(
            destino_pendiente,
            destino_pendiente
        )

        if destino in OPCIONES_MENU:
            st.session_state["inti_menu_actual"] = destino

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

        st.markdown(
            """
            <div class="inti-brand">
                <div class="inti-brand-icon">I</div>
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

        for titulo, opciones in MENU:

            st.markdown(
                f'<div class="inti-menu-heading">{titulo}</div>',
                unsafe_allow_html=True
            )

            for destino, nombre in opciones:

                indice = OPCIONES_MENU.index(destino)
                seleccionado = destino == actual

                if st.button(
                    nombre,
                    key=f"inti_menu_boton_{indice}",
                    use_container_width=True,
                    type=(
                        "primary"
                        if seleccionado
                        else "tertiary"
                    )
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
                    Inteligencia y gestión de proyectos
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    return actual
