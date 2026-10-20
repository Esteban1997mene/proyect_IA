import streamlit as st
from datetime import datetime


# ============================================================
# INTI PROJECTS AI
# ANALIZADOR DE DOCUMENTOS
# ============================================================


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def obtener_valor(
    oportunidad,
    campo,
    default="No informado"
):
    valor = oportunidad.get(campo)

    if valor is None or valor == "":
        return default

    return valor


def obtener_clave_oportunidad(
    oportunidad
):
    return str(
        oportunidad.get("referencia")
        or oportunidad.get("id_proceso")
        or oportunidad.get("titulo")
        or "oportunidad_intiled"
    )


def normalizar_url(url):

    if not url:
        return ""

    if isinstance(url, dict):

        url = (
            url.get("url")
            or url.get("href")
            or url.get("link")
            or ""
        )

    if not isinstance(url, str):

        try:
            url = str(url)

        except Exception:
            return ""

    url = url.strip()

    if not (
        url.startswith("http://")
        or url.startswith("https://")
    ):
        return ""

    return url


# ============================================================
# INICIALIZAR REGISTRO DOCUMENTAL
# ============================================================

def inicializar_analisis_documental(
    oportunidad
):

    clave = obtener_clave_oportunidad(
        oportunidad
    )

    if (
        "analisis_documentales"
        not in st.session_state
    ):

        st.session_state[
            "analisis_documentales"
        ] = {}

    registros = st.session_state[
        "analisis_documentales"
    ]

    if clave not in registros:

        registros[clave] = {

            "id":
                clave,

            "fecha_creacion":
                datetime.now().isoformat(),

            "ultima_actualizacion":
                datetime.now().isoformat(),

            "estado":
                "SIN ANALIZAR",

            "oportunidad":
                oportunidad,

            "documentos":
                [],

            "porcentaje_analisis":
                0,

            "resultado":
                {},

            "requisitos":
                [],

            "brechas":
                [],

            "fortalezas":
                [],

            "bid_score":
                None,

            "decision":
                None
        }

    registros[
        clave
    ][
        "oportunidad"
    ] = oportunidad

    return registros[
        clave
    ]


# ============================================================
# ENCABEZADO
# ============================================================

def mostrar_encabezado(
    oportunidad
):

    st.title(
        "📑 Analizador de Documentos"
    )

    st.caption(
        "Análisis de pliegos, TDR, estudios previos, "
        "anexos técnicos y documentos contractuales."
    )

    st.divider()

    st.markdown(
        "### Convocatoria seleccionada"
    )

    st.markdown(
        f"#### {obtener_valor(oportunidad, 'titulo')}"
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.write(
            "**Entidad**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "entidad"
            )
        )

    with col2:

        st.write(
            "**Referencia**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "referencia"
            )
        )

    with col3:

        st.write(
            "**Fuente**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "fuente"
            )
        )

    col4, col5, col6 = st.columns(
        3
    )

    with col4:

        st.write(
            "**Presupuesto**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "valor"
            )
        )

    with col5:

        st.write(
            "**Modalidad**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "modalidad"
            )
        )

    with col6:

        st.write(
            "**Fecha de cierre**"
        )

        st.write(
            obtener_valor(
                oportunidad,
                "fecha_cierre"
            )
        )


# ============================================================
# FUENTE OFICIAL
# ============================================================

def mostrar_fuente_oficial(
    oportunidad
):

    st.subheader(
        "🌐 Convocatoria oficial"
    )

    url = normalizar_url(
        oportunidad.get(
            "url",
            ""
        )
    )

    if url:

        st.write(
            "Puedes consultar la fuente original "
            "antes de cargar los documentos."
        )

        st.link_button(
            "🌐 Abrir convocatoria oficial",
            url,
            use_container_width=True
        )

    else:

        st.info(
            "La fuente detectada no proporcionó "
            "un enlace directo utilizable."
        )


# ============================================================
# TIPOS DE DOCUMENTOS
# ============================================================

def mostrar_tipos_documentos():

    st.subheader(
        "📚 Documentos recomendados"
    )

    st.write(
        "Para realizar un análisis completo, INTI "
        "puede trabajar con varios documentos "
        "de la misma convocatoria."
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.info(
            "### 📘 Documento principal\n\n"
            "• TDR\n"
            "• Pliego de condiciones\n"
            "• Solicitud de ofertas\n"
            "• Invitación"
        )

    with col2:

        st.info(
            "### 📐 Documentos técnicos\n\n"
            "• Anexos técnicos\n"
            "• Especificaciones\n"
            "• Diseños\n"
            "• Estudios previos"
        )

    with col3:

        st.info(
            "### 💰 Documentos económicos\n\n"
            "• Presupuesto\n"
            "• Formato económico\n"
            "• APU\n"
            "• Cronograma"
        )


# ============================================================
# CARGADOR
# ============================================================

def mostrar_cargador(
    oportunidad,
    analisis
):

    st.subheader(
        "📤 Cargar documentos"
    )

    st.write(
        "Carga los documentos oficiales asociados "
        "a esta convocatoria."
    )

    archivos = st.file_uploader(
        "Selecciona uno o varios documentos",
        type=[
            "pdf",
            "docx",
            "xlsx",
            "xls"
        ],
        accept_multiple_files=True,
        key=(
            f"documentos_"
            f"{obtener_clave_oportunidad(oportunidad)}"
        )
    )

    st.caption(
        "Formatos admitidos: PDF, DOCX, XLSX y XLS."
    )

    if not archivos:

        return

    st.write(
        f"**{len(archivos)} documento(s) seleccionado(s)**"
    )

    for archivo in archivos:

        st.write(
            f"📄 {archivo.name}"
        )

    if st.button(
        "💾 Asociar documentos a la convocatoria",
        type="primary",
        use_container_width=True,
        key=(
            f"asociar_docs_"
            f"{obtener_clave_oportunidad(oportunidad)}"
        )
    ):

        documentos_registrados = []

        for archivo in archivos:

            documento = {

                "nombre":
                    archivo.name,

                "tipo_mime":
                    archivo.type,

                "tamano":
                    archivo.size,

                "fecha_carga":
                    datetime.now().isoformat(),

                "estado":
                    "PENDIENTE_ANALISIS"
            }

            documentos_registrados.append(
                documento
            )

        analisis[
            "documentos"
        ] = documentos_registrados

        analisis[
            "estado"
        ] = "DOCUMENTOS CARGADOS"

        analisis[
            "ultima_actualizacion"
        ] = datetime.now().isoformat()

        st.success(
            "Documentos asociados correctamente "
            "a la convocatoria."
        )

        st.rerun()


# ============================================================
# DOCUMENTOS REGISTRADOS
# ============================================================

def mostrar_documentos_registrados(
    analisis
):

    documentos = analisis.get(
        "documentos",
        []
    )

    st.subheader(
        "📂 Documentos asociados"
    )

    if not documentos:

        st.info(
            "Todavía no existen documentos "
            "asociados a esta convocatoria."
        )

        return

    for indice, documento in enumerate(
        documentos,
        start=1
    ):

        with st.container(
            border=True
        ):

            col1, col2, col3 = st.columns(
                [3, 1, 1]
            )

            with col1:

                st.write(
                    f"**{indice}. "
                    f"{documento.get('nombre', 'Documento')}**"
                )

            with col2:

                tamano = documento.get(
                    "tamano",
                    0
                )

                if tamano:

                    mb = tamano / (
                        1024 * 1024
                    )

                    st.write(
                        f"{mb:.2f} MB"
                    )

            with col3:

                estado = documento.get(
                    "estado",
                    "PENDIENTE"
                )

                if estado == "ANALIZADO":

                    st.success(
                        "Analizado"
                    )

                else:

                    st.warning(
                        "Pendiente"
                    )


# ============================================================
# COBERTURA DOCUMENTAL
# ============================================================

def mostrar_cobertura_documental(
    analisis
):

    st.subheader(
        "📊 Cobertura documental"
    )

    documentos = analisis.get(
        "documentos",
        []
    )

    if not documentos:

        st.progress(
            0
        )

        st.write(
            "**0% — Sin documentos cargados**"
        )

        return

    # Por ahora solamente indicamos que existen documentos.
    # En el motor documental real este porcentaje dependerá
    # de los requisitos encontrados.

    porcentaje = analisis.get(
        "porcentaje_analisis",
        0
    )

    st.progress(
        porcentaje / 100
    )

    st.write(
        f"**{porcentaje}% analizado**"
    )

    controles = [
        (
            "Objeto contractual",
            False
        ),
        (
            "Presupuesto",
            False
        ),
        (
            "Plazo",
            False
        ),
        (
            "Experiencia",
            False
        ),
        (
            "Personal mínimo",
            False
        ),
        (
            "Requisitos financieros",
            False
        ),
        (
            "Especificaciones técnicas",
            False
        ),
        (
            "Factores de evaluación",
            False
        ),
        (
            "Garantías",
            False
        ),
        (
            "Causales de rechazo",
            False
        )
    ]

    columnas = st.columns(
        2
    )

    for indice, (
        nombre,
        encontrado
    ) in enumerate(
        controles
    ):

        with columnas[
            indice % 2
        ]:

            if encontrado:

                st.write(
                    f"✅ {nombre}"
                )

            else:

                st.write(
                    f"⚪ {nombre}"
                )


# ============================================================
# BOTÓN DE ANÁLISIS
# ============================================================

def mostrar_accion_analisis(
    oportunidad,
    analisis
):

    st.subheader(
        "🧠 Análisis INTI"
    )

    documentos = analisis.get(
        "documentos",
        []
    )

    if not documentos:

        st.warning(
            "Debes cargar al menos un documento "
            "antes de iniciar el análisis."
        )

        st.button(
            "🧠 Analizar documentos con INTI",
            disabled=True,
            use_container_width=True
        )

        return

    st.write(
        "INTI analizará los documentos cargados "
        "para identificar los requisitos relevantes "
        "de la convocatoria."
    )

    if st.button(
        "🧠 Analizar documentos con INTI",
        type="primary",
        use_container_width=True,
        key=(
            f"analizar_docs_"
            f"{obtener_clave_oportunidad(oportunidad)}"
        )
    ):

        # ====================================================
        # TODAVÍA NO ANALIZAMOS EL CONTENIDO REAL
        # ====================================================

        st.warning(
            "El motor de lectura documental todavía "
            "no está conectado. Los documentos ya están "
            "asociados correctamente a la convocatoria."
        )

        st.info(
            "El siguiente paso será conectar "
            "`services/document_analyzer.py` para "
            "extraer automáticamente el contenido."
        )


# ============================================================
# RESULTADOS
# ============================================================

def mostrar_resultados(
    analisis
):

    resultado = analisis.get(
        "resultado",
        {}
    )

    if not resultado:

        return

    st.subheader(
        "📋 Resultado del análisis"
    )

    campos = [
        (
            "Objeto",
            "objeto"
        ),
        (
            "Presupuesto",
            "presupuesto"
        ),
        (
            "Plazo",
            "plazo"
        ),
        (
            "Experiencia",
            "experiencia"
        ),
        (
            "Personal",
            "personal"
        ),
        (
            "Requisitos financieros",
            "financieros"
        ),
        (
            "Especificaciones técnicas",
            "especificaciones"
        ),
        (
            "Factores de evaluación",
            "factores_evaluacion"
        ),
        (
            "Garantías",
            "garantias"
        ),
        (
            "Causales de rechazo",
            "causales_rechazo"
        )
    ]

    for titulo, clave in campos:

        valor = resultado.get(
            clave
        )

        if valor:

            with st.expander(
                titulo
            ):

                st.write(
                    valor
                )


# ============================================================
# NAVEGACIÓN
# ============================================================

def mostrar_navegacion(
    oportunidad
):

    st.divider()

    st.subheader(
        "🚀 Continuar"
    )

    col1, col2 = st.columns(
        2
    )

    with col1:

        if st.button(
            "🧠 Volver al Análisis INTILED",
            use_container_width=True,
            key="volver_analisis_intiled"
        ):

            st.session_state[
                "oportunidad_seleccionada"
            ] = oportunidad

            st.session_state[
                "navegar_a"
            ] = "🧠 Análisis INTILED"

            st.rerun()

    with col2:

        if st.button(
            "🏗️ Ir a Estructuración",
            use_container_width=True,
            type="primary",
            key="ir_estructuracion_documentos"
        ):

            st.session_state[
                "oportunidad_seleccionada"
            ] = oportunidad

            st.session_state[
                "navegar_a"
            ] = "🏗️ Estructuración"

            st.rerun()


# ============================================================
# MÓDULO PRINCIPAL
# ============================================================

def mostrar_analizador():

    # ========================================================
    # VERIFICAR OPORTUNIDAD
    # ========================================================

    if (
        "oportunidad_seleccionada"
        not in st.session_state
    ):

        st.title(
            "📑 Analizador de Documentos"
        )

        st.caption(
            "Análisis de documentos contractuales "
            "y técnicos."
        )

        st.divider()

        st.info(
            "No existe una convocatoria seleccionada."
        )

        st.write(
            "Ve al **🔎 Radar de oportunidades**, "
            "selecciona un proceso y después utiliza "
            "**📑 Analizar pliegos / TDR**."
        )

        return

    # ========================================================
    # OPORTUNIDAD
    # ========================================================

    oportunidad = st.session_state[
        "oportunidad_seleccionada"
    ]

    # ========================================================
    # REGISTRO
    # ========================================================

    analisis = (
        inicializar_analisis_documental(
            oportunidad
        )
    )

    # ========================================================
    # INTERFAZ
    # ========================================================

    mostrar_encabezado(
        oportunidad
    )

    st.divider()

    mostrar_fuente_oficial(
        oportunidad
    )

    st.divider()

    mostrar_tipos_documentos()

    st.divider()

    mostrar_cargador(
        oportunidad,
        analisis
    )

    st.divider()

    mostrar_documentos_registrados(
        analisis
    )

    st.divider()

    mostrar_cobertura_documental(
        analisis
    )

    st.divider()

    mostrar_accion_analisis(
        oportunidad,
        analisis
    )

    mostrar_resultados(
        analisis
    )

    mostrar_navegacion(
        oportunidad
    )
