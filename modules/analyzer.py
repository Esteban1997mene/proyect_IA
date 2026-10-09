import streamlit as st


def mostrar_analizador():

    st.title("🧠 Analizador IA")

    st.write(
        "Carga una convocatoria, TDR, pliego "
        "o documento para realizar su análisis."
    )

    st.file_uploader(
        "Cargar documento",
        type=["pdf", "docx"]
    )
