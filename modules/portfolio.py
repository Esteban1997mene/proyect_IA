import streamlit as st
from datetime import datetime

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


# ============================================================
# INTI PROJECTS AI
# PORTAFOLIO INTILED
# ============================================================


def inicializar_portafolio():

    if "portfolio_projects" not in st.session_state:

        st.session_state[
            "portfolio_projects"
        ] = []

    return st.session_state[
        "portfolio_projects"
    ]


# ============================================================
# ENCABEZADO
# ============================================================

def mostrar_encabezado():

    col1, col2 = st.columns(
        [5, 1]
    )

    with col1:

        st.title(
            "📊 Portafolio INTILED"
        )

        st.caption(
            "Centro ejecutivo de seguimiento "
            "de proyectos e iniciativas."
        )

    with col2:

        if st.button(
            "🔒 Salir",
            use_container_width=True
        ):

            cerrar_sesion()
            st.rerun()


# ============================================================
# MÉTRICAS
# ============================================================

def mostrar_metricas(
    proyectos
):

    metricas = calcular_metricas(
        proyectos
    )

    st.subheader(
        "📌 Resumen ejecutivo"
    )

    col1, col2, col3, col4, col5 = (
        st.columns(5)
    )

    with col1:

        st.metric(
            "Proyectos",
            metricas["total"]
        )

    with col2:

        st.metric(
            "Valor estimado",
            formatear_moneda(
                metricas[
                    "valor_total"
                ]
            )
        )

    with col3:

        st.metric(
            "Pipeline ponderado",
            formatear_moneda(
                metricas[
                    "valor_ponderado"
                ]
            )
        )

    with col4:

        st.metric(
            "Prioridad P1",
            metricas[
                "prioridad_1"
            ]
        )

    with col5:

        st.metric(
            "Bloqueados",
            metricas[
                "bloqueados"
            ]
        )


# ============================================================
# FILTROS
# ============================================================

def aplicar_filtros(
    proyectos
):

    st.subheader(
        "🔎 Buscar proyectos"
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        busqueda = st.text_input(
            "Buscar",
            placeholder=(
                "Proyecto, entidad, municipio..."
            )
        )

    with col2:

        estado = st.selectbox(
            "Estado",
            [
                "Todos"
            ] + ESTADOS_PROYECTO
        )

    with col3:

        prioridad = st.selectbox(
            "Prioridad",
            [
                "Todas"
            ] + PRIORIDADES
        )

    resultado = proyectos

    if busqueda:

        texto = busqueda.lower()

        resultado = [
            p
            for p in resultado
            if texto in (
                str(
                    p.get(
                        "nombre",
                        ""
                    )
                )
                + " "
                + str(
                    p.get(
                        "entidad",
                        ""
                    )
                )
                + " "
                + str(
                    p.get(
                        "municipio",
                        ""
                    )
                )
            ).lower()
        ]

    if estado != "Todos":

        resultado = [
            p
            for p in resultado
            if p.get(
                "estado"
            ) == estado
        ]

    if prioridad != "Todas":

        resultado = [
            p
            for p in resultado
            if p.get(
                "prioridad"
            ) == prioridad
        ]

    return resultado


# ============================================================
# TABLA EJECUTIVA
# ============================================================

def mostrar_tabla(
    proyectos
):

    st.subheader(
        "📋 Proyectos"
    )

    if not proyectos:

        st.info(
            "No existen proyectos "
            "para mostrar."
        )

        return

    datos = []

    for proyecto in proyectos:

        datos.append({

            "Proyecto":
                proyecto.get(
                    "nombre"
                ),

            "Entidad":
                proyecto.get(
                    "entidad"
                ),

            "Estado":
                proyecto.get(
                    "estado"
                ),

            "Prioridad":
                proyecto.get(
                    "prioridad"
                ),

            "Responsable":
                proyecto.get(
                    "responsable"
                ),

            "Valor":
                formatear_moneda(
                    proyecto.get(
                        "valor_estimado",
                        0
                    )
                ),

            "Prob.":
                f"{proyecto.get('probabilidad', 0)}%",

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
# PROYECTOS CRÍTICOS
# ============================================================

def mostrar_criticos(
    proyectos
):

    criticos = (
        obtener_proyectos_criticos(
            proyectos
        )
    )

    st.subheader(
        "🚨 Atención gerencial"
    )

    if not criticos:

        st.success(
            "No existen proyectos críticos "
            "registrados."
        )

        return

    for proyecto in criticos:

        with st.container(
            border=True
        ):

            st.markdown(
                f"### {proyecto.get('nombre', '')}"
            )

            col1, col2, col3 = (
                st.columns(3)
            )

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
                    f"{proyecto.get('responsable', '')}"
                )

            st.write(
                "**Situación actual:**"
            )

            st.write(
                proyecto.get(
                    "situacion_actual",
                    "Sin información"
                )
            )

            st.write(
                "**Próxima acción:**"
            )

            st.write(
                proyecto.get(
                    "proxima_accion",
                    "Sin definir"
                )
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

    acciones = (
        obtener_acciones_pendientes(
            proyectos
        )
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
                f"**{accion['proyecto']}**"
            )

            st.write(
                accion[
                    "accion"
                ]
            )

            col1, col2 = st.columns(
                2
            )

            with col1:

                st.caption(
                    "Responsable: "
                    f"{accion['responsable'] or 'Sin asignar'}"
                )

            with col2:

                st.caption(
                    "Prioridad: "
                    f"{accion['prioridad']}"
                )


# ============================================================
# NUEVO PROYECTO
# ============================================================

def mostrar_nuevo_proyecto(
    proyectos
):

    with st.expander(
        "➕ Registrar nueva iniciativa / proyecto"
    ):

        with st.form(
            "form_nuevo_proyecto"
        ):

            nombre = st.text_input(
                "Nombre del proyecto *"
            )

            col1, col2 = st.columns(
                2
            )

            with col1:

                entidad = st.text_input(
                    "Entidad / cliente"
                )

                municipio = st.text_input(
                    "Municipio"
                )

                tipo = st.selectbox(
                    "Tipo",
                    TIPOS_PROYECTO
                )

                valor = st.number_input(
                    "Valor estimado COP",
                    min_value=0.0,
                    step=1000000.0
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
                    20
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
                        "Debes ingresar el nombre "
                        "del proyecto."
                    )

                else:

                    id_proyecto = (
                        f"PRJ-"
                        f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
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
                        "Proyecto registrado "
                        "en Portafolio INTILED.",
                        responsable
                    )

                    proyectos.append(
                        proyecto
                    )

                    st.success(
                        "Proyecto registrado."
                    )

                    st.rerun()


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

    proyectos = (
        inicializar_portafolio()
    )

    # ========================================================
    # CABECERA
    # ========================================================

    mostrar_encabezado()

    st.divider()

    # ========================================================
    # MÉTRICAS
    # ========================================================

    mostrar_metricas(
        proyectos
    )

    st.divider()

    # ========================================================
    # PESTAÑAS
    # ========================================================

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📊 Portafolio",
            "🚨 Atención",
            "⚡ Acciones",
            "➕ Nuevo proyecto"
        ]
    )

    with tab1:

        filtrados = aplicar_filtros(
            proyectos
        )

        mostrar_tabla(
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
