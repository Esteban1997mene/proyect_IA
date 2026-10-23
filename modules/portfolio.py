import streamlit as st
from datetime import datetime

# ============================================================
# INTI PROJECTS AI
# PORTAFOLIO INTILED
# INTILED SAS BIC
# ============================================================

from services.portfolio_auth import (
    esta_autenticado,
    mostrar_login,
    cerrar_sesion
)

from services.portfolio_engine import (
    ESTADOS_PROYECTO,
    PRIORIDADES,
    TIPOS_PROYECTO,
    calcular_metricas,
    formatear_moneda,
    obtener_proyectos_criticos,
    obtener_acciones_pendientes,
    registrar_cambio
)

from services.excel_importer import (
    procesar_excel_proyectos
)


# ============================================================
# INICIALIZACIÓN
# ============================================================

def inicializar_portafolio():

    if "portfolio_projects" not in st.session_state:
        st.session_state["portfolio_projects"] = []

    return st.session_state["portfolio_projects"]


def inicializar_papelera():

    if "portfolio_trash" not in st.session_state:
        st.session_state["portfolio_trash"] = []

    return st.session_state["portfolio_trash"]


# ============================================================
# ENCABEZADO
# ============================================================

def mostrar_encabezado():

    col1, col2 = st.columns([5, 1])

    with col1:

        st.title("📊 Portafolio INTILED")

        st.caption(
            "Centro ejecutivo de seguimiento de proyectos, "
            "iniciativas y oportunidades de INTILED SAS BIC."
        )

    with col2:

        usuario = st.session_state.get(
            "portfolio_user",
            "Usuario"
        )

        st.caption(
            f"👤 {usuario}"
        )

        if st.button(
            "🔒 Cerrar sesión",
            use_container_width=True,
            key="cerrar_sesion_portafolio"
        ):

            cerrar_sesion()
            st.rerun()


# ============================================================
# MÉTRICAS
# ============================================================

def mostrar_metricas(proyectos):

    metricas = calcular_metricas(
        proyectos
    )

    st.subheader(
        "📌 Resumen ejecutivo"
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "Proyectos",
            metricas.get("total", 0)
        )

    with col2:

        st.metric(
            "Valor estimado",
            formatear_moneda(
                metricas.get(
                    "valor_total",
                    0
                )
            )
        )

    with col3:

        st.metric(
            "Pipeline ponderado",
            formatear_moneda(
                metricas.get(
                    "valor_ponderado",
                    0
                )
            )
        )

    with col4:

        st.metric(
            "Prioridad P1",
            metricas.get(
                "prioridad_1",
                0
            )
        )

    with col5:

        st.metric(
            "Bloqueados",
            metricas.get(
                "bloqueados",
                0
            )
        )


# ============================================================
# RESUMEN DE ESTADOS
# ============================================================

def mostrar_resumen_estados(proyectos):

    if not proyectos:
        return

    conteo = {}

    for proyecto in proyectos:

        estado = proyecto.get(
            "estado",
            "Sin estado"
        )

        conteo[estado] = (
            conteo.get(
                estado,
                0
            )
            + 1
        )

    st.markdown(
        "### 🚦 Estado general"
    )

    estados = sorted(
        conteo.items(),
        key=lambda x: x[1],
        reverse=True
    )

    cantidad = min(
        len(estados),
        5
    )

    if cantidad == 0:
        return

    columnas = st.columns(
        cantidad
    )

    for indice, (
        estado,
        numero
    ) in enumerate(
        estados[:5]
    ):

        with columnas[indice]:

            st.metric(
                estado,
                numero
            )


# ============================================================
# FILTROS
# ============================================================

def aplicar_filtros(proyectos):

    st.subheader(
        "🔎 Buscar proyectos"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        busqueda = st.text_input(
            "Buscar",
            placeholder=(
                "Proyecto, entidad, municipio, responsable..."
            ),
            key="portfolio_busqueda"
        )

    with col2:

        estado = st.selectbox(
            "Estado",
            ["Todos"] + ESTADOS_PROYECTO,
            key="portfolio_filtro_estado"
        )

    with col3:

        prioridad = st.selectbox(
            "Prioridad",
            ["Todas"] + PRIORIDADES,
            key="portfolio_filtro_prioridad"
        )

    resultado = proyectos

    if busqueda:

        texto = busqueda.lower().strip()

        resultado = [
            proyecto
            for proyecto in resultado
            if texto in (
                str(proyecto.get("nombre", ""))
                + " "
                + str(proyecto.get("entidad", ""))
                + " "
                + str(proyecto.get("municipio", ""))
                + " "
                + str(proyecto.get("responsable", ""))
            ).lower()
        ]

    if estado != "Todos":

        resultado = [
            proyecto
            for proyecto in resultado
            if proyecto.get("estado") == estado
        ]

    if prioridad != "Todas":

        resultado = [
            proyecto
            for proyecto in resultado
            if proyecto.get("prioridad") == prioridad
        ]

    return resultado


# ============================================================
# TABLA
# ============================================================

def mostrar_tabla(proyectos):

    st.subheader(
        "📋 Proyectos"
    )

    if not proyectos:

        st.info(
            "No existen proyectos para mostrar."
        )

        return

    datos = []

    for proyecto in proyectos:

        datos.append({

            "Proyecto":
                proyecto.get(
                    "nombre",
                    ""
                ),

            "Entidad":
                proyecto.get(
                    "entidad",
                    ""
                ),

            "Estado":
                proyecto.get(
                    "estado",
                    ""
                ),

            "Prioridad":
                proyecto.get(
                    "prioridad",
                    ""
                ),

            "Responsable":
                proyecto.get(
                    "responsable",
                    ""
                ),

            "Valor":
                formatear_moneda(
                    proyecto.get(
                        "valor_estimado",
                        0
                    )
                ),

            "Probabilidad":
                (
                    f"{proyecto.get('probabilidad', 0) or 0}%"
                ),

            "Próxima acción":
                proyecto.get(
                    "proxima_accion",
                    ""
                )
        })

    st.dataframe(
        datos,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# EDITAR PROYECTO
# ============================================================

def mostrar_edicion_proyecto(
    proyecto
):

    st.markdown(
        "### ✏️ Editar proyecto"
    )

    proyecto_id = str(
        proyecto.get(
            "id",
            "sin_id"
        )
    )

    with st.form(
        f"editar_proyecto_{proyecto_id}"
    ):

        nombre = st.text_input(
            "Nombre del proyecto",
            value=proyecto.get(
                "nombre",
                ""
            )
        )

        col1, col2 = st.columns(2)

        with col1:

            entidad = st.text_input(
                "Entidad / cliente",
                value=proyecto.get(
                    "entidad",
                    ""
                )
            )

            municipio = st.text_input(
                "Municipio",
                value=proyecto.get(
                    "municipio",
                    ""
                )
            )

            tipo_actual = proyecto.get(
                "tipo",
                TIPOS_PROYECTO[0]
            )

            indice_tipo = (
                TIPOS_PROYECTO.index(
                    tipo_actual
                )
                if tipo_actual in TIPOS_PROYECTO
                else 0
            )

            tipo = st.selectbox(
                "Tipo de proyecto",
                TIPOS_PROYECTO,
                index=indice_tipo
            )

            valor = st.number_input(
                "Valor estimado COP",
                min_value=0.0,
                value=float(
                    proyecto.get(
                        "valor_estimado",
                        0
                    )
                    or 0
                ),
                step=1000000.0,
                format="%.0f"
            )

        with col2:

            responsable = st.text_input(
                "Responsable",
                value=proyecto.get(
                    "responsable",
                    ""
                )
            )

            estado_actual = proyecto.get(
                "estado",
                ESTADOS_PROYECTO[0]
            )

            indice_estado = (
                ESTADOS_PROYECTO.index(
                    estado_actual
                )
                if estado_actual in ESTADOS_PROYECTO
                else 0
            )

            estado = st.selectbox(
                "Estado",
                ESTADOS_PROYECTO,
                index=indice_estado
            )

            prioridad_actual = proyecto.get(
                "prioridad",
                PRIORIDADES[0]
            )

            indice_prioridad = (
                PRIORIDADES.index(
                    prioridad_actual
                )
                if prioridad_actual in PRIORIDADES
                else 0
            )

            prioridad = st.selectbox(
                "Prioridad",
                PRIORIDADES,
                index=indice_prioridad
            )

            probabilidad = st.slider(
                "Probabilidad comercial",
                0,
                100,
                int(
                    proyecto.get(
                        "probabilidad",
                        0
                    )
                    or 0
                ),
                5
            )

        situacion = st.text_area(
            "Situación actual",
            value=proyecto.get(
                "situacion_actual",
                ""
            ),
            height=120
        )

        proxima_accion = st.text_area(
            "Próxima acción",
            value=proyecto.get(
                "proxima_accion",
                ""
            ),
            height=120
        )

        guardar = st.form_submit_button(
            "💾 Guardar cambios",
            type="primary",
            use_container_width=True
        )

        if guardar:

            if not nombre.strip():

                st.error(
                    "El proyecto debe tener un nombre."
                )

                return

            campos = {

                "nombre":
                    nombre.strip(),

                "entidad":
                    entidad.strip(),

                "municipio":
                    municipio.strip(),

                "tipo":
                    tipo,

                "valor_estimado":
                    valor,

                "responsable":
                    responsable.strip(),

                "estado":
                    estado,

                "prioridad":
                    prioridad,

                "probabilidad":
                    probabilidad,

                "situacion_actual":
                    situacion.strip(),

                "proxima_accion":
                    proxima_accion.strip()
            }

            cambios = []

            for campo, nuevo in campos.items():

                anterior = proyecto.get(
                    campo
                )

                if anterior != nuevo:

                    cambios.append(
                        f"{campo}: "
                        f"{anterior} → {nuevo}"
                    )

                    proyecto[
                        campo
                    ] = nuevo

            if cambios:

                proyecto[
                    "ultima_actualizacion"
                ] = datetime.now().isoformat()

                registrar_cambio(
                    proyecto,
                    (
                        "Proyecto actualizado. "
                        + " | ".join(
                            cambios
                        )
                    ),
                    responsable.strip()
                )

                st.success(
                    "Proyecto actualizado correctamente."
                )

                st.rerun()

            else:

                st.info(
                    "No se detectaron cambios."
                )


# ============================================================
# ENVIAR A PAPELERA
# ============================================================

def enviar_a_papelera(
    proyecto,
    proyectos
):

    papelera = inicializar_papelera()

    eliminado = dict(
        proyecto
    )

    eliminado[
        "fecha_eliminacion"
    ] = datetime.now().isoformat()

    eliminado[
        "eliminado_por"
    ] = st.session_state.get(
        "portfolio_user",
        ""
    )

    registrar_cambio(
        eliminado,
        "Proyecto enviado a la papelera.",
        st.session_state.get(
            "portfolio_user",
            ""
        )
    )

    papelera.append(
        eliminado
    )

    if proyecto in proyectos:

        proyectos.remove(
            proyecto
        )


# ============================================================
# GESTIÓN DEL PROYECTO
# ============================================================

def mostrar_gestion_proyecto(
    proyecto,
    proyectos
):

    st.divider()

    st.markdown(
        "### ⚙️ Gestión del proyecto"
    )

    st.caption(
        "Puedes modificar la información o enviar "
        "el proyecto a la papelera."
    )

    tab_editar, tab_eliminar = st.tabs(
        [
            "✏️ Editar proyecto",
            "🗑️ Eliminar proyecto"
        ]
    )

    with tab_editar:

        mostrar_edicion_proyecto(
            proyecto
        )

    with tab_eliminar:

        st.warning(
            "El proyecto será enviado primero a la "
            "papelera. Podrás restaurarlo posteriormente."
        )

        st.write(
            "**Proyecto seleccionado:**"
        )

        st.write(
            proyecto.get(
                "nombre",
                ""
            )
        )

        proyecto_id = str(
            proyecto.get(
                "id",
                ""
            )
        )

        confirmar = st.checkbox(
            "Confirmo que deseo enviar este "
            "proyecto a la papelera.",
            key=(
                "confirmar_papelera_"
                + proyecto_id
            )
        )

        if st.button(
            "🗑️ Enviar a papelera",
            type="primary",
            use_container_width=True,
            disabled=not confirmar,
            key=(
                "enviar_papelera_"
                + proyecto_id
            )
        ):

            enviar_a_papelera(
                proyecto,
                proyectos
            )

            st.success(
                "Proyecto enviado a la papelera."
            )

            st.rerun()


# ============================================================
# FICHA EJECUTIVA
# ============================================================

def mostrar_detalle_proyecto(
    proyectos
):

    if not proyectos:
        return

    st.divider()

    st.subheader(
        "🔎 Ficha ejecutiva del proyecto"
    )

    opciones = {}

    for indice, proyecto in enumerate(
        proyectos
    ):

        etiqueta = (
            f"{proyecto.get('nombre', 'Proyecto')} | "
            f"{proyecto.get('entidad', 'Sin entidad')} "
            f"[{indice + 1}]"
        )

        opciones[
            etiqueta
        ] = indice

    seleccion = st.selectbox(
        "Seleccionar proyecto",
        list(
            opciones.keys()
        ),
        key="portfolio_detalle_proyecto"
    )

    proyecto = proyectos[
        opciones[
            seleccion
        ]
    ]

    with st.container(
        border=True
    ):

        st.markdown(
            f"## {proyecto.get('nombre', '')}"
        )

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        with col1:

            st.write(
                "**Estado**"
            )

            st.write(
                proyecto.get(
                    "estado",
                    "Sin definir"
                )
            )

        with col2:

            st.write(
                "**Prioridad**"
            )

            st.write(
                proyecto.get(
                    "prioridad",
                    "Sin definir"
                )
            )

        with col3:

            st.write(
                "**Valor estimado**"
            )

            st.write(
                formatear_moneda(
                    proyecto.get(
                        "valor_estimado",
                        0
                    )
                )
            )

        with col4:

            st.write(
                "**Responsable**"
            )

            st.write(
                proyecto.get(
                    "responsable",
                    ""
                )
                or "Sin asignar"
            )

        st.divider()

        col5, col6 = st.columns(2)

        with col5:

            st.write(
                "**Entidad / Cliente**"
            )

            st.write(
                proyecto.get(
                    "entidad",
                    ""
                )
                or "No informado"
            )

            st.write(
                "**Tipo de proyecto**"
            )

            st.write(
                proyecto.get(
                    "tipo",
                    ""
                )
                or "No informado"
            )

        with col6:

            st.write(
                "**Municipio**"
            )

            st.write(
                proyecto.get(
                    "municipio",
                    ""
                )
                or "No informado"
            )

            st.write(
                "**Probabilidad comercial**"
            )

            st.write(
                f"{proyecto.get('probabilidad', 0) or 0}%"
            )

        st.divider()

        st.markdown(
            "### 📌 Situación actual"
        )

        st.write(
            proyecto.get(
                "situacion_actual",
                ""
            )
            or "Sin información registrada."
        )

        st.markdown(
            "### ➡️ Próxima acción"
        )

        st.write(
            proyecto.get(
                "proxima_accion",
                ""
            )
            or "Sin próxima acción definida."
        )

        fecha_accion = proyecto.get(
            "fecha_proxima_accion"
        )

        if fecha_accion:

            st.caption(
                f"📅 Fecha prevista: "
                f"{fecha_accion}"
            )

        # ====================================================
        # FECHAS CONTRACTUALES
        # ====================================================

        if (
            proyecto.get(
                "fecha_inicio_contrato"
            )
            or proyecto.get(
                "desembolso_anticipo"
            )
            or proyecto.get(
                "fecha_finalizacion"
            )
        ):

            st.divider()

            st.markdown(
                "### 📅 Fechas del proyecto"
            )

            c1, c2, c3 = st.columns(3)

            with c1:

                st.write(
                    "**Inicio**"
                )

                st.write(
                    proyecto.get(
                        "fecha_inicio_contrato"
                    )
                    or "No definido"
                )

            with c2:

                st.write(
                    "**Desembolso / anticipo**"
                )

                st.write(
                    proyecto.get(
                        "desembolso_anticipo"
                    )
                    or "No definido"
                )

            with c3:

                st.write(
                    "**Finalización**"
                )

                st.write(
                    proyecto.get(
                        "fecha_finalizacion"
                    )
                    or "No definido"
                )

        # ====================================================
        # HISTORIAL
        # ====================================================

        st.divider()

        st.markdown(
            "### 🕒 Historial del proyecto"
        )

        historial = proyecto.get(
            "historial",
            []
        )

        if not historial:

            st.info(
                "Este proyecto todavía no tiene "
                "movimientos históricos."
            )

        else:

            for evento in reversed(
                historial
            ):

                fecha = evento.get(
                    "fecha",
                    "Sin fecha"
                )

                with st.expander(
                    f"📅 {fecha}",
                    expanded=False
                ):

                    fuente = evento.get(
                        "fuente",
                        ""
                    )

                    if fuente:

                        st.caption(
                            f"Fuente: {fuente}"
                        )

                    descripcion = evento.get(
                        "descripcion",
                        ""
                    )

                    if descripcion:

                        st.write(
                            descripcion
                        )

                    if (
                        "valor_estimado"
                        in evento
                    ):

                        st.write(
                            "**Valor registrado:** "
                            + formatear_moneda(
                                evento.get(
                                    "valor_estimado",
                                    0
                                )
                            )
                        )

                    if evento.get(
                        "estado"
                    ):

                        st.write(
                            "**Estado:** "
                            f"{evento.get('estado')}"
                        )

                    cambios = evento.get(
                        "cambios",
                        []
                    )

                    if cambios:

                        st.markdown(
                            "**Cambios detectados:**"
                        )

                        for cambio in cambios:

                            anterior = cambio.get(
                                "anterior"
                            )

                            actual = cambio.get(
                                "actual"
                            )

                            if (
                                cambio.get(
                                    "campo"
                                )
                                == "valor_estimado"
                            ):

                                anterior = (
                                    formatear_moneda(
                                        anterior or 0
                                    )
                                )

                                actual = (
                                    formatear_moneda(
                                        actual or 0
                                    )
                                )

                            st.write(
                                f"• **{cambio.get('etiqueta', '')}:** "
                                f"{anterior} → {actual}"
                            )

        # ====================================================
        # EDITAR / ELIMINAR
        # ====================================================

        mostrar_gestion_proyecto(
            proyecto,
            st.session_state[
                "portfolio_projects"
            ]
        )


# ============================================================
# ATENCIÓN GERENCIAL
# ============================================================

def mostrar_criticos(
    proyectos
):

    st.subheader(
        "🚨 Atención gerencial"
    )

    criticos = obtener_proyectos_criticos(
        proyectos
    )

    if not criticos:

        st.success(
            "No existen proyectos críticos registrados."
        )

        return

    for proyecto in criticos:

        with st.container(
            border=True
        ):

            st.markdown(
                f"### {proyecto.get('nombre', '')}"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.write(
                    f"**Estado:** "
                    f"{proyecto.get('estado', '')}"
                )

            with col2:

                st.write(
                    f"**Prioridad:** "
                    f"{proyecto.get('prioridad', '')}"
                )

            with col3:

                st.write(
                    f"**Responsable:** "
                    f"{proyecto.get('responsable', '') or 'Sin asignar'}"
                )

            st.write(
                "**Situación actual:**"
            )

            st.write(
                proyecto.get(
                    "situacion_actual",
                    ""
                )
                or "Sin información."
            )

            st.write(
                "**Próxima acción:**"
            )

            st.write(
                proyecto.get(
                    "proxima_accion",
                    ""
                )
                or "Sin definir."
            )


# ============================================================
# ACCIONES
# ============================================================

def mostrar_acciones(
    proyectos
):

    st.subheader(
        "⚡ Próximas acciones"
    )

    acciones = obtener_acciones_pendientes(
        proyectos
    )

    if not acciones:

        st.info(
            "No existen acciones pendientes."
        )

        return

    for accion in acciones:

        with st.container(
            border=True
        ):

            st.markdown(
                f"### {accion.get('proyecto', '')}"
            )

            st.write(
                accion.get(
                    "accion",
                    ""
                )
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.caption(
                    "👤 Responsable: "
                    f"{accion.get('responsable') or 'Sin asignar'}"
                )

            with col2:

                st.caption(
                    "🚦 Prioridad: "
                    f"{accion.get('prioridad') or 'Sin definir'}"
                )

            with col3:

                st.caption(
                    "📅 Fecha: "
                    f"{accion.get('fecha') or 'Sin definir'}"
                )


# ============================================================
# NUEVO PROYECTO
# ============================================================

def mostrar_nuevo_proyecto(
    proyectos
):

    st.subheader(
        "➕ Registrar nueva iniciativa / proyecto"
    )

    with st.form(
        "form_nuevo_proyecto"
    ):

        nombre = st.text_input(
            "Nombre del proyecto *"
        )

        col1, col2 = st.columns(2)

        with col1:

            entidad = st.text_input(
                "Entidad / cliente"
            )

            municipio = st.text_input(
                "Municipio"
            )

            tipo = st.selectbox(
                "Tipo de proyecto",
                TIPOS_PROYECTO
            )

            valor = st.number_input(
                "Valor estimado COP",
                min_value=0.0,
                step=1000000.0,
                format="%.0f"
            )

        with col2:

            responsable = st.text_input(
                "Responsable"
            )

            estado = st.selectbox(
                "Estado",
                ESTADOS_PROYECTO
            )

            prioridad = st.selectbox(
                "Prioridad",
                PRIORIDADES
            )

            probabilidad = st.slider(
                "Probabilidad comercial",
                0,
                100,
                20,
                5
            )

        situacion = st.text_area(
            "Situación actual"
        )

        proxima_accion = st.text_area(
            "Próxima acción"
        )

        guardar = st.form_submit_button(
            "💾 Registrar proyecto",
            type="primary",
            use_container_width=True
        )

        if guardar:

            if not nombre.strip():

                st.error(
                    "Debes ingresar el nombre del proyecto."
                )

            else:

                proyecto = {

                    "id":
                        (
                            "PRJ-"
                            + datetime.now().strftime(
                                "%Y%m%d%H%M%S%f"
                            )
                        ),

                    "nombre":
                        nombre.strip(),

                    "entidad":
                        entidad.strip(),

                    "municipio":
                        municipio.strip(),

                    "departamento":
                        "",

                    "tipo":
                        tipo,

                    "valor_estimado":
                        valor,

                    "estado":
                        estado,

                    "prioridad":
                        prioridad,

                    "probabilidad":
                        probabilidad,

                    "responsable":
                        responsable.strip(),

                    "situacion_actual":
                        situacion.strip(),

                    "proxima_accion":
                        proxima_accion.strip(),

                    "fecha_proxima_accion":
                        None,

                    "fecha_creacion":
                        datetime.now().isoformat(),

                    "ultima_actualizacion":
                        datetime.now().isoformat(),

                    "historial":
                        []
                }

                registrar_cambio(
                    proyecto,
                    "Proyecto registrado manualmente.",
                    responsable.strip()
                )

                proyectos.append(
                    proyecto
                )

                st.success(
                    "Proyecto registrado correctamente."
                )

                st.rerun()


# ============================================================
# IMPORTADOR EXCEL
# ============================================================

def mostrar_importador_excel(
    proyectos
):

    st.subheader(
        "📥 Importar portafolio histórico"
    )

    st.write(
        "Carga el archivo Excel de seguimiento. "
        "INTI analizará las hojas y reconstruirá "
        "el historial disponible."
    )

    archivo = st.file_uploader(
        "Seleccionar archivo Excel",
        type=["xlsx"],
        key="portfolio_excel_importer"
    )

    if archivo is not None:

        st.success(
            f"📎 {archivo.name}"
        )

        if st.button(
            "🔍 Analizar archivo",
            type="primary",
            use_container_width=True,
            key="analizar_excel_portafolio"
        ):

            try:

                with st.spinner(
                    "Analizando portafolio..."
                ):

                    resultado = procesar_excel_proyectos(
                        archivo.getvalue()
                    )

                st.session_state[
                    "portfolio_import_preview"
                ] = resultado

                st.success(
                    "Archivo analizado correctamente."
                )

                st.rerun()

            except Exception as error:

                st.error(
                    "No fue posible analizar el archivo."
                )

                st.exception(
                    error
                )

    resultado = st.session_state.get(
        "portfolio_import_preview"
    )

    if not resultado:
        return

    st.divider()

    st.markdown(
        "### 👁️ Vista previa"
    )

    proyectos_importados = resultado.get(
        "proyectos",
        []
    )

    valor_total = sum(
        float(
            proyecto.get(
                "valor_estimado",
                0
            )
            or 0
        )
        for proyecto in proyectos_importados
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Hojas",
            resultado.get(
                "total_hojas",
                0
            )
        )

    with c2:

        st.metric(
            "Proyectos",
            len(
                proyectos_importados
            )
        )

    with c3:

        st.metric(
            "Valor identificado",
            formatear_moneda(
                valor_total
            )
        )

    datos = []

    for proyecto in proyectos_importados:

        datos.append({

            "Proyecto":
                proyecto.get(
                    "nombre",
                    ""
                ),

            "Entidad":
                proyecto.get(
                    "entidad",
                    ""
                ),

            "Prioridad":
                proyecto.get(
                    "prioridad",
                    ""
                ),

            "Valor":
                formatear_moneda(
                    proyecto.get(
                        "valor_estimado",
                        0
                    )
                ),

            "Responsable":
                proyecto.get(
                    "responsable",
                    ""
                ),

            "Estado":
                proyecto.get(
                    "estado",
                    ""
                ),

            "Histórico":
                len(
                    proyecto.get(
                        "historial",
                        []
                    )
                )
        })

    st.dataframe(
        datos,
        use_container_width=True,
        hide_index=True
    )

    st.warning(
        "Revisa la información antes de confirmar."
    )

    confirmar = st.checkbox(
        "He revisado los proyectos y autorizo "
        "la carga al Portafolio INTILED.",
        key="confirmar_excel_portafolio"
    )

    if st.button(
        "📥 Cargar proyectos al Portafolio",
        type="primary",
        use_container_width=True,
        disabled=not confirmar,
        key="confirmar_importacion_portafolio"
    ):

        st.session_state[
            "portfolio_projects"
        ] = proyectos_importados

        st.session_state[
            "portfolio_excel_imported"
        ] = True

        st.session_state[
            "portfolio_import_date"
        ] = datetime.now().isoformat()

        st.session_state.pop(
            "portfolio_import_preview",
            None
        )

        st.success(
            "Portafolio cargado correctamente."
        )

        st.rerun()


# ============================================================
# PAPELERA
# ============================================================

def mostrar_papelera():

    papelera = inicializar_papelera()

    st.subheader(
        "🗑️ Papelera de proyectos"
    )

    st.caption(
        "Los proyectos eliminados pueden restaurarse "
        "mientras permanezcan en la papelera."
    )

    if not papelera:

        st.success(
            "La papelera está vacía."
        )

        return

    st.metric(
        "Proyectos en papelera",
        len(
            papelera
        )
    )

    for indice, proyecto in enumerate(
        list(
            papelera
        )
    ):

        identificador = (
            str(
                proyecto.get(
                    "id",
                    "proyecto"
                )
            )
            + "_"
            + str(
                indice
            )
        )

        with st.container(
            border=True
        ):

            st.markdown(
                f"### {proyecto.get('nombre', '')}"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.write(
                    "**Entidad**"
                )

                st.write(
                    proyecto.get(
                        "entidad",
                        ""
                    )
                    or "No informado"
                )

            with col2:

                st.write(
                    "**Valor**"
                )

                st.write(
                    formatear_moneda(
                        proyecto.get(
                            "valor_estimado",
                            0
                        )
                    )
                )

            with col3:

                st.write(
                    "**Responsable**"
                )

                st.write(
                    proyecto.get(
                        "responsable",
                        ""
                    )
                    or "Sin asignar"
                )

            fecha_eliminacion = proyecto.get(
                "fecha_eliminacion"
            )

            if fecha_eliminacion:

                try:

                    fecha_obj = datetime.fromisoformat(
                        fecha_eliminacion
                    )

                    fecha_eliminacion = (
                        fecha_obj.strftime(
                            "%d/%m/%Y %H:%M"
                        )
                    )

                except Exception:
                    pass

            st.caption(
                f"Eliminado: "
                f"{fecha_eliminacion or 'Sin fecha'}"
            )

            col_restaurar, col_eliminar = (
                st.columns(2)
            )

            with col_restaurar:

                if st.button(
                    "♻️ Restaurar",
                    use_container_width=True,
                    key=(
                        "restaurar_"
                        + identificador
                    )
                ):

                    restaurado = dict(
                        proyecto
                    )

                    restaurado.pop(
                        "fecha_eliminacion",
                        None
                    )

                    restaurado.pop(
                        "eliminado_por",
                        None
                    )

                    registrar_cambio(
                        restaurado,
                        "Proyecto restaurado desde la papelera.",
                        st.session_state.get(
                            "portfolio_user",
                            ""
                        )
                    )

                    st.session_state[
                        "portfolio_projects"
                    ].append(
                        restaurado
                    )

                    papelera.remove(
                        proyecto
                    )

                    st.success(
                        "Proyecto restaurado."
                    )

                    st.rerun()

            with col_eliminar:

                confirmar = st.checkbox(
                    "Confirmar borrado",
                    key=(
                        "confirmar_definitivo_"
                        + identificador
                    )
                )

                if st.button(
                    "❌ Eliminar definitivamente",
                    use_container_width=True,
                    disabled=not confirmar,
                    key=(
                        "eliminar_definitivo_"
                        + identificador
                    )
                ):

                    papelera.remove(
                        proyecto
                    )

                    st.success(
                        "Proyecto eliminado definitivamente."
                    )

                    st.rerun()


# ============================================================
# MÓDULO PRINCIPAL
# ============================================================

def mostrar_portafolio():

    if not esta_autenticado():

        mostrar_login()
        return

    proyectos = inicializar_portafolio()

    mostrar_encabezado()

    st.divider()

    mostrar_metricas(
        proyectos
    )

    mostrar_resumen_estados(
        proyectos
    )

    st.divider()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "📊 Portafolio",
            "🚨 Atención",
            "⚡ Acciones",
            "➕ Nuevo proyecto",
            "📥 Importar Excel",
            "🗑️ Papelera"
        ]
    )

    with tab1:

        filtrados = aplicar_filtros(
            proyectos
        )

        mostrar_tabla(
            filtrados
        )

        mostrar_detalle_proyecto(
            filtrados
        )

    with tab2:

        mostrar_criticos(
            proyectos
        )

    with tab3:

        mostrar_acciones(
            proyectos
        )

    with tab4:

        mostrar_nuevo_proyecto(
            proyectos
        )

    with tab5:

        mostrar_importador_excel(
            proyectos
        )

    with tab6:

        mostrar_papelera()
