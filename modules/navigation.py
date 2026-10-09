import streamlit as st


def mostrar_menu():

    with st.sidebar:

        st.markdown("## ⚡ INTI")
        st.caption("Projects AI")

        st.divider()

        opcion = st.radio(
            "Navegación",
            [
                "🏠 Dashboard",
                "🔎 Radar de oportunidades",
                "🎯 Oportunidades",
                "🧠 Analizador IA",
                "🏗️ Estructuración",
                "🇨🇴 Proyectos públicos / MGA",
                "📚 Investigación",
                "📄 Generador de propuestas",
                "🏢 Biblioteca INTILED",
                "📊 Seguimiento"
            ],
            label_visibility="collapsed"
        )

        st.divider()

        st.caption("INTILED SAS BIC")
        st.caption("INTI Projects AI")

    return opcion
