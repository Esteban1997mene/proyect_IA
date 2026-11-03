
# modules/radar.py
# INTI Projects Enterprise - INTILED SAS BIC

import html

import streamlit as st

from services.radar_sources import (
    CATEGORIAS,
    consultar_colombia,
    filtrar_oportunidades,
    opciones_territoriales,
    estado_vigencia,
)

from services.opportunity_classifier import (
    evaluar_oportunidad,
)

from services.opportunity_workspace import (
    ESTADOS,
    iniciar_workspace,
    sincronizar_legacy,
    guardar_oportunidad,
    guardar_y_activar,
    activar_oportunidad,
    oportunidad_activa,
    listar_oportunidades,
    actualizar_estado,
    actualizar_notas,
    exportar_workspace,
    importar_workspace,
    retirar_oportunidad,
    registrar_evento,
)


# ============================================================
# ESTILOS
# ============================================================

def estilos_radar():
    st.markdown(
        """
        <style>
        .inti-radar-hero {
            background: linear-gradient(
                115deg, #202630, #303A48
            );
            border-radius: 18px;
            padding: 30px 34px;
            margin-bottom: 22px;
        }
        .inti-radar-eyebrow {
            color: #FFAD72;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 1.4px;
            margin-bottom: 10px;
        }
        .inti-radar-title {
            color: #FFFFFF;
            font-size: 36px;
            font-weight: 800;
            margin-bottom: 10px;
        }
        .inti-radar-text {
            color: #D2D9E3;
            line-height: 1.65;
            font-size: 15px;
        }
        .inti-radar-section {
            font-size: 20px;
            font-weight: 750;
            margin: 24px 0 12px;
            color: #242C39;
        }
        .inti-radar-table-wrap {
            overflow-x: auto;
            border: 1px solid #E4E9F0;
            border-radius: 12px;
            background: #FFFFFF;
        }
        .inti-radar-table {
            border-collapse: collapse;
            width: 100%;
            font-size: 13px;
        }
        .inti-radar-table th {
            background: #202630;
            color: white;
            text-align: left;
            padding: 13px;
        }
        .inti-radar-table td {
            padding: 13px;
            border-bottom: 1px solid #E4E9F0;
            vertical-align: top;
            color: #273140;
        }
        .inti-radar-table tbody tr:hover td {
            background: #FFF6EE;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def encabezado():
    st.markdown(
        """
        <div class="inti-radar-hero">
            <div class="inti-radar-eyebrow">
                INTILED SAS BIC · INTELIGENCIA COMERCIAL
            </div>
            <div class="inti-radar-title">
                Radar de oportunidades
            </div>
            <div class="inti-radar-text">
                Colombia · Identificación de convocatorias,
                evaluación preliminar y seguimiento
                independiente de cada oportunidad.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def formato_presupuesto(item):
    valor = item.get("presupuesto")

    if valor is None:
        return "No informado"

    try:
        return f"COP ${float(valor):,.0f}"
    except (TypeError, ValueError):
        return "No informado"


def titulo_corto(item, longitud=95):
    titulo = str(
        item.get("titulo") or "Sin título"
    )
    if len(titulo) > longitud:
        return titulo[:longitud] + "..."
    return titulo


def ir_analisis():
    """
    Utiliza la navegación existente del proyecto.
    El identificador activo permanece guardado.
    """
    from modules.navigation import cambiar_pagina

    sincronizar_legacy()
    cambiar_pagina("🧠 Análisis INTILED")


def preparar(datos):
    preparados = []

    for item in datos:
        registro = dict(item)
        registro["evaluacion"] = (
            evaluar_oportunidad(registro)
        )
        preparados.append(registro)

    return preparados


def tabla_html(datos):
    columnas = [
        ("titulo", "Objeto"),
        ("entidad", "Entidad"),
        ("region", "Departamento"),
        ("localidad", "Municipio"),
        ("fecha_cierre", "Cierre"),
        ("decision", "Recomendación"),
    ]

    cabecera = "".join(
        f"<th>{html.escape(nombre)}</th>"
        for _, nombre in columnas
    )

    filas = []

    for item in datos:
        registro = dict(item)

        registro["decision"] = (
            item["evaluacion"]["decision"]
        )

        celdas = []

        for clave, _ in columnas:
            valor = (
                registro.get(clave)
                or "No informado"
            )

            celdas.append(
                "<td>"
                + html.escape(str(valor))
                + "</td>"
            )

        filas.append(
            "<tr>"
            + "".join(celdas)
            + "</tr>"
        )

    st.markdown(
        f"""
        <div class="inti-radar-table-wrap">
          <table class="inti-radar-table">
            <thead><tr>{cabecera}</tr></thead>
            <tbody>{"".join(filas)}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# BUSCAR CONVOCATORIAS
# ============================================================

def consultar_busqueda(categoria, texto, dias):
    with st.spinner(
        "Consultando procesos de Colombia..."
    ):
        datos, error = consultar_colombia(
            categoria=categoria,
            busqueda=texto,
            dias=dias,
            limite=500,
        )

    st.session_state[
        "radar_co_resultados"
    ] = preparar(datos)

    st.session_state[
        "radar_co_error"
    ] = error

    st.session_state[
        "radar_co_criterios"
    ] = (categoria, texto, dias)


def mostrar_ficha(item, indice):
    with st.container(border=True):
        st.markdown(
            f"#### {titulo_corto(item, 160)}"
        )

        st.write(
            "**Entidad:** "
            + (item.get("entidad") or "No informada")
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.caption(
                "Presupuesto: "
                + formato_presupuesto(item)
            )

        with col2:
            st.caption(
                "Cierre: "
                + (
                    item.get("fecha_cierre")
                    or "No informado"
                )
            )

        with col3:
            st.caption(
                "Vigencia: "
                + estado_vigencia(item)
            )

        evaluacion = item["evaluacion"]

        st.write(
            "**Recomendación:** "
            + evaluacion["decision"]
        )

        st.caption(evaluacion["motivo"])

        with st.expander(
            "Ver información y verificaciones"
        ):
            st.write(
                "**Código:** "
                + (item.get("codigo") or "Sin dato")
            )

            st.write(
                "**Territorio registrado:** "
                + item.get("region", "")
                + " / "
                + item.get("localidad", "")
            )

            st.write(
                "**Estado:** "
                + (item.get("estado") or "Sin dato")
            )

            st.write(
                "**Descripción:** "
                + (
                    item.get("descripcion")
                    or "No disponible"
                )
            )

            st.markdown(
                "**Verificaciones pendientes**"
            )

            for pendiente in evaluacion[
                "pendientes"
            ]:
                st.write("- " + pendiente)

            st.caption(
                "La ubicación registrada puede "
                "corresponder a la entidad contratante "
                "y no al lugar de ejecución."
            )

        enlace = item.get("enlace", "")

        if isinstance(enlace, str) and enlace.startswith(
            ("https://", "http://")
        ):
            st.link_button(
                "Abrir fuente del proceso",
                enlace,
                use_container_width=True,
            )

        identificador = (
            f"{item.get('pais', 'Colombia')}:"
            f"{item.get('codigo', '')}"
        )

        workspace = iniciar_workspace()
        ya_guardada = (
            identificador in workspace["expedientes"]
        )

        col_guardar, col_activar = st.columns(2)

        with col_guardar:
            if st.button(
                "Actualizar guardada"
                if ya_guardada
                else "Guardar oportunidad",
                key=f"guardar_co_{indice}_"
                    f"{item.get('codigo', indice)}",
                use_container_width=True,
            ):
                guardar_oportunidad(item)
                st.success(
                    "Oportunidad incorporada "
                    "a Mis oportunidades."
                )

        with col_activar:
            if st.button(
                "Trabajar en esta oportunidad",
                key=f"activar_co_{indice}_"
                    f"{item.get('codigo', indice)}",
                type="primary",
                use_container_width=True,
            ):
                guardar_y_activar(item)
                ir_analisis()


def pestaña_buscar():
    st.markdown(
        '<div class="inti-radar-section">'
        '01. Buscar oportunidades en Colombia'
        '</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        categoria = st.selectbox(
            "Tipo de proyecto",
            ["Todas"] + list(CATEGORIAS.keys()),
            key="radar_co_categoria",
        )

    with col2:
        dias = st.selectbox(
            "Periodo de publicación",
            [30, 90, 180, 365],
            index=2,
            format_func=lambda x: f"Últimos {x} días",
            key="radar_co_dias",
        )

    texto = st.text_input(
        "Palabra clave adicional",
        placeholder=(
            "Ej. luminaria solar, subestación, "
            "interventoría..."
        ),
        key="radar_co_texto",
    )

    if st.button(
        "Buscar convocatorias",
        key="radar_co_buscar",
        type="primary",
        use_container_width=True,
    ):
        consultar_busqueda(
            categoria,
            texto,
            dias,
        )

    criterios = st.session_state.get(
        "radar_co_criterios"
    )

    if criterios is None:
        st.info(
            "Selecciona el sector y presiona "
            "Buscar convocatorias."
        )
        return

    if criterios != (categoria, texto, dias):
        st.warning(
            "Cambiaste los criterios. Presiona "
            "Buscar convocatorias para actualizar."
        )
        return

    error = st.session_state.get(
        "radar_co_error"
    )

    if error:
        st.error(error)
        return

    datos = st.session_state.get(
        "radar_co_resultados", []
    )

    st.markdown(
        '<div class="inti-radar-section">'
        '02. Filtrar resultados'
        '</div>',
        unsafe_allow_html=True,
    )

    col_region, col_ciudad = st.columns(2)

    with col_region:
        departamento = st.selectbox(
            "Departamento",
            opciones_territoriales(
                datos, "region"
            ),
            key="radar_co_departamento",
        )

    datos_region = [
        item for item in datos
        if departamento == "Todas"
        or item["region"] == departamento
    ]

    with col_ciudad:
        municipio = st.selectbox(
            "Municipio",
            opciones_territoriales(
                datos_region, "localidad"
            ),
            key=(
                "radar_co_municipio_"
                + departamento
            ),
        )

    decision = st.selectbox(
        "Recomendación INTILED",
        [
            "Todas",
            "Evaluar participación individual",
            "Evaluar alianza",
            "No participar",
            "Pendiente de verificación",
        ],
        key="radar_co_decision",
    )

    filtradas = filtrar_oportunidades(
        datos,
        region=departamento,
        localidad=municipio,
        decision=decision,
    )

    st.markdown(
        '<div class="inti-radar-section">'
        '03. Resultados identificados'
        '</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Resultados",
        len(filtradas),
    )

    c2.metric(
        "Guardadas",
        len(listar_oportunidades()),
    )

    c3.metric(
        "Por verificar",
        sum(
            estado_vigencia(x) == "Por verificar"
            for x in filtradas
        ),
    )

    st.caption(
        "Los resultados corresponden a los "
        "registros recuperados, no necesariamente "
        "a todos los procesos del país."
    )

    if not filtradas:
        st.info(
            "No se encontraron resultados con "
            "estos criterios."
        )
        return

    maximo = st.selectbox(
        "Resultados por página",
        [5, 10, 20],
        index=1,
        key="radar_co_maximo",
    )

    paginas = max(
        1,
        (len(filtradas) + maximo - 1) // maximo,
    )

    pagina = st.selectbox(
        "Página",
        list(range(1, paginas + 1)),
        key=(
            f"radar_co_pagina_{departamento}_"
            f"{municipio}_{decision}_{len(filtradas)}"
        ),
    )

    inicio = (pagina - 1) * maximo
    visibles = filtradas[
        inicio:inicio + maximo
    ]

    tabla_html(visibles)

    st.markdown(
        '<div class="inti-radar-section">'
        '04. Seleccionar convocatoria'
        '</div>',
        unsafe_allow_html=True,
    )

    for indice, item in enumerate(
        visibles, start=inicio
    ):
        mostrar_ficha(item, indice)


# ============================================================
# MIS OPORTUNIDADES
# ============================================================

def tarjeta_expediente(expediente):
    identificador = expediente["id"]
    item = expediente["oportunidad"]

    activa = oportunidad_activa()
    es_activa = (
        activa is not None
        and activa["id"] == identificador
    )

    with st.container(border=True):
        st.markdown(
            f"#### {titulo_corto(item, 150)}"
        )

        st.write(
            "**Entidad:** "
            + (
                item.get("entidad")
                or "No informada"
            )
        )

        st.write(
            "**Código:** "
            + (
                item.get("codigo")
                or "Sin código"
            )
        )

        st.write(
            "**Estado de gestión:** "
            + expediente["estado"]
        )

        if es_activa:
            st.success(
                "Esta es la oportunidad activa."
            )

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "Activar expediente",
                key=f"workspace_activar_{identificador}",
                use_container_width=True,
                disabled=es_activa,
            ):
                activar_oportunidad(
                    identificador
                )
                st.rerun()

        with col2:
            if st.button(
                "Abrir análisis",
                key=f"workspace_analizar_{identificador}",
                use_container_width=True,
                type="primary",
            ):
                activar_oportunidad(
                    identificador
                )
                ir_analisis()

        with st.expander(
            "Gestionar expediente"
        ):
            estado = st.selectbox(
                "Estado de seguimiento",
                ESTADOS,
                index=(
                    ESTADOS.index(expediente["estado"])
                    if expediente["estado"] in ESTADOS
                    else 0
                ),
                key=f"workspace_estado_{identificador}",
            )

            notas = st.text_area(
                "Notas de seguimiento",
                value=expediente.get(
                    "notas", ""
                ),
                height=120,
                key=f"workspace_notas_{identificador}",
                placeholder=(
                    "Registra requisitos, pendientes, "
                    "reuniones, aliados potenciales..."
                ),
            )

            if st.button(
                "Guardar seguimiento",
                key=f"workspace_guardar_{identificador}",
                use_container_width=True,
            ):
                actualizar_estado(
                    identificador, estado
                )
                actualizar_notas(
                    identificador, notas
                )
                st.success(
                    "Seguimiento actualizado."
                )

            st.markdown("**Historial de actividad**")

            historial = expediente.get(
                "historial", []
            )

            for evento in reversed(
                historial[-20:]
            ):
                st.caption(
                    f"{evento.get('fecha', '')} · "
                    f"{evento.get('accion', '')}"
                )

            st.divider()

            confirmar = st.checkbox(
                "Confirmo que deseo retirar "
                "esta oportunidad de la sesión",
                key=f"workspace_confirmar_{identificador}",
            )

            if st.button(
                "Retirar expediente",
                key=f"workspace_retirar_{identificador}",
                disabled=not confirmar,
            ):
                retirar_oportunidad(
                    identificador
                )
                st.rerun()


def pestaña_mis_oportunidades():
    expedientes = listar_oportunidades()
    activa = oportunidad_activa()

    st.markdown(
        '<div class="inti-radar-section">'
        'Portafolio de convocatorias'
        '</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Oportunidades guardadas",
        len(expedientes),
    )

    c2.metric(
        "En evaluación",
        sum(
            exp["estado"] == "En evaluación"
            for exp in expedientes
        ),
    )

    c3.metric(
        "Preparando propuesta",
        sum(
            exp["estado"] == "Preparando propuesta"
            for exp in expedientes
        ),
    )

    if activa:
        st.info(
            "Expediente activo: "
            + titulo_corto(
                activa["oportunidad"],
                110,
            )
        )
    else:
        st.info(
            "No hay expediente activo. "
            "Puedes activar cualquiera "
            "de tus oportunidades guardadas."
        )

    if not expedientes:
        st.warning(
            "Todavía no tienes oportunidades "
            "guardadas. Utiliza la pestaña "
            "Buscar convocatorias."
        )

    else:
        filtro_estado = st.selectbox(
            "Filtrar por estado",
            ["Todos"] + ESTADOS,
            key="workspace_filtro_estado",
        )

        visibles = [
            expediente
            for expediente in expedientes
            if filtro_estado == "Todos"
            or expediente["estado"] == filtro_estado
        ]

        for expediente in visibles:
            tarjeta_expediente(expediente)

    st.markdown(
        '<div class="inti-radar-section">'
        'Respaldo de expedientes'
        '</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Los datos se conservan durante la "
        "sesión actual de INTI. Descarga un "
        "respaldo para recuperarlos después "
        "de cerrar o reiniciar la aplicación."
    )

    st.download_button(
        "Exportar mis oportunidades",
        data=exportar_workspace(),
        file_name=(
            "inti_oportunidades_respaldo.json"
        ),
        mime="application/json",
        use_container_width=True,
        key="workspace_exportar",
    )

    archivo = st.file_uploader(
        "Restaurar respaldo de oportunidades",
        type=["json"],
        key="workspace_importar_archivo",
    )

    if archivo is not None:
        if st.button(
            "Importar respaldo",
            key="workspace_importar_boton",
            use_container_width=True,
        ):
            contenido = archivo.getvalue().decode(
                "utf-8"
            )

            correcto, mensaje = importar_workspace(
                contenido
            )

            if correcto:
                st.success(mensaje)
                st.rerun()
            else:
                st.error(mensaje)


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def mostrar_radar():
    iniciar_workspace()
    sincronizar_legacy()

    estilos_radar()
    encabezado()

    tab_buscar, tab_guardadas = st.tabs([
        "Buscar convocatorias",
        "Mis oportunidades",
    ])

    with tab_buscar:
        pestaña_buscar()

    with tab_guardadas:
        pestaña_mis_oportunidades()

    st.caption(
        "INTI Projects Enterprise · "
        "INTILED SAS BIC · Colombia"
    )
