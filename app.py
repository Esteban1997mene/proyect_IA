
import streamlit as st
from pathlib import Path

# ============================================================
# INTI PROJECTS AI
# APLICACIÓN PRINCIPAL
# INTILED SAS BIC
# ============================================================

st.set_page_config(
    page_title="INTI Projects | INTILED",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# MÓDULOS
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
# RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

# ============================================================
# ESTILOS
# ============================================================

def cargar_estilos():

    ruta_css = ASSETS_DIR / "styles.css"

    if ruta_css.exists():
        try:
            css = ruta_css.read_text(
                encoding="utf-8"
            )

            st.markdown(
                f"<style>{css}</style>",
                unsafe_allow_html=True
            )

        except Exception:
            st.warning(
                "No fue posible cargar los estilos."
            )


cargar_estilos()

# ============================================================
# ESTADO INICIAL
# ============================================================

if "ingreso" not in st.session_state:
    st.session_state["ingreso"] = False

if "oportunidad_seleccionada" not in st.session_state:
    st.session_state["oportunidad_seleccionada"] = None

# ============================================================
# PORTADA
# ============================================================

def mostrar_portada():

    st.markdown(
        """
        <style>

        section[data-testid="stSidebar"] {
            display: none;
        }

        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background: #111821 !important;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 1050px;
            padding-top: 5vh;
        }

        .st-key-inti_portada_panel {
            position: relative;
            overflow: hidden;

            background: linear-gradient(
                125deg,
                #202630,
                #303A48
            );

            border: 1px solid #3D4856;
            border-radius: 24px;

            padding: 35px 45px 40px;

            box-shadow:
                0 20px 60px rgba(0,0,0,.25);

            animation: intiEntrada 1s ease-out;
        }

        .st-key-inti_portada_panel::before {
            content: "";

            position: absolute;

            width: 390px;
            height: 390px;

            right: -140px;
            top: -150px;

            border-radius: 50%;
            border: 1px solid rgba(244,119,33,.25);

            box-shadow:
                0 0 0 45px rgba(244,119,33,.035),
                0 0 0 100px rgba(244,119,33,.025);

            animation: intiPulso 7s ease-in-out infinite;
            pointer-events: none;
        }

        .st-key-inti_portada_panel::after {
            content: "";

            position: absolute;

            height: 2px;
            width: 80%;

            left: -50%;
            bottom: 70px;

            background: linear-gradient(
                90deg,
                transparent,
                #F47721,
                transparent
            );

            transform: rotate(-15deg);
            animation: intiLinea 7s linear infinite;
            pointer-events: none;
        }

        .inti-portada-etiqueta {
            color: #FFAD72;
            font-size: 13px;
            font-weight: 750;
            letter-spacing: 2px;
            text-align: center;
            margin-top: 10px;
        }

        .inti-portada-titulo {
            color: #FFFFFF;
            font-size: clamp(40px, 5vw, 66px);
            font-weight: 800;
            text-align: center;
            letter-spacing: -1.5px;
            margin: 15px 0;
        }

        .inti-portada-titulo span {
            color: #F47721;
        }

        .inti-portada-subtitulo {
            color: #CBD3DE;
            font-size: 19px;
            line-height: 1.8;
            text-align: center;
            max-width: 750px;
            margin: 10px auto 25px;
        }

        .inti-portada-linea {
            width: 65%;
            height: 4px;
            border-radius: 10px;

            margin: 25px auto;

            background: linear-gradient(
                90deg,
                #F47721,
                #FFB16C,
                #F47721
            );

            background-size: 200% 100%;
            animation: intiEnergia 4s linear infinite;
        }

        @keyframes intiEntrada {
            from {
                opacity: 0;
                transform: translateY(18px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes intiPulso {
            0%, 100% {
                transform: scale(1);
                opacity: .6;
            }

            50% {
                transform: scale(1.12);
                opacity: 1;
            }
        }

        @keyframes intiLinea {
            from {
                left: -70%;
            }

            to {
                left: 110%;
            }
        }

        @keyframes intiEnergia {
            from {
                background-position: 200% 0;
            }

            to {
                background-position: -200% 0;
            }
        }

        @media (max-width: 768px) {
            .st-key-inti_portada_panel {
                padding: 25px 18px;
            }

            .inti-portada-subtitulo {
                font-size: 16px;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            .st-key-inti_portada_panel,
            .st-key-inti_portada_panel::before,
            .st-key-inti_portada_panel::after,
            .inti-portada-linea {
                animation: none;
            }
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    with st.container(key="inti_portada_panel"):

        st.write("")

        ruta_logo = ASSETS_DIR / "logo_intiled.png"

        if ruta_logo.exists():

            col1, col2, col3 = st.columns(
                [1.3, 1, 1.3]
            )

            with col2:
                st.image(
                    str(ruta_logo),
                    use_container_width=True
                )

        st.markdown(
            """
            <div class="inti-portada-etiqueta">
                PLATAFORMA CORPORATIVA
            </div>

            <div class="inti-portada-titulo">
                INTI <span>PROJECTS</span>
            </div>

            <div class="inti-portada-subtitulo">
                Inteligencia para identificar oportunidades,
                analizar convocatorias, estructurar proyectos
                y desarrollar propuestas estratégicas.
            </div>

            <div class="inti-portada-linea"></div>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(
            [1, 1.4, 1]
        )

        with col2:

            if st.button(
                "INGRESAR A LA PLATAFORMA",
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
                color:#CBD3DE;
                font-size:14px;
                margin-top:24px;
            ">
                INTILED SAS BIC
                · Innovación · Energía · Tecnología
            </p>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# VOLVER A PORTADA
# ============================================================

def mostrar_opcion_salida():

    with st.sidebar:

        st.divider()

        if st.button(
            "Volver a la portada",
            use_container_width=True,
            key="inti_volver_portada"
        ):

            st.session_state["ingreso"] = False
            st.rerun()


# ============================================================
# RUTAS DE MÓDULOS
# ============================================================

def ejecutar_modulo(opcion):

    rutas = {
        "🏠 Dashboard": mostrar_dashboard,
        "🔎 Radar de oportunidades": mostrar_radar,
        "🎯 Oportunidades": mostrar_oportunidades,
        "🧠 Análisis INTILED": mostrar_analisis_intiled,
        "📑 Analizador de documentos": mostrar_analizador,
        "📊 Portafolio INTILED": mostrar_portafolio,
        "🏗️ Estructuración": mostrar_estructuracion,
        "🇨🇴 Proyectos públicos / MGA": mostrar_mga,
        "📚 Investigación": mostrar_investigacion,
        "📄 Generador de propuestas": mostrar_propuestas,
        "🏢 Biblioteca INTILED": mostrar_biblioteca,
        "📊 Seguimiento": mostrar_seguimiento,
    }

    try:
        from modules.meetings import mostrar_reuniones
        rutas["📅 Reuniones y avances"] = mostrar_reuniones
    except ImportError:
        pass

    funcion = rutas.get(opcion)

    if funcion is None:
        st.warning(
            "Esta sección todavía no está disponible."
        )
        return

    funcion()


# ============================================================
# APLICACIÓN PRINCIPAL
# ============================================================

def ejecutar_aplicacion():

    opcion = mostrar_menu()

    mostrar_opcion_salida()

    ejecutar_modulo(opcion)


def main():

    if st.session_state.get("ingreso", False):
        ejecutar_aplicacion()
    else:
        mostrar_portada()


if __name__ == "__main__":
    main()
