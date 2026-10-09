import streamlit as st

st.set_page_config(
    page_title="INTI Projects AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ocultar elementos predeterminados
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        .block-container {
            padding-top: 3rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Estado de ingreso
if "ingreso" not in st.session_state:
    st.session_state.ingreso = False


def pagina_ingreso():

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.image(
            "assets/logo_intiled.png",
            use_container_width=True
        )

        st.markdown(
            """
            <h1 style="
                text-align:center;
                font-size:48px;
                margin-bottom:0;
            ">
                INTI PROJECTS AI
            </h1>

            <p style="
                text-align:center;
                font-size:20px;
                color:#777;
            ">
                Inteligencia para transformar oportunidades
                en proyectos.
            </p>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        if st.button(
            "Ingresar a la plataforma",
            use_container_width=True,
            type="primary"
        ):
            st.session_state.ingreso = True
            st.rerun()

        st.markdown(
            """
            <p style="
                text-align:center;
                margin-top:40px;
                color:#888;
                font-size:13px;
            ">
                Plataforma interna de INTILED SAS BIC
            </p>
            """,
            unsafe_allow_html=True
        )


def dashboard():

    st.title("⚡ INTI Projects AI")

    st.write(
        "Bienvenido al sistema inteligente de "
        "identificación y estructuración de proyectos."
    )

    st.success(
        "La plataforma se encuentra funcionando correctamente."
    )

    if st.button("Cerrar"):
        st.session_state.ingreso = False
        st.rerun()


if st.session_state.ingreso:
    dashboard()
else:
    pagina_ingreso()
