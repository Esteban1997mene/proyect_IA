import streamlit as st

from modules.navigation import mostrar_menu
from modules.dashboard import mostrar_dashboard
from modules.radar import mostrar_radar
from modules.opportunities import mostrar_oportunidades
from modules.analyzer import mostrar_analizador
from modules.structuring import mostrar_estructuracion
from modules.mga import mostrar_mga
from modules.research import mostrar_investigacion
from modules.proposals import mostrar_propuestas
from modules.library import mostrar_biblioteca
from modules.tracking import mostrar_seguimiento


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="INTI Projects AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# ESTILOS
# =========================================================

st.markdown(
    """
    <style>

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        min-width: 280px;
        max-width: 280px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# ESTADO DE INGRESO
# =========================================================

if "ingreso" not in st.session_state:
    st.session_state.ingreso = False


# =========================================================
# PORTADA
# =========================================================

def mostrar_portada():

    st.write("")
    st.write("")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        try:
            st.image(
                "assets/logo_intiled.png",
                use_container_width=True
            )
        except:
            pass

        st.markdown(
            """
            <h1 style="
                text-align:center;
                font-size:50px;
                margin-bottom:5px;
            ">
                INTI PROJECTS AI
            </h1>

            <p style="
                text-align:center;
                font-size:21px;
                color:#777777;
            ">
                Inteligencia para transformar oportunidades
                en proyectos.
            </p>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        if st.button(
            "⚡ Ingresar a la plataforma",
            use_container_width=True,
            type="primary"
        ):

            st.session_state.ingreso = True
            st.rerun()

        st.markdown(
            """
            <p style="
                text-align:center;
                margin-top:50px;
                color:#888888;
                font-size:13px;
            ">
                Plataforma interna de inteligencia de proyectos
                <br>
                INTILED SAS BIC
            </p>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# APLICACIÓN
# =========================================================

def ejecutar_aplicacion():

    opcion = mostrar_menu()

    if opcion == "🏠 Dashboard":
        mostrar_dashboard()

    elif opcion == "🔎 Radar de oportunidades":
        mostrar_radar()

    elif opcion == "🎯 Oportunidades":
        mostrar_oportunidades()

    elif opcion == "🧠 Analizador IA":
        mostrar_analizador()

    elif opcion == "🏗️ Estructuración":
        mostrar_estructuracion()

    elif opcion == "🇨🇴 Proyectos públicos / MGA":
        mostrar_mga()

    elif opcion == "📚 Investigación":
        mostrar_investigacion()

    elif opcion == "📄 Generador de propuestas":
        mostrar_propuestas()

    elif opcion == "🏢 Biblioteca INTILED":
        mostrar_biblioteca()

    elif opcion == "📊 Seguimiento":
        mostrar_seguimiento()


# =========================================================
# EJECUCIÓN
# =========================================================

if st.session_state.ingreso:

    ejecutar_aplicacion()

else:

    mostrar_portada()
