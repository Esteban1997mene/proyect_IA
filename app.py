
import streamlit as st
from pathlib import Path
import base64

# ============================================================
# INTI PROJECTS AI
# PLATAFORMA CORPORATIVA INTILED SAS BIC
# ============================================================

from modules.navigation import mostrar_menu
from modules.dashboard import mostrar_dashboard
from modules.radar import mostrar_radar
from modules.opportunities import mostrar_oportunidades
from modules.intiled_analysis import mostrar_analisis_intiled
from modules.analyzer import mostrar_analizador
from modules.portfolio import mostrar_portafolio
from modules.structuring import mostrar_estructuracion
from modules.mga import mostrar_mga
from modules.research import mostrar_investigacion
from modules.proposals import mostrar_propuestas
from modules.library import mostrar_biblioteca
from modules.tracking import mostrar_seguimiento


# ============================================================
# CONFIGURACIÓN PRINCIPAL
# ============================================================

st.set_page_config(
    page_title="INTI Projects | INTILED",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

COLOR_NARANJA = "#F47721"
COLOR_OSCURO = "#202630"


# ============================================================
# CARGAR ESTILOS CORPORATIVOS
# ============================================================

def cargar_estilos():

    ruta_css = ASSETS_DIR / "styles.css"

    if ruta_css.exists():

        contenido_css = ruta_css.read_text(
            encoding="utf-8"
        )

        st.markdown(
            f"<style>{contenido_css}</style>",
            unsafe_allow_html=True
        )

    else:

        st.warning(
            "No se encontró assets/styles.css. "
            "La aplicación utilizará los estilos básicos."
        )


cargar_estilos()


# ============================================================
# LOGO CORPORATIVO
# ============================================================

def obtener_logo_base64():

    ruta_logo = ASSETS_DIR / "logo_intiled.png"

    if not ruta_logo.exists():
        return None

    try:

        contenido = ruta_logo.read_bytes()

        return base64.b64encode(
            contenido
        ).decode("utf-8")

    except Exception:

        return None


# ============================================================
# ESTADO GENERAL
# ============================================================

if "ingreso" not in st.session_state:
    st.session_state["ingreso"] = False

if "oportunidad_seleccionada" not in st.session_state:
    st.session_state["oportunidad_seleccionada"] = None


# ============================================================
# PORTADA CORPORATIVA
# ============================================================

def mostrar_portada():

    logo_base64 = obtener_logo_base64()

    if logo_base64:

        logo_html = (
            '<img class="inti-welcome-logo" '
            'src="data:image/png;base64,'
            + logo_base64
            + '" alt="INTILED">'
        )

    else:

        logo_html = (
            '<div class="inti-welcome-symbol">⚡</div>'
        )

    st.markdown(
        """
        <style>

        /* ==========================================
           PORTADA CORPORATIVA
           ========================================== */

        section[data-testid="stSidebar"] {
            display: none;
        }

        [data-testid="stAppViewContainer"] {
            background: #111821;
        }

        .block-container {
            max-width: 1000px;
            padding-top: 6vh;
        }

        .inti-welcome {
            position: relative;
            overflow: hidden;
            min-height: 510px;
            border-radius: 26px;
            background:
                radial-gradient(
                    circle at 80% 25%,
                    rgba(244,119,33,0.20),
                    transparent 38%
                ),
                linear-gradient(
                    135deg,
                    #202630 0%,
                    #111821 65%,
                    #26313F 100%
                );
            border: 1px solid rgba(255,255,255,0.10);
            padding: 64px 45px 38px;
            text-align: center;
            box-shadow: 0 22px 65px rgba(0,0,0,0.22);
        }

        .inti-welcome::before {
            content: "";
            position: absolute;
            width: 380px;
            height: 380px;
            border: 1px solid rgba(244,119,33,0.18);
            border-radius: 50%;
            top: -140px;
            right: -120px;
            box-shadow:
                0 0 0 45px rgba(244,119,33,0.025),
                0 0 0 95px rgba(244,119,33,0.018);
            animation: intiPulse 8s ease-in-out infinite;
            pointer-events: none;
        }

        .inti-welcome::after {
            content: "";
            position: absolute;
            width: 500px;
            height: 2px;
            left: -80px;
            bottom: 100px;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(244,119,33,0.65),
                transparent
            );
            transform: rotate(-24deg);
            animation: intiEnergy 7s ease-in-out infinite;
            pointer-events: none;
        }

        .inti-welcome-logo {
            position: relative;
            z-index: 1;
            max-width: 215px;
            max-height: 125px;
            object-fit: contain;
            margin-bottom: 28px;
        }

        .inti-welcome-symbol {
            font-size: 72px;
            margin-bottom: 20px;
        }

        .inti-welcome-label {
            position: relative;
            z-index: 1;
            display: inline-block;
            color: #FFAD72;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 3px;
            margin-bottom: 15px;
        }

        .inti-welcome-title {
            position: relative;
            z-index: 1;
            font-size: clamp(38px, 5vw, 66px);
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: -2px;
            line-height: 1.1;
            margin: 0;
        }

        .inti-welcome-title span {
            color: #F47721;
        }

        .inti-welcome-description {
            position: relative;
            z-index: 1;
            max-width: 620px;
            margin: 22px auto 0;
            color: #CAD0D8;
            font-size: 17px;
            line-height: 1.8;
        }

        .inti-welcome-divider {
            height: 1px;
            max-width: 420px;
            margin: 36px auto 22px;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255,255,255,0.25),
                transparent
            );
        }

        .inti-welcome-footer {
            color: #9DA8B5;
            font-size: 12px;
            letter-spacing: 1px;
        }

        @keyframes intiPulse {
            0%, 100% {
                transform: scale(1);
                opacity: 0.55;
            }
            50% {
                transform: scale(1.12);
                opacity: 1;
            }
        }

        @keyframes intiEnergy {
            0%, 100% {
                transform: translateX(-90px) rotate(-24deg);
                opacity: 0.2;
            }
            50% {
                transform: translateX(180px) rotate(-24deg);
                opacity: 0.8;
            }
        }

        @media (max-width: 768px) {
            .inti-welcome {
                min-height: 420px;
                padding: 42px 20px 28px;
            }

            .inti-welcome-description {
                font-size: 14px;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            .inti-welcome::before,
            .inti-welcome::after {
                animation: none;
            }
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="inti-welcome">
            {logo_html}

            <div class="inti-welcome-label">
                INTELIGENCIA Y GESTIÓN DE PROYECTOS
            </div>

            <h1 class="inti-welcome-title">
                INTI <span>PROJECTS</span>
            </h1>

            <p class="inti-welcome-description">
                Descubre oportunidades, evalúa convocatorias,
                estructura proyectos y desarrolla propuestas
                estratégicas desde una sola plataforma.
            </p>

            <div class="inti-welcome-divider"></div>

            <div class="inti-welcome-footer">
                INTILED SAS BIC · PLATAFORMA CORPORATIVA
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    col1, col2, col3 = st.columns(
        [1, 1.3, 1]
    )

    with col2:

        if st.button(
            "Ingresar a INTI Projects",
            type="primary",
            use_container_width=True,
            key="inti_ingresar"
        ):

            st.session_state["ingreso"] = True
            st.rerun()

    st.markdown(
        """
        <p style="
            text-align:center;
            color:#AAB2BD;
            font-size:12px;
            margin-top:25px;
        ">
            Innovación · Energía · Tecnología · Proyectos
        </p>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# BARRA SUPERIOR
# ============================================================

def mostrar_barra_superior():

    with st.sidebar:

        st.divider()

        st.caption(
            "INTILED SAS BIC"
        )

        if st.button(
            "Volver a la portada",
            use_container_width=True,
            key="inti_volver_portada"
        ):

            st.session_state["ingreso"] = False
            st.rerun()


# ============================================================
# NAVEGACIÓN ENTRE MÓDULOS
# ============================================================

def ejecutar_modulo(opcion):

    rutas = {

        "🏠 Dashboard":
            mostrar_dashboard,

        "🔎 Radar de oportunidades":
            mostrar_radar,

        "🎯 Oportunidades":
            mostrar_oportunidades,

        "🧠 Análisis INTILED":
            mostrar_analisis_intiled,

        "📑 Analizador de documentos":
            mostrar_analizador,

        "📊 Portafolio INTILED":
            mostrar_portafolio,

        "🏗️ Estructuración":
            mostrar_estructuracion,

        "🇨🇴 Proyectos públicos / MGA":
            mostrar_mga,

        "📚 Investigación":
            mostrar_investigacion,

        "📄 Generador de propuestas":
            mostrar_propuestas,

        "🏢 Biblioteca INTILED":
            mostrar_biblioteca,

        "📊 Seguimiento":
            mostrar_seguimiento
    }

    # Módulo de reuniones: opcional mientras
    # completamos el desarrollo.

    try:

        from modules.meetings import mostrar_reuniones

        rutas[
            "📅 Reuniones y avances"
        ] = mostrar_reuniones

    except ImportError:

        pass

    # Alias para mantener compatibilidad
    # con los nombres actuales del menú.

    alias = {

        "Inicio":
            "🏠 Dashboard",

        "Dashboard":
            "🏠 Dashboard",

        "Radar de oportunidades":
            "🔎 Radar de oportunidades",

        "Convocatorias":
            "🔎 Radar de oportunidades",

        "Oportunidades":
            "🎯 Oportunidades",

        "Análisis INTILED":
            "🧠 Análisis INTILED",

        "Analizador de documentos":
            "📑 Analizador de documentos",

        "Portafolio INTILED":
            "📊 Portafolio INTILED",

        "Reuniones y avances":
            "📅 Reuniones y avances",

        "Estructuración":
            "🏗️ Estructuración",

        "Proyectos públicos / MGA":
            "🇨🇴 Proyectos públicos / MGA",

        "Investigación":
            "📚 Investigación",

        "Generador de propuestas":
            "📄 Generador de propuestas",

        "Biblioteca INTILED":
            "🏢 Biblioteca INTILED",

        "Seguimiento":
            "📊 Seguimiento"
    }

    destino = alias.get(
        opcion,
        opcion
    )

    funcion = rutas.get(
        destino
    )

    if funcion is None:

        st.warning(
            "Esta sección todavía no está disponible."
        )

        return

    try:

        funcion()

    except Exception as error:

        st.error(
            "Ocurrió un problema al cargar esta sección."
        )

        with st.expander(
            "Ver detalles técnicos"
        ):

            st.exception(
                error
            )


# ============================================================
# APLICACIÓN PRINCIPAL
# ============================================================

def ejecutar_aplicacion():

    opcion = mostrar_menu()

    mostrar_barra_superior()

    ejecutar_modulo(
        opcion
    )


# ============================================================
# EJECUCIÓN
# ============================================================

def main():

    if st.session_state.get(
        "ingreso",
        False
    ):

        ejecutar_aplicacion()

    else:

        mostrar_portada()


if __name__ == "__main__":

    main()
