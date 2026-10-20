import streamlit as st
from datetime import datetime

from services.document_analyzer import analizar_documentos


# ============================================================
# INTI PROJECTS AI
# ANALIZADOR DOCUMENTAL
# ============================================================
#
# FLUJO:
#
# Convocatoria seleccionada
#       ↓
# Fuente oficial
#       ↓
# Carga de TDR / pliegos / anexos
#       ↓
# Motor document_analyzer.py
#       ↓
# Extracción de requisitos
#       ↓
# Cobertura documental
#       ↓
# Resultado consolidado
#       ↓
# Análisis INTILED / Estructuración
#
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
        or oportunidad.get("id")
        or oportunidad.get("titulo")
        or "oportunidad_intiled"
    )


def normalizar_url(url):

    if not url:
        return ""

    # Algunos resultados pueden traer
    # la URL dentro de un diccionario.
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


def obtener_url_oportunidad(
    oportunidad
):

    posibles_campos = [
        "url",
        "URL",
        "link",
        "enlace",
        "url_proceso",
        "urlproceso",
        "urlProceso"
    ]

    for campo in posibles_campos:

        url = normalizar_url(
            oportunidad.get(campo)
        )

        if url:
            return url

    return ""


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
                "SIN DOCUMENTOS",

            "oportunidad":
                oportunidad,

            # Metadata de los documentos
            "documentos":
                [],

            # Resultados del motor documental
            "resultado":
                {},

            "cobertura":
                {},

            "porcentaje_analisis":
                0,

            "errores":
                [],

            # Posteriormente se llenarán
            # con requirements_engine.py
            "requisitos":
                [],

            "fortalezas":
                [],

            "brechas":
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
        "Lectura y análisis de TDR, pliegos, "
        "estudios previos, anexos técnicos, "
        "presupuestos y demás documentos "
        "de la convocatoria."
    )

    st.divider()

    st.markdown(
        "### 🎯 Convocatoria seleccionada"
    )

    titulo = obtener_valor(
        oportunidad,
        "titulo",
        "Oportunidad sin título"
    )

    st.markdown(
        f"#### {titulo}"
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
        "🌐 Fuente oficial"
    )

    url = obtener_url_oportunidad(
        oportunidad
    )

    if url:

        st.write(
            "Consulta la convocatoria directamente "
            "en la fuente donde fue detectada."
        )

        st.link_button(
            "🌐 Abrir convocatoria oficial",
            url,
            use_container_width=True
        )

    else:

        st.info(
            "Esta oportunidad no contiene todavía "
            "un enlace directo utilizable hacia "
            "la convocatoria oficial."
        )


# ============================================================
# GUÍA DOCUMENTAL
# ============================================================

def mostrar_guia_documental():

    st.subheader(
        "📚 Documentación del proceso"
    )

    st.write(
        "Puedes cargar varios documentos de la misma "
        "convocatoria. INTI los analizará como un "
        "expediente documental conjunto."
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.info(
            "### 📘 Principal\n\n"
            "• TDR\n"
            "• Pliego de condiciones\n"
            "• Solicitud de ofertas\n"
            "• Invitación"
        )

    with col2:

        st.info(
            "### 📐 Técnico\n\n"
            "• Estudios previos\n"
            "• Anexos técnicos\n"
            "• Especificaciones\n"
            "• Fichas técnicas"
        )

    with col3:

        st.info(
            "### 💰 Complementario\n\n"
            "• Presupuesto\n"
            "• Cronograma\n"
            "• Formularios\n"
            "• Adendas"
        )


# ============================================================
# CARGADOR DE DOCUMENTOS
# ============================================================

def mostrar_cargador(
    oportunidad,
    analisis
):

    st.subheader(
        "📤 Cargar documentos"
    )

    st.write(
        "Selecciona los documentos oficiales "
        "que deseas analizar."
    )

    clave = obtener_clave_oportunidad(
        oportunidad
    )

    archivos = st.file_uploader(
        "TDR, pliegos, anexos y documentos complementarios",
        type=[
            "pdf",
            "docx",
            "xlsx"
        ],
        accept_multiple_files=True,
        key=f"uploader_documentos_{clave}"
    )

    st.caption(
        "Formatos soportados actualmente: "
        "PDF, DOCX y XLSX."
    )

    # Guardamos los objetos UploadedFile
    # temporalmente en session_state.
    #
    # NO los almacenamos dentro del registro
    # documental definitivo.
    if archivos:

        st.session_state[
            f"archivos_temporales_{clave}"
        ] = archivos

        st.success(
            f"📎 {len(archivos)} documento(s) "
            "seleccionado(s)."
        )

        for indice, archivo in enumerate(
            archivos,
            start=1
        ):

            col1, col2 = st.columns(
                [4, 1]
            )

            with col1:

                st.write(
                    f"📄 {indice}. {archivo.name}"
                )

            with col2:

                mb = archivo.size / (
                    1024 * 1024
                )

                st.caption(
                    f"{mb:.2f} MB"
                )

        if st.button(
            "💾 Asociar documentos a la convocatoria",
            type="primary",
            use_container_width=True,
            key=f"asociar_documentos_{clave}"
        ):

            documentos = []

            for archivo in archivos:

                documentos.append({

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
                })

            analisis[
                "documentos"
            ] = documentos

            analisis[
                "estado"
            ] = "DOCUMENTOS CARGADOS"

            analisis[
                "ultima_actualizacion"
            ] = datetime.now().isoformat()

            # Si asociamos nuevos documentos,
            # invalidamos el análisis anterior.
            analisis[
                "resultado"
            ] = {}

            analisis[
                "cobertura"
            ] = {}

            analisis[
                "porcentaje_analisis"
            ] = 0

            analisis[
                "errores"
            ] = []

            analisis[
                "bid_score"
            ] = None

            analisis[
                "decision"
            ] = None

            st.success(
                "✅ Documentos asociados "
                "correctamente."
            )

            st.rerun()

    else:

        archivos_guardados = (
            st.session_state.get(
                f"archivos_temporales_{clave}",
                []
            )
        )

        if archivos_guardados:

            st.caption(
                "INTI mantiene temporalmente los "
                "archivos seleccionados durante "
                "esta sesión."
            )

    return archivos


# ============================================================
# DOCUMENTOS ASOCIADOS
# ============================================================

def mostrar_documentos_asociados(
    analisis
):

    st.subheader(
        "📂 Documentos asociados"
    )

    documentos = analisis.get(
        "documentos",
        []
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
                [4, 1, 1]
            )

            with col1:

                st.write(
                    f"**📄 {indice}. "
                    f"{documento.get('nombre', 'Documento')}**"
                )

                categoria = documento.get(
                    "categoria"
                )

                if categoria:

                    st.caption(
                        f"Clasificación INTI: {categoria}"
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

                else:

                    st.write(
                        "—"
                    )

            with col3:

                estado = documento.get(
                    "estado",
                    "PENDIENTE_ANALISIS"
                )

                if estado == "ANALIZADO":

                    st.success(
                        "Analizado"
                    )

                elif estado == "ERROR":

                    st.error(
                        "Error"
                    )

                else:

                    st.warning(
                        "Pendiente"
                    )


# ============================================================
# PREPARAR ARCHIVOS PARA EL MOTOR
# ============================================================

def preparar_archivos_para_analisis(
    oportunidad
):

    clave = obtener_clave_oportunidad(
        oportunidad
    )

    archivos = st.session_state.get(
        f"archivos_temporales_{clave}",
        []
    )

    documentos_motor = []

    for archivo in archivos:

        try:

            bytes_archivo = (
                archivo.getvalue()
            )

            documentos_motor.append({

                "nombre":
                    archivo.name,

                "tipo_mime":
                    archivo.type,

                "tamano":
                    archivo.size,

                # Los bytes solamente se usan
                # durante el análisis.
                "bytes":
                    bytes_archivo
            })

        except Exception:

            continue

    return documentos_motor


# ============================================================
# EJECUTAR ANÁLISIS
# ============================================================

def mostrar_accion_analisis(
    oportunidad,
    analisis
):

    st.subheader(
        "🧠 Análisis documental INTI"
    )

    documentos = analisis.get(
        "documentos",
        []
    )

    if not documentos:

        st.warning(
            "Primero debes cargar y asociar "
            "al menos un documento."
        )

        st.button(
            "🧠 Analizar documentos con INTI",
            disabled=True,
            use_container_width=True,
            key="analizar_documentos_deshabilitado"
        )

        return

    documentos_motor = (
        preparar_archivos_para_analisis(
            oportunidad
        )
    )

    if not documentos_motor:

        st.warning(
            "Los documentos están registrados, "
            "pero INTI ya no tiene acceso temporal "
            "a los archivos originales."
        )

        st.write(
            "Vuelve a seleccionar los archivos "
            "en el cargador antes de ejecutar "
            "el análisis."
        )

        return

    st.write(
        "INTI leerá los documentos y localizará "
        "información contractual, técnica, económica "
        "y habilitante."
    )

    st.caption(
        "En esta etapa INTI extrae evidencia textual. "
        "Todavía no determina automáticamente que "
        "INTILED cumpla un requisito."
    )

    clave = obtener_clave_oportunidad(
        oportunidad
    )

    if st.button(
        "🧠 Analizar documentos con INTI",
        type="primary",
        use_container_width=True,
        key=f"analizar_documentos_{clave}"
    ):

        with st.spinner(
            "INTI está leyendo y analizando "
            "los documentos..."
        ):

            try:

                resultado_motor = (
                    analizar_documentos(
                        documentos_motor
                    )
                )

                # ============================================
                # RESULTADOS
                # ============================================

                analisis[
                    "resultado"
                ] = resultado_motor.get(
                    "resultado",
                    {}
                )

                analisis[
                    "cobertura"
                ] = resultado_motor.get(
                    "cobertura",
                    {}
                )

                analisis[
                    "porcentaje_analisis"
                ] = resultado_motor.get(
                    "porcentaje_analisis",
                    0
                )

                analisis[
                    "errores"
                ] = resultado_motor.get(
                    "errores",
                    []
                )

                analisis[
                    "estado"
                ] = "ANALIZADO"

                analisis[
                    "ultima_actualizacion"
                ] = datetime.now().isoformat()

                # ============================================
                # ACTUALIZAR METADATA DE DOCUMENTOS
                # ============================================

                documentos_analizados = (
                    resultado_motor.get(
                        "documentos",
                        []
                    )
                )

                metadata_actualizada = []

                for documento in documentos_analizados:

                    metadata_actualizada.append({

                        "nombre":
                            documento.get(
                                "nombre",
                                ""
                            ),

                        "tipo_mime":
                            documento.get(
                                "tipo_mime",
                                ""
                            ),

                        "tamano":
                            documento.get(
                                "tamano",
                                0
                            ),

                        "categoria":
                            documento.get(
                                "categoria",
                                "OTRO"
                            ),

                        "caracteres":
                            documento.get(
                                "caracteres",
                                0
                            ),

                        "fecha_analisis":
                            documento.get(
                                "fecha_analisis",
                                datetime.now().isoformat()
                            ),

                        "estado":
                            "ANALIZADO"
                    })

                # Si un archivo produjo error,
                # también lo mostramos.
                nombres_analizados = {
                    documento.get("nombre")
                    for documento
                    in metadata_actualizada
                }

                for documento_original in documentos:

                    nombre = documento_original.get(
                        "nombre"
                    )

                    if (
                        nombre
                        not in nombres_analizados
                    ):

                        metadata_actualizada.append({

                            **documento_original,

                            "estado":
                                "ERROR"
                        })

                analisis[
                    "documentos"
                ] = metadata_actualizada

                st.success(
                    "✅ INTI completó el análisis "
                    "documental."
                )

                st.rerun()

            except Exception as error:

                st.error(
                    "❌ No fue posible completar "
                    "el análisis documental."
                )

                st.exception(
                    error
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

    porcentaje = analisis.get(
        "porcentaje_analisis",
        0
    )

    porcentaje = max(
        0,
        min(
            porcentaje,
            100
        )
    )

    st.progress(
        porcentaje / 100
    )

    st.write(
        f"**{porcentaje}% de los campos "
        "contractuales principales fueron localizados.**"
    )

    cobertura = analisis.get(
        "cobertura",
        {}
    )

    controles = [
        (
            "Objeto contractual",
            cobertura.get(
                "objeto",
                False
            )
        ),
        (
            "Presupuesto",
            cobertura.get(
                "presupuesto",
                False
            )
        ),
        (
            "Plazo",
            cobertura.get(
                "plazo",
                False
            )
        ),
        (
            "Experiencia",
            cobertura.get(
                "experiencia",
                False
            )
        ),
        (
            "Personal mínimo",
            cobertura.get(
                "personal",
                False
            )
        ),
        (
            "Requisitos financieros",
            cobertura.get(
                "financieros",
                False
            )
        ),
        (
            "Especificaciones técnicas",
            cobertura.get(
                "especificaciones",
                False
            )
        ),
        (
            "Factores de evaluación",
            cobertura.get(
                "factores_evaluacion",
                False
            )
        ),
        (
            "Garantías",
            cobertura.get(
                "garantias",
                False
            )
        ),
        (
            "Causales de rechazo",
            cobertura.get(
                "causales_rechazo",
                False
            )
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

    if porcentaje < 100:

        st.info(
            "⚪ Un campo no localizado no significa "
            "necesariamente que no exista. Puede estar "
            "en otro anexo, formulario o documento "
            "que todavía no haya sido cargado."
        )


# ============================================================
# ERRORES DOCUMENTALES
# ============================================================

def mostrar_errores(
    analisis
):

    errores = analisis.get(
        "errores",
        []
    )

    if not errores:
        return

    st.subheader(
        "⚠️ Incidencias de lectura"
    )

    for error in errores:

        documento = error.get(
            "documento",
            "Documento"
        )

        mensaje = error.get(
            "error",
            "Error desconocido"
        )

        st.error(
            f"**{documento}**\n\n"
            f"{mensaje}"
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
        "📋 Información localizada"
    )

    st.caption(
        "Los siguientes contenidos corresponden "
        "a fragmentos encontrados en los documentos. "
        "Todavía deben interpretarse y convertirse "
        "en requisitos estructurados."
    )

    campos = [
        (
            "📌 Objeto contractual",
            "objeto"
        ),
        (
            "💰 Presupuesto",
            "presupuesto"
        ),
        (
            "⏱️ Plazo",
            "plazo"
        ),
        (
            "🏢 Experiencia requerida",
            "experiencia"
        ),
        (
            "👷 Personal mínimo / personal clave",
            "personal"
        ),
        (
            "💵 Capacidad financiera",
            "financieros"
        ),
        (
            "⚡ Especificaciones técnicas",
            "especificaciones"
        ),
        (
            "🏆 Factores de evaluación y puntaje",
            "factores_evaluacion"
        ),
        (
            "🛡️ Garantías",
            "garantias"
        ),
        (
            "❌ Causales de rechazo",
            "causales_rechazo"
        ),
        (
            "📦 Entregables",
            "entregables"
        ),
        (
            "💳 Forma de pago",
            "forma_pago"
        )
    ]

    for titulo, clave in campos:

        contenido = resultado.get(
            clave,
            ""
        )

        encontrado = bool(
            contenido
            and str(
                contenido
            ).strip()
        )

        if encontrado:

            with st.expander(
                f"✅ {titulo}",
                expanded=False
            ):

                st.text_area(
                    "Evidencia localizada",
                    value=contenido,
                    height=320,
                    disabled=True,
                    key=(
                        f"resultado_{clave}_"
                        f"{analisis.get('id')}"
                    )
                )

        else:

            with st.expander(
                f"⚪ {titulo}",
                expanded=False
            ):

                st.info(
                    "INTI no localizó información "
                    "suficiente sobre este campo "
                    "en los documentos analizados."
                )


# ============================================================
# ESTADO DEL ANÁLISIS
# ============================================================

def mostrar_estado(
    analisis
):

    st.subheader(
        "🔎 Estado del expediente"
    )

    estado = analisis.get(
        "estado",
        "SIN DOCUMENTOS"
    )

    documentos = analisis.get(
        "documentos",
        []
    )

    porcentaje = analisis.get(
        "porcentaje_analisis",
        0
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.metric(
            "Estado",
            estado
        )

    with col2:

        st.metric(
            "Documentos",
            len(documentos)
        )

    with col3:

        st.metric(
            "Cobertura",
            f"{porcentaje}%"
        )


# ============================================================
# NAVEGACIÓN
# ============================================================

def mostrar_navegacion(
    oportunidad,
    analisis
):

    st.divider()

    st.subheader(
        "🚀 Siguiente paso"
    )

    analizado = (
        analisis.get(
            "estado"
        )
        == "ANALIZADO"
    )

    if analizado:

        st.success(
            "El expediente ya tiene un primer "
            "análisis documental. Podemos continuar "
            "con el análisis estratégico y la "
            "estructuración."
        )

    else:

        st.info(
            "Se recomienda completar el análisis "
            "documental antes de estructurar "
            "la propuesta definitiva."
        )

    col1, col2, col3 = st.columns(
        3
    )

    # ========================================================
    # ANÁLISIS INTILED
    # ========================================================

    with col1:

        if st.button(
            "🧠 Análisis INTILED",
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

    # ========================================================
    # ESTRUCTURACIÓN
    # ========================================================

    with col2:

        if st.button(
            "🏗️ Ir a Estructuración",
            use_container_width=True,
            type="primary",
            key="ir_estructuracion_desde_analizador"
        ):

            st.session_state[
                "oportunidad_seleccionada"
            ] = oportunidad

            st.session_state[
                "iniciar_estructuracion"
            ] = True

            st.session_state[
                "navegar_a"
            ] = "🏗️ Estructuración"

            st.rerun()

    # ========================================================
    # OPORTUNIDADES
    # ========================================================

    with col3:

        if st.button(
            "🎯 Volver a oportunidades",
            use_container_width=True,
            key="volver_oportunidades_analizador"
        ):

            st.session_state[
                "navegar_a"
            ] = "🎯 Oportunidades"

            st.rerun()


# ============================================================
# MÓDULO PRINCIPAL
# ============================================================

def mostrar_analizador():

    # ========================================================
    # SIN OPORTUNIDAD
    # ========================================================

    if (
        "oportunidad_seleccionada"
        not in st.session_state
    ):

        st.title(
            "📑 Analizador de Documentos"
        )

        st.caption(
            "Lectura y análisis documental "
            "de convocatorias."
        )

        st.divider()

        st.info(
            "No existe una convocatoria seleccionada."
        )

        st.write(
            "Ve al **🔎 Radar de oportunidades**, "
            "selecciona una convocatoria y utiliza "
            "**📑 Analizar pliegos / TDR**."
        )

        return

    # ========================================================
    # RECUPERAR OPORTUNIDAD
    # ========================================================

    oportunidad = st.session_state[
        "oportunidad_seleccionada"
    ]

    # ========================================================
    # INICIALIZAR EXPEDIENTE
    # ========================================================

    analisis = (
        inicializar_analisis_documental(
            oportunidad
        )
    )

    # ========================================================
    # ENCABEZADO
    # ========================================================

    mostrar_encabezado(
        oportunidad
    )

    st.divider()

    # ========================================================
    # ESTADO
    # ========================================================

    mostrar_estado(
        analisis
    )

    st.divider()

    # ========================================================
    # FUENTE OFICIAL
    # ========================================================

    mostrar_fuente_oficial(
        oportunidad
    )

    st.divider()

    # ========================================================
    # GUÍA
    # ========================================================

    mostrar_guia_documental()

    st.divider()

    # ========================================================
    # CARGA
    # ========================================================

    mostrar_cargador(
        oportunidad,
        analisis
    )

    st.divider()

    # ========================================================
    # DOCUMENTOS ASOCIADOS
    # ========================================================

    mostrar_documentos_asociados(
        analisis
    )

    st.divider()

    # ========================================================
    # ANALIZAR
    # ========================================================

    mostrar_accion_analisis(
        oportunidad,
        analisis
    )

    # ========================================================
    # RESULTADOS SOLO DESPUÉS DEL ANÁLISIS
    # ========================================================

    if (
        analisis.get(
            "estado"
        )
        == "ANALIZADO"
    ):

        st.divider()

        mostrar_cobertura_documental(
            analisis
        )

        mostrar_errores(
            analisis
        )

        st.divider()

        mostrar_resultados(
            analisis
        )

    # ========================================================
    # NAVEGACIÓN
    # ========================================================

    mostrar_navegacion(
        oportunidad,
        analisis
    )
