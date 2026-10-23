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
# UTILIDADES
# ============================================================

def obtener_id_seguro(proyecto, indice=0):

    proyecto_id = str(
        proyecto.get("id", "")
    ).strip()

    if proyecto_id:
        return proyecto_id

    return (
        "proyecto_"
        + str(indice)
        + "_"
        + str(
            abs(
                hash(
                    (
                        proyecto.get("nombre", ""),
                        proyecto.get("entidad", ""),
                        proyecto.get("responsable", "")
                    )
                )
            )
        )
    )


def limpiar_modos_gestion():

    st.session_state["portfolio_edit_mode"] = False
    st.session_state["portfolio_delete_mode"] = False

    st.session_state.pop(
        "portfolio_manage_id",
        None
    )


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

            limpiar_modos_gestion()

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
            metricas.get(
                "total",
                0
            )
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

    if not conteo:
        return

    st.markdown(
        "### 🚦 Estado general"
    )

    estados_ordenados = sorted(
        conteo.items(),
        key=lambda x: x[1],
        reverse=True
    )

    cantidad_columnas = min(
        len(estados_ordenados),
        5
    )

    if cantidad_columnas <= 0:
        return

    columnas = st.columns(
        cantidad_columnas
    )

    for indice, (
        estado,
        cantidad
    ) in enumerate(
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

    resultado = list(
        proyectos
    )

    if busqueda:

        texto = busqueda.lower().strip()

        resultado = [
            proyecto
            for proyecto in resultado
            if texto in (
                str(
                    proyecto.get(
                        "nombre",
                        ""
                    )
                )
                + " "
                + str(
                    proyecto.get(
                        "entidad",
                        ""
                    )
                )
                + " "
                + str(
                    proyecto.get(
                        "municipio",
                        ""
                    )
                )
                + " "
                + str(
                    proyecto.get(
                        "responsable",
                        ""
                    )
                )
            ).lower()
        ]

    if estado != "Todos":

        resultado = [
            proyecto
            for proyecto in resultado
            if proyecto.get(
                "estado"
            ) == estado
        ]

    if prioridad != "Todas":

        resultado = [
            proyecto
            for proyecto in resultado
            if proyecto.get(
                "prioridad"
            ) == prioridad
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
    proyecto,
    proyecto_id
):

    st.markdown(
        "### ✏️ Editar proyecto"
    )

    st.info(
        "Modifica la información necesaria y "
        "pulsa Guardar cambios."
    )

    with st.form(
        f"form_editar_{proyecto_id}"
    ):

        nombre = st.text_input(
            "Nombre del proyecto",
            value=proyecto.get(
                "nombre",
                ""
            )
        )

        entidad = st.text_input(
            "Entidad / cliente",
            value=proyecto.get(
                "entidad",
                ""
            )
        )

        col1, col2 = st.columns(2)

        with col1:

            municipio = st.text_input(
                "Municipio",
                value=proyecto.get(
                    "municipio",
                    ""
                )
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

            responsable = st.text_input(
                "Responsable",
                value=proyecto.get(
                    "responsable",
                    ""
                )
            )

        with col2:

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

        probabilidad_actual = int(
            proyecto.get(
                "probabilidad",
                0
            )
            or 0
        )

        probabilidad_actual = max(
            0,
            min(
                probabilidad_actual,
                100
            )
        )

        probabilidad = st.slider(
            "Probabilidad comercial",
            min_value=0,
            max_value=100,
            value=probabilidad_actual,
            step=5
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

            nuevos_datos = {

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

            for campo, nuevo_valor in nuevos_datos.items():

                valor_anterior = proyecto.get(
                    campo
                )

                if valor_anterior != nuevo_valor:

                    cambios.append(
                        f"{campo}: "
                        f"{valor_anterior} → "
                        f"{nuevo_valor}"
                    )

                    proyecto[
                        campo
                    ] = nuevo_valor

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
                    st.session_state.get(
                        "portfolio_user",
                        ""
                    )
                )

                limpiar_modos_gestion()

                st.success(
                    "✅ Proyecto actualizado correctamente."
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

    proyecto_eliminado = dict(
        proyecto
    )

    proyecto_eliminado[
        "historial"
    ] = list(
        proyecto.get(
            "historial",
            []
        )
    )

    proyecto_eliminado[
        "fecha_eliminacion"
    ] = datetime.now().isoformat()

    proyecto_eliminado[
        "eliminado_por"
    ] = st.session_state.get(
        "portfolio_user",
        ""
    )

    registrar_cambio(
        proyecto_eliminado,
        "Proyecto enviado a la papelera.",
        st.session_state.get(
            "portfolio_user",
            ""
        )
    )

    papelera.append(
        proyecto_eliminado
    )

    if proyecto in proyectos:

        proyectos.remove(
            proyecto
        )


# ============================================================
# GESTIÓN SIMPLE
# ============================================================

def mostrar_gestion_proyecto(
    proyecto,
    proyectos,
    proyecto_id
):

    st.divider()

    st.markdown(
        "## ⚙️ Gestionar proyecto"
    )

    st.caption(
        "Selecciona una acción para este proyecto."
    )

    col_editar, col_eliminar = st.columns(2)

    # ========================================================
    # EDITAR
    # ========================================================

    with col_editar:

        if st.button(
            "✏️ Editar proyecto",
            type="primary",
            use_container_width=True,
            key=(
                "boton_editar_"
                + proyecto_id
            )
        ):

            st.session_state[
                "portfolio_edit_mode"
            ] = True

            st.session_state[
                "portfolio_delete_mode"
            ] = False

            st.session_state[
                "portfolio_manage_id"
            ] = proyecto_id

            st.rerun()

    # ========================================================
    # ELIMINAR
    # ========================================================

    with col_eliminar:

        if st.button(
            "🗑️ Eliminar proyecto",
            use_container_width=True,
            key=(
                "boton_eliminar_"
                + proyecto_id
            )
        ):

            st.session_state[
                "portfolio_delete_mode"
            ] = True

            st.session_state[
                "portfolio_edit_mode"
            ] = False

            st.session_state[
                "portfolio_manage_id"
            ] = proyecto_id

            st.rerun()

    # ========================================================
    # FORMULARIO DE EDICIÓN
    # ========================================================

    if (
        st.session_state.get(
            "portfolio_edit_mode",
            False
        )
        and
        st.session_state.get(
            "portfolio_manage_id"
        )
        == proyecto_id
    ):

        st.divider()

        mostrar_edicion_proyecto(
            proyecto,
            proyecto_id
        )

        if st.button(
            "↩️ Cancelar edición",
            use_container_width=True,
            key=(
                "cancelar_edicion_"
                + proyecto_id
            )
        ):

            limpiar_modos_gestion()

            st.rerun()

    # ========================================================
    # CONFIRMACIÓN DE ELIMINACIÓN
    # ========================================================

    if (
        st.session_state.get(
            "portfolio_delete_mode",
            False
        )
        and
        st.session_state.get(
            "portfolio_manage_id"
        )
        == proyecto_id
    ):

        st.divider()

        st.error(
            "⚠️ Confirmar eliminación"
        )

        st.markdown(
            f"### {proyecto.get('nombre', '')}"
        )

        st.write(
            "El proyecto será retirado del portafolio "
            "y enviado a la Papelera."
        )

        st.write(
            "Desde la Papelera podrás restaurarlo "
            "si fue eliminado por error."
        )

        confirmar = st.checkbox(
            "Sí, confirmo que deseo enviar "
            "este proyecto a la papelera.",
            key=(
                "confirmar_eliminar_"
                + proyecto_id
            )
        )

        col_confirmar, col_cancelar = st.columns(2)

        with col_confirmar:

            if st.button(
                "🗑️ Sí, eliminar proyecto",
                type="primary",
                use_container_width=True,
                disabled=not confirmar,
                key=(
                    "confirmar_borrado_"
                    + proyecto_id
                )
            ):

                enviar_a_papelera(
                    proyecto,
                    proyectos
                )

                limpiar_modos_gestion()

                st.success(
                    "Proyecto enviado a la papelera."
                )

                st.rerun()

        with col_cancelar:

            if st.button(
                "Cancelar",
                use_container_width=True,
                key=(
                    "cancelar_eliminar_"
                    + proyecto_id
                )
            ):

                limpiar_modos_gestion()

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

    st.caption(
        "Selecciona un proyecto para consultar, "
        "editar o eliminar su información."
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
            ""
        )

        valor = formatear_moneda(
            proyecto.get(
                "valor_estimado",
                0
            )
        )

        etiqueta = (
            f"{nombre} | "
            f"{entidad or 'Sin entidad'} | "
            f"{valor}"
        )

        if etiqueta in opciones:

            etiqueta = (
                f"{etiqueta} "
                f"[{indice + 1}]"
            )

        opciones[
            etiqueta
        ] = indice

    seleccion = st.selectbox(
        "Proyecto seleccionado",
        list(
            opciones.keys()
        ),
        key="portfolio_detalle_proyecto"
    )

    indice_proyecto = opciones[
        seleccion
    ]

    proyecto = proyectos[
        indice_proyecto
    ]

    proyecto_id = obtener_id_seguro(
        proyecto,
        indice_proyecto
    )

    with st.container(
        border=True
    ):

        st.markdown(
            f"## {proyecto.get('nombre', '')}"
        )

        st.caption(
            proyecto.get(
                "entidad",
                ""
            )
            or "Entidad no registrada"
        )

        # ====================================================
        # RESUMEN
        # ====================================================

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Valor estimado",
                formatear_moneda(
                    proyecto.get(
                        "valor_estimado",
                        0
                    )
                )
            )

        with col2:

            st.write(
                "**Estado**"
            )

            st.write(
                proyecto.get(
                    "estado",
                    "Sin definir"
                )
            )

        with col3:

            st.write(
                "**Prioridad**"
            )

            st.write(
                proyecto.get(
                    "prioridad",
                    "Sin definir"
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

        # ====================================================
        # SITUACIÓN Y ACCIÓN
        # ====================================================

        st.divider()

        col5, col6 = st.columns(2)

        with col5:

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

        with col6:

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

        # ====================================================
        # INFORMACIÓN COMPLETA
        # ====================================================

        with st.expander(
            "📋 Ver información completa"
        ):

            st.write(
                "**Entidad / cliente:**",
                proyecto.get(
                    "entidad",
                    ""
                )
                or "No informado"
            )

            st.write(
                "**Municipio:**",
                proyecto.get(
                    "municipio",
                    ""
                )
                or "No informado"
            )

            st.write(
                "**Departamento:**",
                proyecto.get(
                    "departamento",
                    ""
                )
                or "No informado"
            )

            st.write(
                "**Tipo de proyecto:**",
                proyecto.get(
                    "tipo",
                    ""
                )
                or "No informado"
            )

            st.write(
                "**Probabilidad comercial:**",
                (
                    f"{proyecto.get('probabilidad', 0) or 0}%"
                )
            )

            if proyecto.get(
                "fecha_proxima_accion"
            ):

                st.write(
                    "**Fecha próxima acción:**",
                    proyecto.get(
                        "fecha_proxima_accion"
                    )
                )

            if proyecto.get(
                "fecha_inicio_contrato"
            ):

                st.write(
                    "**Inicio del contrato:**",
                    proyecto.get(
                        "fecha_inicio_contrato"
                    )
                )

            if proyecto.get(
                "desembolso_anticipo"
            ):

                st.write(
                    "**Desembolso / anticipo:**",
                    proyecto.get(
                        "desembolso_anticipo"
                    )
                )

            if proyecto.get(
                "fecha_finalizacion"
            ):

                st.write(
                    "**Finalización:**",
                    proyecto.get(
                        "fecha_finalizacion"
                    )
                )

        # ====================================================
        # HISTORIAL
        # ====================================================

        historial = proyecto.get(
            "historial",
            []
        )

        with st.expander(
            f"🕒 Historial del proyecto ({len(historial)})"
        ):

            if not historial:

                st.info(
                    "No existen movimientos históricos."
                )

            else:

                for evento in reversed(
                    historial
                ):

                    st.markdown(
                        f"**📅 "
                        f"{evento.get('fecha', 'Sin fecha')}**"
                    )

                    if evento.get(
                        "fuente"
                    ):

                        st.caption(
                            "Fuente: "
                            f"{evento.get('fuente')}"
                        )

                    if evento.get(
                        "descripcion"
                    ):

                        st.write(
                            evento.get(
                                "descripcion"
                            )
                        )

                    if (
                        "valor_estimado"
                        in evento
                    ):

                        st.caption(
                            "Valor registrado: "
                            + formatear_moneda(
                                evento.get(
                                    "valor_estimado",
                                    0
                                )
                            )
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

                                anterior = formatear_moneda(
                                    anterior or 0
                                )

                                actual = formatear_moneda(
                                    actual or 0
                                )

                            st.write(
                                f"• "
                                f"{cambio.get('etiqueta', '')}: "
                                f"{anterior} → {actual}"
                            )

                    st.divider()

        # ====================================================
        # GESTIÓN
        # ====================================================

        mostrar_gestion_proyecto(
            proyecto,
            st.session_state[
                "portfolio_projects"
            ],
            proyecto_id
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

    st.caption(
        "Proyectos P1 y proyectos que requieren "
        "atención especial."
    )

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
                    "**Estado**"
                )

                st.write(
                    proyecto.get(
                        "estado",
                        ""
                    )
                )

            with col2:

                st.write(
                    "**Prioridad**"
                )

                st.write(
                    proyecto.get(
                        "prioridad",
                        ""
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
        "➕ Nuevo proyecto"
    )

    st.caption(
        "Registra una nueva iniciativa o proyecto "
        "en el Portafolio INTILED."
    )

    with st.form(
        "form_nuevo_proyecto"
    ):

        nombre = st.text_input(
            "Nombre del proyecto *"
        )

        entidad = st.text_input(
            "Entidad / cliente"
        )

        col1, col2 = st.columns(2)

        with col1:

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
                    "Proyecto registrado manualmente "
                    "en Portafolio INTILED.",
                    st.session_state.get(
                        "portfolio_user",
                        responsable.strip()
                    )
                )

                proyectos.append(
                    proyecto
                )

                st.success(
                    "✅ Proyecto registrado correctamente."
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

    st.warning(
        "Primero se mostrará una vista previa. "
        "Los datos solo serán cargados cuando "
        "confirmes la importación."
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
                key="limpiar_importacion"
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
            len(
                proyectos_importados
            )
        )

    with col3:

        st.metric(
            "Valor identificado",
            formatear_moneda(
                valor_total
            )
        )

    with st.expander(
        "📚 Ver hojas detectadas"
    ):

        for hoja in hojas:

            st.write(
                f"📄 **{hoja.get('nombre', '')}** "
                f"— "
                f"{len(hoja.get('proyectos', []))} "
                f"registros"
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

    if datos:

        st.dataframe(
            datos,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "No se detectaron proyectos para importar."
        )

        return

    if proyectos:

        st.warning(
            f"Actualmente existen {len(proyectos)} "
            "proyectos en el portafolio. "
            "Al confirmar, el portafolio actual "
            "será reemplazado por la información "
            "del archivo importado."
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

        limpiar_modos_gestion()

        st.success(
            "✅ Portafolio cargado correctamente."
        )

        st.rerun()


# ============================================================
# PAPELERA
# ============================================================

def mostrar_papelera():

    papelera = inicializar_papelera()

    st.subheader(
        "🗑️ Papelera"
    )

    st.caption(
        "Aquí aparecen los proyectos retirados "
        "del portafolio. Puedes restaurarlos o "
        "eliminarlos definitivamente."
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

        proyecto_id = obtener_id_seguro(
            proyecto,
            indice
        )

        identificador = (
            proyecto_id
            + "_trash_"
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
                    "**Entidad / cliente**"
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

                    fecha_eliminacion_texto = (
                        fecha_obj.strftime(
                            "%d/%m/%Y %H:%M"
                        )
                    )

                except Exception:

                    fecha_eliminacion_texto = str(
                        fecha_eliminacion
                    )

            else:

                fecha_eliminacion_texto = (
                    "Sin fecha"
                )

            st.caption(
                f"🕒 Enviado a papelera: "
                f"{fecha_eliminacion_texto}"
            )

            eliminado_por = proyecto.get(
                "eliminado_por",
                ""
            )

            if eliminado_por:

                st.caption(
                    f"👤 Por: {eliminado_por}"
                )

            col_restaurar, col_eliminar = (
                st.columns(2)
            )

            # =================================================
            # RESTAURAR
            # =================================================

            with col_restaurar:

                if st.button(
                    "♻️ Restaurar proyecto",
                    type="primary",
                    use_container_width=True,
                    key=(
                        "restaurar_"
                        + identificador
                    )
                ):

                    restaurado = dict(
                        proyecto
                    )

                    restaurado[
                        "historial"
                    ] = list(
                        proyecto.get(
                            "historial",
                            []
                        )
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
                        "Proyecto restaurado correctamente."
                    )

                    st.rerun()

            # =================================================
            # ELIMINAR DEFINITIVAMENTE
            # =================================================

            with col_eliminar:

                confirmar_definitivo = st.checkbox(
                    "Confirmar borrado definitivo",
                    key=(
                        "confirmar_definitivo_"
                        + identificador
                    )
                )

                if st.button(
                    "❌ Eliminar definitivamente",
                    use_container_width=True,
                    disabled=not confirmar_definitivo,
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

    if not fecha:
        return

    try:

        fecha_obj = datetime.fromisoformat(
            fecha
        )

        fecha_texto = fecha_obj.strftime(
            "%d/%m/%Y %H:%M"
        )

    except Exception:

        fecha_texto = str(
            fecha
        )

    st.success(
        f"📥 Portafolio importado: {fecha_texto}"
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
    # INICIALIZAR DATOS
    # ========================================================

    proyectos = inicializar_portafolio()

    inicializar_papelera()

    # ========================================================
    # ENCABEZADO
    # ========================================================

    mostrar_encabezado()

    mostrar_estado_importacion()

    st.divider()

    # ========================================================
    # RESUMEN EJECUTIVO
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
    # ATENCIÓN GERENCIAL
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

    # ========================================================
    # PAPELERA
    # ========================================================

    with tab6:

        mostrar_papelera()
