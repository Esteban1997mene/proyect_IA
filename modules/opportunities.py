import streamlit as st


def mostrar_oportunidades():

    st.title("🎯 Oportunidades seleccionadas")

    st.caption(
        "Oportunidades identificadas por INTI "
        "para evaluación y estructuración."
    )

    st.divider()

    if "oportunidad_seleccionada" not in st.session_state:

        st.info(
            "Todavía no se ha seleccionado "
            "ninguna oportunidad."
        )

        st.write(
            "Utiliza el **Radar de oportunidades** "
            "para identificar convocatorias."
        )

        return

    oportunidad = st.session_state[
        "oportunidad_seleccionada"
    ]

    with st.container(border=True):

        st.subheader(
            oportunidad["proyecto"]
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.write(
                f"**País**  \n{oportunidad['pais']}"
            )

            st.write(
                f"**Entidad**  \n{oportunidad['entidad']}"
            )

        with col2:

            st.write(
                f"**Financiación**  \n{oportunidad['tipo']}"
            )

            st.write(
                f"**Presupuesto**  \n{oportunidad['presupuesto']}"
            )

        with col3:

            st.metric(
                "INTILED Score",
                f"{oportunidad['score']}/100"
            )

            st.write(
                f"**Cierre:** {oportunidad['cierre']}"
            )

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "🧠 Análisis detallado",
            use_container_width=True
        ):

            st.session_state[
                "solicitar_analisis"
            ] = True

            st.success(
                "Oportunidad enviada "
                "al Analizador IA."
            )

    with col2:

        if st.button(
            "🏗️ Iniciar estructuración",
            use_container_width=True
        ):

            st.session_state[
                "iniciar_estructuracion"
            ] = True

            st.success(
                "Proyecto enviado al módulo "
                "de estructuración."
            )

    with col3:

        if st.button(
            "🗑️ Descartar",
            use_container_width=True
        ):

            del st.session_state[
                "oportunidad_seleccionada"
            ]

            st.rerun()
