
# modules/radar.py

import streamlit as st
import pandas as pd

from services.radar_sources import (
    consultar_colombia,
    importar_ecuador,
    opciones_territoriales,
    filtrar_oportunidades,
    SERCOP_URL,
)

from services.opportunity_classifier import (
    evaluar_oportunidad,
    LINEAS_INTILED,
)


# ============================================================
# DISEÑO CORPORATIVO
# ============================================================

def estilos_radar():
    st.markdown(
        """
        <style>
        .radar-hero {
            background: linear-gradient(
                115deg, #202630, #303A48
            );
            border-radius: 18px;
            padding: 30px 34px;
            margin-bottom: 25px;
            border: 1px solid #3D4653;
        }

        .radar-eyebrow {
            color: #FFAD72;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 1.7px;
            margin-bottom: 12px;
        }

        .radar-title {
            color: #FFFFFF;
            font-size: clamp(30px, 3vw, 39px);
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 12px;
        }

        .radar-description {
            color: #D2D9E3;
            font-size: 16px;
            line-height: 1.7;
            max-width: 850px;
        }

        .radar-section {
            font-size: 21px;
            font-weight: 750;
            color: #242C39;
            margin: 28px 0 15px;
        }

        .radar-card {
            background: #FFFFFF;
            border: 1px solid #E5EAF0;
            border-radius: 14px;
            padding: 20px;
            margin: 12px 0;
        }

        .radar-card-title {
            color: #242C39;
            font-size: 18px;
            font-weight: 750;
            line-height: 1.5;
        }

        .radar-meta {
            color: #707A89;
            font-size: 14px;
            margin-top: 8px;
            line-height: 1.7;
        }

        .radar-footer {
            color: #7A8492;
            font-size: 13px;
            padding: 20px 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def encabezado():
    st.markdown(
        """
        <div class="radar-hero">
            <div class="radar-eyebrow">
                INTILED SAS BIC · INTELIGENCIA COMERCIAL
            </div>
            <div class="radar-title">
                Radar de oportunidades
            </div>
            <div class="radar-description">
                Identifica oportunidades en Colombia y Ecuador,
                explora los territorios de interés y recibe
                una recomendación preliminar de participación
                según las líneas de trabajo de INTILED.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# UTILIDADES
# ============================================================

def preparar_oportunidades(datos):
    resultado = []

    for item in datos:
        registro = dict(item)
        registro["evaluacion"] = evaluar_oportunidad(
            registro
        )
        resultado.append(registro)

    return resultado


def formato_presupuesto(item):
    valor = item.get("presupuesto")

    if valor is None:
        return "No informado"

    moneda = item.get("moneda", "")

    return f"{moneda} {valor:,.0f}"


def opciones_decision():
    return [
        "Todas",
        "Evaluar participación individual",
        "Evaluar alianza",
        "No participar",
        "Pendiente de verificación",
    ]


def cargar_colombia():
    with st.spinner("Consultando SECOP II..."):
        datos, error = consultar_colombia(limite=1000)

    if error:
        st.error(error)
        return

    st.session_state["radar_colombia"] = (
        preparar_oportunidades(datos)
    )
    st.session_state["radar_colombia_consultado"] = True


def mostrar_detalle(item, indice):
    evaluacion = item["evaluacion"]

    with st.expander(
        "Ver evaluación y detalles",
        expanded=False
    ):
        st.markdown("#### Información del proceso")

        st.write(
            f"**Entidad:** {item.get('entidad') or 'No informada'}"
        )
        st.write(
            f"**Código:** {item.get('codigo') or 'No informado'}"
        )
        st.write(
            f"**Estado registrado:** "
            f"{item.get('estado') or 'No informado'}"
        )
        st.write(
            f"**Fecha de cierre:** "
            f"{item.get('fecha_cierre') or 'No informada'}"
        )
        st.write(
            f"**Presupuesto:** {formato_presupuesto(item)}"
        )

        st.markdown("#### Evaluación preliminar INTILED")

        st.write(
            f"**Recomendación:** {evaluacion['decision']}"
        )
        st.write(
            f"**Resultado técnico:** {evaluacion['nivel']}"
        )
        st.write(evaluacion["motivo"])

        if evaluacion["lineas"]:
            st.write(
                "**Líneas relacionadas:** "
                + ", ".join(evaluacion["lineas"])
            )

        st.markdown("#### Verificaciones pendientes")

        for pendiente in evaluacion["pendientes"]:
            st.markdown(f"- {pendiente}")

        st.caption(
            "La evaluación no certifica el cumplimiento "
            "de requisitos habilitantes. La ubicación "
            "mostrada tampoco confirma por sí sola "
            "el lugar de ejecución."
        )

        descripcion = item.get("descripcion", "")

        if descripcion:
            st.markdown("#### Descripción disponible")
            st.write(descripcion[:5000])

        enlace = item.get("enlace", "")

        if enlace.startswith(("https://", "http://")):
            st.link_button(
                "Consultar proceso en la fuente",
                enlace,
                use_container_width=True,
            )

        if st.button(
            "Enviar a Análisis INTILED",
            key=f"radar_analizar_{indice}",
            type="primary",
            use_container_width=True,
        ):
            st.session_state[
                "oportunidad_seleccionada"
            ] = item

            st.session_state["navegar_a"] = (
                "🧠 Análisis INTILED"
            )

            st.rerun()


# ============================================================
# INTERFAZ PRINCIPAL
# ============================================================

def mostrar_radar():
    estilos_radar()
    encabezado()

    if "radar_colombia" not in st.session_state:
        st.session_state["radar_colombia"] = []

    if "radar_colombia_consultado" not in st.session_state:
        st.session_state["radar_colombia_consultado"] = False

    st.markdown(
        '<div class="radar-section">01. Cobertura geográfica</div>',
        unsafe_allow_html=True
    )

    col_pais, col_fuente = st.columns([1, 2])

    with col_pais:
        pais = st.selectbox(
            "País",
            ["Colombia", "Ecuador"],
            key="radar_pais",
        )

    with col_fuente:
        if pais == "Colombia":
            st.info(
                "Fuente: datos abiertos de SECOP II. "
                "La consulta inicial recupera una muestra "
                "de registros y no constituye una búsqueda "
                "exhaustiva de todas las convocatorias."
            )
        else:
            st.info(
                "Fuente: SERCOP. Para esta primera versión "
                "se requiere importar un archivo CSV "
                "obtenido de una fuente oficial."
            )

    # --------------------------------------------------------
    # OBTENCIÓN DE DATOS
    # --------------------------------------------------------

    if pais == "Colombia":

        if st.button(
            "Consultar oportunidades de Colombia",
            type="primary",
            key="radar_consultar_colombia",
        ):
            cargar_colombia()

        oportunidades = st.session_state[
            "radar_colombia"
        ]

        if not st.session_state[
            "radar_colombia_consultado"
        ]:
            st.caption(
                "Presiona Consultar para cargar los registros."
            )

    else:
        st.link_button(
            "Abrir portal oficial SERCOP",
            SERCOP_URL,
        )

        archivo = st.file_uploader(
            "Importar oportunidades de Ecuador",
            type=["csv"],
            key="radar_archivo_ecuador",
            help=(
                "Carga un CSV obtenido de una fuente "
                "oficial de contratación pública."
            ),
        )

        if archivo is not None:
            datos, error = importar_ecuador(archivo)

            if error:
                st.error(error)
                oportunidades = []
            else:
                oportunidades = preparar_oportunidades(datos)
                st.success(
                    f"Se importaron {len(oportunidades)} registros."
                )
        else:
            oportunidades = []

    # --------------------------------------------------------
    # FILTROS TERRITORIALES
    # --------------------------------------------------------

    st.markdown(
        '<div class="radar-section">02. Filtros de búsqueda</div>',
        unsafe_allow_html=True
    )

    regiones = opciones_territoriales(
        oportunidades, "region"
    )

    col_region, col_localidad = st.columns(2)

    with col_region:
        region = st.selectbox(
            "Departamento"
            if pais == "Colombia"
            else "Provincia",
            regiones,
            key=f"radar_region_{pais}",
        )

    oportunidades_region = [
        item for item in oportunidades
        if region == "Todas"
        or item["region"] == region
    ]

    localidades = opciones_territoriales(
        oportunidades_region, "localidad"
    )

    with col_localidad:
        localidad = st.selectbox(
            "Municipio"
            if pais == "Colombia"
            else "Cantón / ciudad",
            localidades,
            key=f"radar_localidad_{pais}_{region}",
        )

    col_busqueda, col_decision = st.columns([2, 1])

    with col_busqueda:
        busqueda = st.text_input(
            "Buscar por objeto, entidad o código",
            placeholder=(
                "Ej. alumbrado público, energía solar, "
                "interventoría..."
            ),
            key="radar_busqueda",
        )

    with col_decision:
        decision = st.selectbox(
            "Ruta de participación",
            opciones_decision(),
            key="radar_filtro_decision",
        )

    # --------------------------------------------------------
    # RESULTADOS
    # --------------------------------------------------------

    filtradas = filtrar_oportunidades(
        oportunidades,
        texto=busqueda,
        region=region,
        localidad=localidad,
        decision=decision,
    )

    st.markdown(
        '<div class="radar-section">03. Resultados</div>',
        unsafe_allow_html=True
    )

    individual = sum(
        1 for item in filtradas
        if item["evaluacion"]["decision"]
        == "Evaluar participación individual"
    )

    alianza = sum(
        1 for item in filtradas
        if item["evaluacion"]["decision"]
        == "Evaluar alianza"
    )

    descartadas = sum(
        1 for item in filtradas
        if item["evaluacion"]["decision"]
        == "No participar"
    )

    pendientes = sum(
        1 for item in filtradas
        if item["evaluacion"]["decision"]
        == "Pendiente de verificación"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Resultados", len(filtradas))
    c2.metric("Evaluar individual", individual)
    c3.metric("Evaluar alianza", alianza)
    c4.metric("Pendientes / descartadas", pendientes + descartadas)

    if not filtradas:
        st.info(
            "No hay resultados para los filtros actuales. "
            "Comprueba la fuente de datos o amplía la búsqueda."
        )
        return

    st.caption(
        "Las recomendaciones se basan en afinidad temática. "
        "No equivalen a una revisión de pliegos ni confirman "
        "que los procesos sigan abiertos."
    )

    # --------------------------------------------------------
    # TABLA EJECUTIVA
    # --------------------------------------------------------

    filas = []

    for item in filtradas:
        filas.append({
            "Objeto": item["titulo"],
            "Entidad": item["entidad"],
            "Territorio": (
                f"{item['region']} / {item['localidad']}"
            ),
            "Cierre": item["fecha_cierre"] or "Sin dato",
            "Presupuesto": formato_presupuesto(item),
            "Recomendación": (
                item["evaluacion"]["decision"]
            ),
        })

    st.dataframe(
        pd.DataFrame(filas),
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # FICHAS
    # --------------------------------------------------------

    st.markdown(
        '<div class="radar-section">04. Evaluación de oportunidades</div>',
        unsafe_allow_html=True
    )

    maximo = st.selectbox(
        "Resultados por página",
        [5, 10, 20, 50],
        index=1,
        key="radar_por_pagina",
    )

    paginas = max(
        1, (len(filtradas) + maximo - 1) // maximo
    )

    pagina = st.number_input(
        "Página",
        min_value=1,
        max_value=paginas,
        value=1,
        key=f"radar_pagina_{pais}_{region}_{localidad}_{decision}_{len(filtradas)}",
    )

    inicio = (pagina - 1) * maximo
    fin = inicio + maximo

    for indice, item in enumerate(
        filtradas[inicio:fin],
        start=inicio,
    ):
        with st.container(border=True):
            st.markdown(
                f"### {item['titulo']}"
            )

            st.write(
                f"**Entidad:** "
                f"{item['entidad'] or 'No informada'}"
            )

            st.write(
                f"**Ubicación registrada:** "
                f"{item['region']} / {item['localidad']}"
            )

            col1, col2 = st.columns(2)

            with col1:
                st.write(
                    f"**Presupuesto:** "
                    f"{formato_presupuesto(item)}"
                )

            with col2:
                st.write(
                    f"**Cierre:** "
                    f"{item['fecha_cierre'] or 'No informado'}"
                )

            st.write(
                "**Recomendación preliminar:** "
                + item["evaluacion"]["decision"]
            )

            st.caption(
                item["evaluacion"]["motivo"]
            )

            mostrar_detalle(item, indice)

    st.markdown(
        """
        <div class="radar-footer">
            INTILED SAS BIC · INTI Projects Enterprise<br>
            Información sujeta a verificación en las
            fuentes oficiales y documentos del proceso.
        </div>
        """,
        unsafe_allow_html=True
    )
