import streamlit as st

# ============================================================
# IMPORTACIÓN DE MÓDULOS
# ============================================================

from modules.navigation import mostrar_menu
from modules.dashboard import mostrar_dashboard
from modules.radar import mostrar_radar
from modules.opportunities import mostrar_oportunidades
from modules.analyzer import mostrar_analizador
from modules.intiled_analysis import mostrar_analisis_intiled
from modules.structuring import mostrar_estructuracion
from modules.mga import mostrar_mga
from modules.research import mostrar_investigacion
from modules.proposals import mostrar_propuestas
from modules.library import mostrar_biblioteca
from modules.tracking import mostrar_seguimiento


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="INTI Projects AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# ESTILOS GENERALES
# ============================================================

st.markdown(
    """
    <style>

    /* Ocultar menú de Streamlit */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }


    /* Contenedor principal */

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }


    /* Sidebar */

    [data-testid="stSidebar"] {
        min-width: 280px;
        max-width: 280px;
    }


    /* Botones */

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }


    /* Métricas */

    [data-testid="stMetric"] {
        border-radius: 10px;
    }


    /* Separación títulos */

    h1 {
        margin-bottom: 0.5rem;
    }

    h2 {
        margin-top: 1rem;
    }

    h3 {
        margin-top: 0.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# ESTADO GENERAL DE LA APLICACIÓN
# ============================================================

if "ingreso" not in st.session_state:
    st.session_state.ingreso = False


# ============================================================
# PORTADA
# ============================================================

def mostrar_portada():

    st.write("")
    st.write("")

    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )

    with col2:

        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        try:

            st.image(
                "assets/logo_intiled.png",
                use_container_width=True
            )

        except Exception:

            pass


        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

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
                margin-top:0px;
            ">
                Inteligencia para transformar oportunidades
                en proyectos.
            </p>
            """,
            unsafe_allow_html=True
        )

        st.write("")


        # ----------------------------------------------------
        # BOTÓN INGRESO
        # ----------------------------------------------------

        if st.button(
            "⚡ Ingresar a la plataforma",
            use_container_width=True,
            type="primary"
        ):

            st.session_state.ingreso = True

            st.rerun()


        # ----------------------------------------------------
        # PIE DE PORTADA
        # ----------------------------------------------------

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


# ============================================================
# APLICACIÓN PRINCIPAL
# ============================================================

def ejecutar_aplicacion():

    # --------------------------------------------------------
    # MENÚ LATERAL
    # --------------------------------------------------------

    opcion = mostrar_menu()


    # ========================================================
    # DASHBOARD
    # ========================================================

    if opcion == "🏠 Dashboard":

        mostrar_dashboard()


    # ========================================================
    # RADAR DE OPORTUNIDADES
    # ========================================================

    elif opcion == "🔎 Radar de oportunidades":

        mostrar_radar()


    # ========================================================
    # OPORTUNIDADES
    # ========================================================

    elif opcion == "🎯 Oportunidades":

        mostrar_oportunidades()


    # ========================================================
    # ANÁLISIS ESTRATÉGICO INTILED
    # ========================================================

    elif opcion == "🧠 Análisis INTILED":

        mostrar_analisis_intiled()


    # ========================================================
    # ANALIZADOR DE DOCUMENTOS
    # ========================================================

    elif opcion == "📑 Analizador de documentos":

        mostrar_analizador()


    # ========================================================
    # ESTRUCTURACIÓN
    # ========================================================

    elif opcion == "🏗️ Estructuración":

        mostrar_estructuracion()


    # ========================================================
    # MGA
    # ========================================================

    elif opcion == "🇨🇴 Proyectos públicos / MGA":

        mostrar_mga()


    # ========================================================
    # INVESTIGACIÓN
    # ========================================================

    elif opcion == "📚 Investigación":

        mostrar_investigacion()


    # ========================================================
    # GENERADOR DE PROPUESTAS
    # ========================================================

    elif opcion == "📄 Generador de propuestas":

        mostrar_propuestas()


    # ========================================================
    # BIBLIOTECA INTILED
    # ========================================================

    elif opcion == "🏢 Biblioteca INTILED":

        mostrar_biblioteca()


    # ========================================================
    # SEGUIMIENTO
    # ========================================================

    elif opcion == "📊 Seguimiento":

        mostrar_seguimiento()


    # ========================================================
    # OPCIÓN NO RECONOCIDA
    # ========================================================

    else:

        st.warning(
            "La opción seleccionada todavía "
            "no se encuentra disponible."
        )


# ============================================================
# EJECUCIÓN
# ============================================================

if st.session_state.ingreso:

    ejecutar_aplicacion()

else:

    mostrar_portada()
