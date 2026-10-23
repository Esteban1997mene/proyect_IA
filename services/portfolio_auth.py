import streamlit as st
import hmac


# ============================================================
# INTI PROJECTS AI
# SEGURIDAD - PORTAFOLIO INTILED
# ============================================================


def verificar_credenciales(usuario, password):

    try:
        usuario_correcto = st.secrets[
            "portfolio"
        ][
            "username"
        ]

        password_correcto = st.secrets[
            "portfolio"
        ][
            "password"
        ]

    except Exception:
        return False

    usuario_valido = hmac.compare_digest(
        str(usuario),
        str(usuario_correcto)
    )

    password_valido = hmac.compare_digest(
        str(password),
        str(password_correcto)
    )

    return (
        usuario_valido
        and password_valido
    )


def esta_autenticado():

    return st.session_state.get(
        "portfolio_authenticated",
        False
    )


def cerrar_sesion():

    st.session_state[
        "portfolio_authenticated"
    ] = False

    st.session_state.pop(
        "portfolio_user",
        None
    )


def mostrar_login():

    st.markdown(
        "## 🔐 Portafolio INTILED"
    )

    st.caption(
        "Información interna y confidencial"
    )

    st.write("")

    col1, col2, col3 = st.columns(
        [1, 1.3, 1]
    )

    with col2:

        with st.container(
            border=True
        ):

            st.markdown(
                "### Acceso autorizado"
            )

            st.write(
                "Ingresa tus credenciales "
                "para consultar el portafolio."
            )

            usuario = st.text_input(
                "Usuario",
                key="portfolio_login_user"
            )

            password = st.text_input(
                "Contraseña",
                type="password",
                key="portfolio_login_password"
            )

            if st.button(
                "🔐 Ingresar",
                type="primary",
                use_container_width=True
            ):

                if verificar_credenciales(
                    usuario,
                    password
                ):

                    st.session_state[
                        "portfolio_authenticated"
                    ] = True

                    st.session_state[
                        "portfolio_user"
                    ] = usuario

                    st.rerun()

                else:

                    st.error(
                        "Usuario o contraseña incorrectos."
                    )

    return False
