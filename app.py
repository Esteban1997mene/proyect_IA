import streamlit as st

# ============================================================
# INTI PROJECTS AI
# APLICACIÓN PRINCIPAL
# INTILED SAS BIC
# ============================================================


# ============================================================
# IMPORTACIÓN DE MÓDULOS
# ============================================================

from modules.navigation import mostrar_menu

# Inicio
from modules.dashboard import mostrar_dashboard

# Oportunidades
from modules.radar import mostrar_radar
from modules.opportunities import mostrar_oportunidades
from modules.intiled_analysis import mostrar_analisis_intiled
from modules.analyzer import mostrar_analizador

# Gestión interna
from modules.portfolio import mostrar_portafolio
from modules.meetings import mostrar_reuniones

# Estructuración
from modules.structuring import mostrar_estructuracion
from modules.mga import mostrar_mga

# Inteligencia y documentación
from modules.research import mostrar_investigacion
from modules.proposals import mostrar_propuestas
from modules.library import mostrar_biblioteca

# Seguimiento
from modules.tracking import mostrar_seguimiento


# ============================================================
# CONFIGURACIÓN GENERAL DE STREAMLIT
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

    /* ======================================================
       OCULTAR ELEMENTOS NATIVOS DE STREAMLIT
       ====================================================== */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }


    /* ======================================================
       CONTENEDOR PRINCIPAL
       ====================================================== */

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }


    /* ======================================================
       SIDEBAR
       ====================================================== */

    [data-testid="stSidebar"] {
        min-width: 285px;
        max-width: 285px;
    }


    /* ======================================================
       BOTONES
       ====================================================== */

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }

    .stLinkButton > a {
        border-radius: 8px;
        font-weight: 600;
    }


    /* ======================================================
       MÉTRICAS
       ====================================================== */

    [data-testid="stMetric"] {
        border-radius: 10px;
    }


    /* ======================================================
       TÍTULOS
       ====================================================== */

    h1 {
        margin-bottom: 0.5rem;
    }

    h2 {
        margin-top: 1rem;
    }

    h3 {
        margin-top: 0.5rem;
    }


    /* ======================================================
       FORMULARIOS
       ====================================================== */

    [data-testid="stForm"] {
        border-radius: 12px;
    }


    /* ======================================================
       TABLAS
       ====================================================== */

    [data-testid="stDataFrame"] {
        border-radius: 10px;
    }


    /* ======================================================
       CONTENEDORES
       ====================================================== */

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px;
    }


    /* ======================================================
       TABS
       ====================================================== */

    button[data-baseweb="tab"] {
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# ESTADOS GENERALES
# ============================================================

if "ingreso" not in st.session_state:
    st.session_state["ingreso"] = False


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

        # ====================================================
        # LOGO
        # ====================================================

        try:

            st.image(
                "assets/logo_intiled.png",
                use_container_width=True
            )

        except Exception:

            pass


        # ====================================================
        # NOMBRE DE LA PLATAFORMA
        # ====================================================

        st.markdown(
            """
            <h1
                style="
                    text-align:center;
                    font-size:50px;
                    margin-bottom:5px;
                "
            >
                INTI PROJECTS AI
            </h1>

            <p
                style="
                    text-align:center;
                    font-size:21px;
                    color:#777777;
                    margin-top:0px;
                "
            >
                Inteligencia para transformar
                oportunidades en proyectos.
            </p>
            """,
            unsafe_allow_html=True
        )

        st.write("")


        # ====================================================
        # BOTÓN DE INGRESO
        # ====================================================

        if st.button(
            "⚡ Ingresar a la plataforma",
            use_container_width=True,
            type="primary",
            key="boton_ingreso_principal"
        ):

            st.session_state[
                "ingreso"
            ] = True

            st.rerun()


        # ====================================================
        # DESCRIPCIÓN
        # ====================================================

        st.markdown(
            """
            <p
                style="
                    text-align:center;
                    margin-top:35px;
                    color:#777777;
                    font-size:14px;
                    line-height:1.6;
                "
            >
                Radar de oportunidades · Inteligencia de proyectos
                <br>
                Estructuración · Portafolio · Seguimiento
            </p>
            """,
            unsafe_allow_html=True
        )


        # ====================================================
        # INFORMACIÓN INSTITUCIONAL
        # ====================================================

        st.markdown(
            """
            <p
                style="
                    text-align:center;
                    margin-top:35px;
                    color:#999999;
                    font-size:12px;
                "
            >
                Plataforma interna de inteligencia
                y gestión de proyectos
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

    # ========================================================
    # MENÚ
    # ========================================================

    opcion = mostrar_menu()


    # ========================================================
    # DASHBOARD
    # ========================================================

    if opcion == "🏠 Dashboard":

        mostrar_dashboard()


    # ========================================================
    # RADAR
    # ========================================================

    elif opcion == "🔎 Radar de oportunidades":

        mostrar_radar()


    # ========================================================
    # OPORTUNIDADES
    # ========================================================

    elif opcion == "🎯 Oportunidades":

        mostrar_oportunidades()


    # ========================================================
    # ANÁLISIS INTILED
    # ========================================================

    elif opcion == "🧠 Análisis INTILED":

        mostrar_analisis_intiled()


    # ========================================================
    # ANALIZADOR DOCUMENTAL
    # ========================================================

    elif opcion == "📑 Analizador de documentos":

        mostrar_analizador()


    # ========================================================
    # PORTAFOLIO INTILED
    # ========================================================

    elif opcion == "📊 Portafolio INTILED":

        mostrar_portafolio()


    # ========================================================
    # REUNIONES Y AVANCES
    # ========================================================

    elif opcion == "📅 Reuniones y avances":

        mostrar_reuniones()


    # ========================================================
    # ESTRUCTURACIÓN
    # ========================================================

    elif opcion == "🏗️ Estructuración":

        mostrar_estructuracion()


    # ========================================================
    # PROYECTOS PÚBLICOS / MGA
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
# CONTROL PRINCIPAL
# ============================================================

if st.session_state[
    "ingreso"
]:

    ejecutar_aplicacion()

else:

    mostrar_portada()

    mostrar_portada()
