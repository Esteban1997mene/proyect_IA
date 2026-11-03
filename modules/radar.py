
# modules/radar.py

import html
from datetime import date

import streamlit as st

from services.radar_sources import (
    CATEGORIAS,
    PROVINCIAS_ECUADOR,
    SERCOP_URL,
    consultar_colombia,
    consultar_ecuador,
    consultar_detalle_ecuador,
    enriquecer_ecuador,
    filtrar_oportunidades,
    opciones_territoriales,
    estado_vigencia,
)

from services.opportunity_classifier import (
    evaluar_oportunidad,
)


def estilos():
    st.markdown("""
    <style>
    .radar-hero {
        background:linear-gradient(115deg,#202630,#303A48);
        border-radius:18px;
        padding:32px 35px;
        margin-bottom:25px;
        border:1px solid #3D4653;
    }
    .radar-eyebrow {
        color:#FFAD72;
        font-size:12px;
        font-weight:800;
        letter-spacing:1.6px;
        margin-bottom:12px;
    }
    .radar-title {
        color:#FFFFFF;
        font-size:38px;
        font-weight:800;
        margin-bottom:12px;
    }
    .radar-description {
        color:#D2D9E3;
        font-size:16px;
        line-height:1.7;
        max-width:850px;
    }
    .radar-section {
        font-size:21px;
        font-weight:750;
        color:#242C39;
        margin:28px 0 15px;
    }
    .radar-table-wrap {
        overflow-x:auto;
        border:1px solid #E5EAF0;
        border-radius:14px;
        background:#FFFFFF;
    }
    .radar-table {
        width:100%;
        border-collapse:collapse;
        font-size:14px;
    }
    .radar-table th {
        background:#202630;
        color:white;
        padding:14px;
        text-align:left;
        white-space:nowrap;
    }
    .radar-table td {
        padding:14px;
        border-bottom:1px solid #E5EAF0;
        vertical-align:top;
        color:#242C39;
    }
    .radar-table tr:hover td {
        background:#FFF6EE;
    }
    .radar-note {
        font-size:13px;
        color:#707A89;
        line-height:1.7;
    }
    </style>
    """, unsafe_allow_html=True)


def encabezado():
    st.markdown("""
    <div class="radar-hero">
      <div class="radar-eyebrow">
        INTILED SAS BIC · INTELIGENCIA COMERCIAL
      </div>
      <div class="radar-title">
        Radar de oportunidades
      </div>
      <div class="radar-description">
        Explora convocatorias de Colombia y Ecuador.
        Selecciona el tipo de proyecto, filtra por
        territorio y evalúa la pertinencia comercial
        para INTILED.
      </div>
    </div>
    """, unsafe_allow_html=True)


def preparar(datos):
    resultado = []

    for item in datos:
        registro = dict(item)
        registro["evaluacion"] = (
            evaluar_oportunidad(registro)
        )
        resultado.append(registro)

    return resultado


def presupuesto(item):
    valor = item.get("presupuesto")

    if valor is None:
        return "No informado"

    moneda = item.get("moneda", "")

    try:
        return f"{moneda} {float(valor):,.0f}"
    except (ValueError, TypeError):
        return "No informado"


def consultar(pais, categoria, busqueda, dias, anio):
    with st.spinner(
        f"Consultando oportunidades de {pais}..."
    ):
        if pais == "Colombia":
            datos, error = consultar_colombia(
                categoria=categoria,
                busqueda=busqueda,
                dias=dias,
                limite=500,
            )
        else:
            datos, error = consultar_ecuador(
                categoria=categoria,
                busqueda=busqueda,
                anio=anio,
                paginas=2,
            )

    st.session_state["radar_resultados"] = (
        preparar(datos)
    )

    st.session_state["radar_error"] = error

    st.session_state["radar_consulta"] = {
        "pais": pais,
        "categoria": categoria,
        "busqueda": busqueda,
        "dias": dias,
        "anio": anio,
    }


def tabla_resultados(datos):
    columnas = [
        ("titulo", "Objeto"),
        ("entidad", "Entidad"),
        ("region", "Departamento / provincia"),
        ("localidad", "Municipio / cantón"),
        ("fecha_cierre", "Cierre"),
        ("recomendacion", "Recomendación"),
    ]

    encabezados = "".join(
        f"<th>{html.escape(nombre)}</th>"
        for _, nombre in columnas
    )

    filas = []

    for item in datos:
        valores = dict(item)
        valores["recomendacion"] = (
            item["evaluacion"]["decision"]
        )

        celdas = "".join(
            "<td>"
            + html.escape(
                str(valores.get(clave) or "No informado")
            )
            + "</td>"
            for clave, _ in columnas
        )

        filas.append(f"<tr>{celdas}</tr>")

    contenido = "".join(filas)

    st.markdown(
        f"""
        <div class="radar-table-wrap">
          <table class="radar-table">
            <thead><tr>{encabezados}</tr></thead>
            <tbody>{contenido}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def detalle_oportunidad(item, indice):
    evaluacion = item["evaluacion"]

    with st.container(border=True):
        st.markdown(
            f"### {item.get('titulo') or 'Sin título'}"
        )

        st.write(
            "**Entidad:** "
            + (
                item.get("entidad")
                or "No informada"
            )
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            st.write(
                "**Presupuesto:** "
                + presupuesto(item)
            )

        with c2:
            st.write(
                "**Publicación:** "
                + (
                    item.get("fecha_publicacion")
                    or "Sin dato"
                )
            )

        with c3:
            st.write(
                "**Cierre:** "
                + (
                    item.get("fecha_cierre")
                    or "Por verificar"
                )
            )

        st.write(
            "**Recomendación preliminar:** "
            + evaluacion["decision"]
        )

        st.caption(evaluacion["motivo"])

        with st.expander(
            "Consultar evaluación completa"
        ):
            st.write(
                "**País:** " + item["pais"]
            )

            st.write(
                "**Departamento / provincia:** "
                + item["region"]
            )

            st.write(
                "**Municipio / cantón:** "
                + item["localidad"]
            )

            st.write(
                "**Tipo de ubicación:** "
                + item.get(
                    "tipo_ubicacion",
                    "No determinada"
                )
            )

            st.write(
                "**Estado registrado:** "
                + item.get(
                    "estado",
                    "No informado"
                )
            )

            st.write(
                "**Vigencia:** "
                + estado_vigencia(item)
            )

            st.write(
                "**Código:** "
                + item.get(
                    "codigo",
                    "No informado"
                )
            )

            st.write(
                "**Fuente:** "
                + item.get(
                    "fuente",
                    "No informada"
                )
            )

            if item.get("categorias"):
                st.write(
                    "**Sectores:** "
                    + ", ".join(
                        item["categorias"]
                    )
                )

            st.markdown(
                "#### Verificaciones pendientes"
            )

            for pendiente in evaluacion[
                "pendientes"
            ]:
                st.write("- " + pendiente)

            if item.get("descripcion"):
                st.markdown(
                    "#### Descripción del proceso"
                )
                st.write(
                    item["descripcion"][:5000]
                )

            st.caption(
                "La recomendación no constituye "
                "certificación de cumplimiento. "
                "La ubicación de ejecución debe "
                "confirmarse en los documentos."
            )

        # Detalle OCDS solo cuando se solicita.
        if (
            item["pais"] == "Ecuador"
            and item.get("ocid")
        ):
            if st.button(
                "Consultar detalle SERCOP",
                key=f"detalle_sercop_{indice}",
                use_container_width=True,
            ):
                with st.spinner(
                    "Consultando registro oficial..."
                ):
                    detalle, error = (
                        consultar_detalle_ecuador(
                            item["ocid"]
                        )
                    )

                if error:
                    st.error(error)
                else:
                    enriquecido = enriquecer_ecuador(
                        item, detalle
                    )

                    st.session_state[
                        "radar_resultados"
                    ] = [
                        enriquecido
                        if x.get("codigo")
                        == item.get("codigo")
                        else x
                        for x in st.session_state[
                            "radar_resultados"
                        ]
                    ]

                    st.success(
                        "Se recuperó el registro OCDS. "
                        "Revisa los datos disponibles."
                    )
                    st.rerun()

        enlace = item.get("enlace", "")

        if enlace.startswith(
            ("http://", "https://")
        ):
            st.link_button(
                "Abrir documento o proceso",
                enlace,
                use_container_width=True,
            )

        if st.button(
            "Enviar a Análisis INTILED",
            type="primary",
            use_container_width=True,
            key=f"analizar_radar_{indice}",
        ):
            st.session_state[
                "oportunidad_seleccionada"
            ] = item

            st.session_state["navegar_a"] = (
                "🧠 Análisis INTILED"
            )
            st.rerun()


def mostrar_radar():
    estilos()
    encabezado()

    if "radar_resultados" not in st.session_state:
        st.session_state["radar_resultados"] = []

    if "radar_error" not in st.session_state:
        st.session_state["radar_error"] = None

    if "radar_consulta" not in st.session_state:
        st.session_state["radar_consulta"] = None

    st.markdown(
        '<div class="radar-section">'
        '01. Configurar búsqueda</div>',
        unsafe_allow_html=True,
    )

    pais = st.selectbox(
        "País",
        ["Colombia", "Ecuador"],
        key="radar_pais_v2",
    )

    categoria = st.selectbox(
        "Tipo de proyecto",
        ["Todas"] + list(CATEGORIAS.keys()),
        key="radar_categoria_v2",
        help=(
            "Selecciona la línea comercial "
            "que deseas consultar."
        ),
    )

    busqueda = st.text_input(
        "Palabra clave adicional (opcional)",
        placeholder=(
            "Ej. luminarias solares, "
            "interventoría, subestación..."
        ),
        key="radar_busqueda_v2",
    )

    col1, col2 = st.columns(2)

    with col1:
        if pais == "Colombia":
            dias = st.selectbox(
                "Publicados en los últimos",
                [30, 90, 180, 365],
                index=2,
                format_func=lambda x: (
                    f"{x} días"
                ),
                key="radar_dias_v2",
            )
            anio = date.today().year
        else:
            dias = 180
            anio = st.selectbox(
                "Año de contratación",
                list(
                    range(
                        date.today().year,
                        2014,
                        -1
                    )
                ),
                key="radar_anio_v2",
            )

    with col2:
        st.caption(
            "Colombia: SECOP II. "
            "Ecuador: API oficial SERCOP OCDS."
        )

    if st.button(
        "Buscar oportunidades",
        type="primary",
        use_container_width=True,
        key="radar_buscar_v2",
    ):
        consultar(
            pais,
            categoria,
            busqueda,
            dias,
            anio,
        )

    consulta = st.session_state[
        "radar_consulta"
    ]

    if consulta is None:
        st.info(
            "Selecciona el país y el tipo "
            "de proyecto, luego presiona Buscar."
        )
        return

    if consulta["pais"] != pais:
        st.info(
            "Cambiaste de país. Presiona Buscar "
            "para consultar la nueva fuente."
        )
        return

    if (
        consulta["categoria"] != categoria
        or consulta["busqueda"] != busqueda
        or consulta["dias"] != dias
        or consulta["anio"] != anio
    ):
        st.warning(
            "Los criterios cambiaron. Presiona "
            "Buscar para actualizar los resultados."
        )
        return

    error = st.session_state["radar_error"]

    if error:
        st.warning(error)

    datos = st.session_state[
        "radar_resultados"
    ]

    st.markdown(
        '<div class="radar-section">'
        '02. Ubicación territorial</div>',
        unsafe_allow_html=True,
    )

    regiones = opciones_territoriales(
        datos, "region"
    )

    col_region, col_localidad = (
        st.columns(2)
    )

    with col_region:
        region = st.selectbox(
            (
                "Departamento"
                if pais == "Colombia"
                else "Provincia"
            ),
            regiones,
            key=f"region_radar_v2_{pais}",
        )

    datos_region = [
        item for item in datos
        if region == "Todas"
        or item["region"] == region
    ]

    localidades = opciones_territoriales(
        datos_region,
        "localidad",
    )

    with col_localidad:
        localidad = st.selectbox(
            (
                "Municipio"
                if pais == "Colombia"
                else "Cantón / ciudad"
            ),
            localidades,
            key=(
                f"localidad_radar_v2_"
                f"{pais}_{region}"
            ),
        )

    decisiones = [
        "Todas",
        "Evaluar participación individual",
        "Evaluar alianza",
        "No participar",
        "Pendiente de verificación",
    ]

    decision = st.selectbox(
        "Ruta de participación",
        decisiones,
        key="decision_radar_v2",
    )

    filtradas = filtrar_oportunidades(
        datos,
        region=region,
        localidad=localidad,
        decision=decision,
    )

    st.markdown(
        '<div class="radar-section">'
        '03. Resumen de resultados</div>',
        unsafe_allow_html=True,
    )

    individuales = sum(
        x["evaluacion"]["decision"]
        == "Evaluar participación individual"
        for x in filtradas
    )

    alianzas = sum(
        x["evaluacion"]["decision"]
        == "Evaluar alianza"
        for x in filtradas
    )

    pendientes = sum(
        x["evaluacion"]["decision"]
        == "Pendiente de verificación"
        for x in filtradas
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Oportunidades", len(filtradas)
    )
    c2.metric(
        "Evaluar individual", individuales
    )
    c3.metric(
        "Evaluar alianza", alianzas
    )
    c4.metric(
        "Pendientes", pendientes
    )

    if not filtradas:
        st.info(
            "No se encontraron registros con "
            "los criterios actuales. Esto no "
            "demuestra que no existan procesos."
        )
        return

    st.caption(
        "Resultados obtenidos de la fuente "
        "consultada. Su vigencia y habilitantes "
        "deben comprobarse antes de postular."
    )

    st.markdown(
        '<div class="radar-section">'
        '04. Oportunidades identificadas</div>',
        unsafe_allow_html=True,
    )

    maximo = st.selectbox(
        "Resultados por página",
        [5, 10, 20],
        index=1,
        key="radar_limite_v2",
    )

    paginas = max(
        1,
        (len(filtradas) + maximo - 1)
        // maximo
    )

    pagina = st.selectbox(
        "Página",
        list(range(1, paginas + 1)),
        key=(
            f"pagina_radar_v2_"
            f"{pais}_{len(filtradas)}"
        ),
    )

    inicio = (pagina - 1) * maximo
    visibles = filtradas[
        inicio:inicio + maximo
    ]

    tabla_resultados(visibles)

    st.markdown(
        '<div class="radar-section">'
        '05. Evaluación individual</div>',
        unsafe_allow_html=True,
    )

    for indice, item in enumerate(
        visibles, start=inicio
    ):
        detalle_oportunidad(
            item, indice
        )

    st.caption(
        "INTI Projects Enterprise · "
        "INTILED SAS BIC. "
        "Evaluación comercial preliminar."
    )
