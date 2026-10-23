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
# INICIALIZAR PORTAFOLIO
# ============================================================

def inicializar_portafolio():
    if "portfolio_projects" not in st.session_state:
        st.session_state["portfolio_projects"] = []

    return st.session_state["portfolio_projects"]


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

        st.caption(f"👤 {usuario}")

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
    metricas = calcular_metricas(proyectos)

    st.subheader("📌 Resumen ejecutivo")

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
                metricas.get("valor_total", 0)
            )
        )

    with col3:
        st.metric(
            "Pipeline ponderado",
            formatear_moneda(
                metricas.get("valor_ponderado", 0)
            )
        )

    with col4:
        st.metric(
            "Prioridad P1",
            metricas.get("prioridad_1", 0)
        )

    with col5:
        st.metric(
            "Bloqueados",
            metricas.get("bloqueados", 0)
        )


# ============================================================
# RESUMEN POR ESTADOS
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
            conteo.get(estado, 0) + 1
        )

    st.markdown("### 🚦 Estado general")

    estados_ordenados = sorted(
        conteo.items(),
        key=lambda x: x[1],
        reverse=True
    )

    cantidad_columnas = min(
        len(estados_ordenados),
        5
    )

    if cantidad_columnas == 0:
        return

    columnas = st.columns(
        cantidad_columnas
    )

    for indice, (estado, cantidad) in enumerate(
        estados_ordenados[:5]
    ):
        with columnas[indice]:
            st.metric(
                estado,
                cantidad
            )


# ============================================================
# FILTROS
# ============================================================

def aplicar_filtros(proyectos):
    st.subheader("🔎 Buscar proyectos")

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
# TABLA DEL PORTAFOLIO
# ============================================================

def mostrar_tabla(proyectos):
    st.subheader("📋 Proyectos")

    if not proyectos:
        st.info(
            "No existen proyectos para mostrar."
        )
        return

    datos = []

    for proyecto in proyectos:
        probabilidad = proyecto.get(
            "probabilidad",
            0
        ) or 0

        datos.append({
            "Proyecto":
                proyecto.get("nombre", ""),

            "Entidad":
                proyecto.get("entidad", ""),

            "Estado":
                proyecto.get("estado", ""),

            "Prioridad":
                proyecto.get("prioridad", ""),

            "Responsable":
                proyecto.get("responsable", ""),

            "Valor":
                formatear_moneda(
                    proyecto.get(
                        "valor_estimado",
                        0
                    )
                ),

            "Probabilidad":
                f"{probabilidad}%",

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
# FICHA EJECUTIVA
# ============================================================

def mostrar_detalle_proyecto(proyectos):
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
        nombre = proyecto.get(
            "nombre",
            "Proyecto"
        )

        entidad = proyecto.get(
            "entidad",
            "Sin entidad"
        )

        etiqueta = (
            f"{nombre} | {entidad} "
            f"[{indice + 1}]"
        )

        opciones[etiqueta] = indice

    seleccion = st.selectbox(
        "Seleccionar proyecto",
        list(opciones.keys()),
        key="portfolio_detalle_proyecto"
    )

    proyecto = proyectos[
        opciones[seleccion]
    ]

    with st.container(border=True):
        st.markdown(
            f"## {proyecto.get('nombre', '')}"
        )

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        with col1:
            st.write("**Estado**")
            st.write(
                proyecto.get(
                    "estado",
                    "Sin definir"
                )
            )

        with col2:
            st.write("**Prioridad**")
            st.write(
                proyecto.get(
                    "prioridad",
                    "Sin definir"
                )
            )

        with col3:
            st.write("**Valor estimado**")
            st.write(
                formatear_moneda(
                    proyecto.get(
                        "valor_estimado",
                        0
                    )
                )
            )

        with col4:
            st.write("**Responsable**")
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
            st.write("**Entidad / Cliente**")
            st.write(
                proyecto.get(
                    "entidad",
                    ""
                )
                or "No informado"
            )

            st.write("**Tipo de proyecto**")
            st.write(
                proyecto.get(
                    "tipo",
                    ""
                )
                or "No informado"
            )

        with col6:
            st.write("**Municipio**")
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
                f"📅 Fecha prevista: {fecha_accion}"
            )

        # ====================================================
        # FECHAS DEL PROYECTO
        # ====================================================

        if (
            proyecto.get("fecha_inicio_contrato")
            or proyecto.get("desembolso_anticipo")
            or proyecto.get("fecha_finalizacion")
        ):
            st.divider()

            st.markdown(
                "### 📅 Fechas del proyecto"
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                st.write("**Inicio**")
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
                st.write("**Finalización**")
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

                    if "valor_estimado" in evento:
                        st.write(
                            "**Valor registrado:** "
                            + formatear_moneda(
                                evento.get(
                                    "valor_estimado",
                                    0
                                )
                            )
                        )

                    if evento.get("estado"):
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
                                cambio.get("campo")
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


# ============================================================
# ATENCIÓN GERENCIAL
# ============================================================

def mostrar_criticos(proyectos):
    st.subheader(
        "🚨 Atención gerencial"
    )

    criticos = obtener_proyectos_criticos(
        proyectos
    )

    if not criticos:
        st.success(
            "No existen proyectos críticos "
            "registrados."
        )
        return

    st.caption(
        "Proyectos P1 y proyectos actualmente "
        "identificados como bloqueados."
    )

    for proyecto in criticos:
        with st.container(border=True):
            st.markdown(
                f"### {proyecto.get('nombre', '')}"
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            with col1:
                st.write("**Estado**")
                st.write(
                    proyecto.get(
                        "estado",
                        ""
                    )
                )

            with col2:
                st.write("**Prioridad**")
                st.write(
                    proyecto.get(
                        "prioridad",
                        ""
                    )
                )

            with col3:
                st.write("**Responsable**")
                st.write(
                    proyecto.get(
                        "responsable",
                        ""
                    )
                    or "Sin asignar"
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

def mostrar_acciones(proyectos):
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
        with st.container(border=True):
            st.markdown(
                f"### {accion.get('proyecto', '')}"
            )

            st.write(
                accion.get(
                    "accion",
                    ""
                )
            )

            col1, col2, col3 = (
                st.columns(3)
            )

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

def mostrar_nuevo_proyecto(proyectos):
    st.subheader(
        "➕ Registrar nueva iniciativa / proyecto"
    )

    st.caption(
        "Utiliza este formulario para agregar "
        "proyectos nuevos al portafolio."
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
                min_value=0,
                max_value=100,
                value=20,
                step=5
            )

        situacion = st.text_area(
            "Situación actual",
            height=100
        )

        proxima_accion = st.text_area(
            "Próxima acción",
            height=100
        )

        guardar = st.form_submit_button(
            "💾 Registrar proyecto",
            type="primary",
            use_container_width=True
        )

        if guardar:
            if not nombre.strip():
                st.error(
                    "Debes ingresar el nombre "
                    "del proyecto."
                )

            else:
                id_proyecto = (
                    "PRJ-"
                    + datetime.now().strftime(
                        "%Y%m%d%H%M%S%f"
                    )
                )

                proyecto = {
                    "id":
                        id_proyecto,

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
                    (
                        "Proyecto registrado "
                        "manualmente en "
                        "Portafolio INTILED."
                    ),
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
# IMPORTAR EXCEL
# ============================================================

def mostrar_importador_excel(proyectos):
    st.subheader(
        "📥 Importar portafolio histórico"
    )

    st.write(
        "Carga el archivo Excel de seguimiento de "
        "proyectos de INTILED. INTI analizará las "
        "hojas, identificará los proyectos actuales "
        "y reconstruirá el historial disponible."
    )

    st.warning(
        "La importación no se realizará inmediatamente. "
        "Primero podrás revisar una vista previa y luego "
        "confirmar la carga."
    )

    archivo = st.file_uploader(
        "Seleccionar archivo Excel",
        type=["xlsx"],
        key="portfolio_excel_importer"
    )

    if archivo is not None:
        st.success(
            f"📎 Archivo seleccionado: {archivo.name}"
        )

        col1, col2 = st.columns(
            [2, 1]
        )

        with col1:
            analizar = st.button(
                "🔍 Analizar archivo",
                type="primary",
                use_container_width=True,
                key="analizar_excel_portafolio"
            )

        with col2:
            limpiar = st.button(
                "🗑️ Limpiar análisis",
                use_container_width=True,
                key="limpiar_importacion_portafolio"
            )

        if limpiar:
            st.session_state.pop(
                "portfolio_import_preview",
                None
            )
            st.rerun()

        if analizar:
            try:
                with st.spinner(
                    "INTI está analizando el archivo..."
                ):
                    resultado = (
                        procesar_excel_proyectos(
                            archivo.getvalue()
                        )
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
                    "No fue posible analizar "
                    "el archivo Excel."
                )

                st.exception(error)

    # ========================================================
    # VISTA PREVIA
    # ========================================================

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

    hojas = resultado.get(
        "hojas",
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

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Hojas detectadas",
            resultado.get(
                "total_hojas",
                len(hojas)
            )
        )

    with col2:
        st.metric(
            "Proyectos detectados",
            resultado.get(
                "total_proyectos",
                len(proyectos_importados)
            )
        )

    with col3:
        st.metric(
            "Valor identificado",
            formatear_moneda(
                valor_total
            )
        )

    # ========================================================
    # HOJAS
    # ========================================================

    with st.expander(
        "📚 Hojas históricas detectadas"
    ):
        if not hojas:
            st.info(
                "No se detectaron hojas."
            )

        for hoja in hojas:
            st.write(
                f"📄 **{hoja.get('nombre', '')}** "
                f"— "
                f"{len(hoja.get('proyectos', []))} "
                f"registros"
            )

    # ========================================================
    # TABLA PREVIA
    # ========================================================

    st.markdown(
        "### 📋 Proyectos que serán cargados"
    )

    datos = []

    for proyecto in proyectos_importados:
        historial = proyecto.get(
            "historial",
            []
        )

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
                len(historial)
        })

    if datos:
        st.dataframe(
            datos,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.warning(
            "No se detectaron proyectos "
            "para importar."
        )
        return

    # ========================================================
    # SEGURIDAD DE IMPORTACIÓN
    # ========================================================

    st.info(
        "Los proyectos con nombres distintos no se "
        "fusionan automáticamente. Esto evita que INTI "
        "combine proyectos diferentes sin autorización."
    )

    if proyectos:
        st.warning(
            f"Actualmente existen {len(proyectos)} "
            "proyectos en el portafolio. Si confirmas "
            "esta importación, serán reemplazados por "
            "los registros del Excel."
        )

    st.markdown(
        "### ✅ Confirmar carga"
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
            "✅ Los proyectos fueron cargados "
            "correctamente al Portafolio INTILED."
        )

        st.rerun()


# ============================================================
# ESTADO DE IMPORTACIÓN
# ============================================================

def mostrar_estado_importacion():
    if not st.session_state.get(
        "portfolio_excel_imported",
        False
    ):
        return

    fecha = st.session_state.get(
        "portfolio_import_date"
    )

    if fecha:
        try:
            fecha_obj = datetime.fromisoformat(
                fecha
            )

            fecha_texto = (
                fecha_obj.strftime(
                    "%d/%m/%Y %H:%M"
                )
            )

        except Exception:
            fecha_texto = str(fecha)

    else:
        fecha_texto = (
            "Fecha no disponible"
        )

    st.success(
        "📥 Portafolio histórico cargado "
        f"correctamente — {fecha_texto}"
    )


# ============================================================
# MÓDULO PRINCIPAL
# ============================================================

def mostrar_portafolio():

    # ========================================================
    # SEGURIDAD
    # ========================================================

    if not esta_autenticado():
        mostrar_login()
        return

    # ========================================================
    # DATOS
    # ========================================================

    proyectos = inicializar_portafolio()

    # ========================================================
    # ENCABEZADO
    # ========================================================

    mostrar_encabezado()

    mostrar_estado_importacion()

    st.divider()

    # ========================================================
    # RESUMEN
    # ========================================================

    mostrar_metricas(
        proyectos
    )

    mostrar_resumen_estados(
        proyectos
    )

    st.divider()

    # ========================================================
    # PESTAÑAS
    # ========================================================

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📊 Portafolio",
            "🚨 Atención",
            "⚡ Acciones",
            "➕ Nuevo proyecto",
            "📥 Importar Excel"
        ]
    )

    # ========================================================
    # PORTAFOLIO
    # ========================================================

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

    # ========================================================
    # ATENCIÓN
    # ========================================================

    with tab2:
        mostrar_criticos(
            proyectos
        )

    # ========================================================
    # ACCIONES
    # ========================================================

    with tab3:
        mostrar_acciones(
            proyectos
        )

    # ========================================================
    # NUEVO PROYECTO
    # ========================================================

    with tab4:
        mostrar_nuevo_proyecto(
            proyectos
        )

    # ========================================================
    # IMPORTAR EXCEL
    # ========================================================

    with tab5:
        mostrar_importador_excel(
            proyectos
        )
