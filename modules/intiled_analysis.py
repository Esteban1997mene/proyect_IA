
# ============================================================
# INTI PROJECTS ENTERPRISE
# INTILED SAS BIC
#
# Archivo: modules/intiled_analysis.py
# Análisis de viabilidad por convocatoria
# ============================================================

import hashlib
import html

import streamlit as st

from services.opportunity_workspace import (
    iniciar_workspace,
    listar_oportunidades,
    oportunidad_activa,
    activar_oportunidad,
    sincronizar_legacy,
    actualizar_estado,
)

from services.analysis_workspace import (
    cargar_analisis,
    guardar_analisis,
    recomendar_participacion,
    actualizar_decision,
    resumen_analisis,
)


# ============================================================
# CONSTANTES
# ============================================================

OPCIONES_CUMPLIMIENTO = [
    "Sin verificar",
    "Cumple - verificado",
    "No cumple - verificado",
]

OPCIONES_ESTADO = [
    "Pendiente",
    "En evaluación",
    "Evaluado",
]

OPCIONES_CONSORCIO = [
    "Sin verificar",
    "Sí, confirmado en pliegos",
    "No, confirmado en pliegos",
]

OPCIONES_DECISION = [
    "Pendiente de verificación",
    "Evaluar participación individual",
    "Evaluar alianza",
    "No recomendar postulación individual",
    "No participar",
]


# ============================================================
# ESTILOS INTILED
# ============================================================

def estilos_analisis():

    st.markdown(
        """
        <style>

        .inti-analysis-hero {
            background: linear-gradient(
                115deg,
                #202630,
                #303A48
            );
            border-radius: 18px;
            padding: 30px 34px;
            margin-bottom: 24px;
        }

        .inti-analysis-eyebrow {
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 1.5px;
            color: #FFAD72;
            margin-bottom: 12px;
        }

        .inti-analysis-title {
            color: #FFFFFF;
            font-size: 35px;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 12px;
        }

        .inti-analysis-description {
            color: #D2D9E3;
            font-size: 15px;
            line-height: 1.7;
        }

        .inti-analysis-heading {
            font-size: 20px;
            font-weight: 750;
            color: #242C39;
            margin: 24px 0 14px;
        }

        .inti-analysis-label {
            color: #F47721;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }

        .inti-analysis-object {
            color: #242C39;
            font-weight: 750;
            font-size: 20px;
            line-height: 1.5;
        }

        .inti-analysis-muted {
            color: #718092;
            font-size: 13px;
            line-height: 1.7;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# UTILIDADES
# ============================================================

def identificador_seguro(identificador):

    return hashlib.sha256(
        str(identificador).encode("utf-8")
    ).hexdigest()[:14]


def valor_cumplimiento(valor):

    if valor is True:
        return "Cumple - verificado"

    if valor is False:
        return "No cumple - verificado"

    return "Sin verificar"


def convertir_cumplimiento(texto):

    if texto == "Cumple - verificado":
        return True

    if texto == "No cumple - verificado":
        return False

    return None


def valor_consorcio(valor):

    if valor is True:
        return "Sí, confirmado en pliegos"

    if valor is False:
        return "No, confirmado en pliegos"

    return "Sin verificar"


def convertir_consorcio(texto):

    if texto == "Sí, confirmado en pliegos":
        return True

    if texto == "No, confirmado en pliegos":
        return False

    return None


def indice_opcion(opciones, valor):

    if valor in opciones:
        return opciones.index(valor)

    return 0


def formato_dinero(valor):

    if valor is None:
        return "No informado"

    try:
        return f"$ {float(valor):,.0f} COP"

    except (ValueError, TypeError):
        return "No informado"


def mostrar_resultado(mensaje, correcto):

    if correcto:
        st.success(mensaje)

    else:
        st.error(mensaje)


# ============================================================
# ENCABEZADO
# ============================================================

def mostrar_encabezado():

    st.markdown(
        """
        <div class="inti-analysis-hero">

            <div class="inti-analysis-eyebrow">
                INTILED SAS BIC · EVALUACIÓN DE VIABILIDAD
            </div>

            <div class="inti-analysis-title">
                Análisis INTILED
            </div>

            <div class="inti-analysis-description">
                Evalúa los requisitos técnicos,
                jurídicos, financieros y comerciales
                de cada convocatoria.

                La información se organiza de manera
                independiente por expediente.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SELECCIONAR EXPEDIENTE
# ============================================================

def selector_expedientes():

    expedientes = listar_oportunidades()

    if not expedientes:

        st.info(
            "Todavía no tienes oportunidades "
            "guardadas. Entra al Radar de "
            "oportunidades y guarda una convocatoria."
        )

        return False

    activo = oportunidad_activa()

    opciones = [
        expediente["id"]
        for expediente in expedientes
    ]

    etiquetas = {}

    for expediente in expedientes:

        oportunidad = expediente.get(
            "oportunidad", {}
        )

        titulo = oportunidad.get(
            "titulo", "Sin título"
        )

        codigo = oportunidad.get(
            "codigo", "Sin código"
        )

        etiquetas[expediente["id"]] = (
            f"{codigo} · {titulo[:90]}"
        )

    if activo and activo["id"] in opciones:

        posicion = opciones.index(
            activo["id"]
        )

    else:
        posicion = 0

    st.markdown(
        '<div class="inti-analysis-heading">'
        '01. Selección de convocatoria'
        '</div>',
        unsafe_allow_html=True,
    )

    columna_selector, columna_boton = (
        st.columns([3, 1])
    )

    with columna_selector:

        seleccion = st.selectbox(
            "Expediente de trabajo",
            opciones,
            index=posicion,
            format_func=lambda identificador: (
                etiquetas.get(
                    identificador,
                    identificador
                )
            ),
            key=(
                "inti_analysis_selector_"
                + str(activo["id"] if activo else "none")
            ),
        )

    with columna_boton:

        st.write("")

        st.write("")

        cambiar = st.button(
            "Activar expediente",
            type="primary",
            use_container_width=True,
            key="inti_analysis_activar",
        )

    if cambiar:

        if activar_oportunidad(seleccion):

            sincronizar_legacy()

            st.rerun()

        else:

            st.error(
                "No fue posible activar "
                "la convocatoria seleccionada."
            )

    if activo is None:

        st.warning(
            "Selecciona un expediente y "
            "presiona Activar expediente."
        )

        return False

    return True


# ============================================================
# FICHA DE LA CONVOCATORIA
# ============================================================

def ficha_convocatoria(expediente):

    item = expediente.get(
        "oportunidad", {}
    )

    titulo = html.escape(
        str(
            item.get("titulo")
            or "Convocatoria sin título"
        )
    )

    st.markdown(
        '<div class="inti-analysis-heading">'
        '02. Expediente activo'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):

        st.markdown(
            '<div class="inti-analysis-label">'
            'CONVOCATORIA SELECCIONADA'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="inti-analysis-object">'
            f'{titulo}'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.write("")

        c1, c2 = st.columns(2)

        with c1:

            st.write(
                "**Entidad contratante:** "
                + str(
                    item.get("entidad")
                    or "No informada"
                )
            )

            st.write(
                "**Código del proceso:** "
                + str(
                    item.get("codigo")
                    or "No informado"
                )
            )

            st.write(
                "**Departamento:** "
                + str(
                    item.get("region")
                    or "Sin determinar"
                )
            )

        with c2:

            st.write(
                "**Presupuesto:** "
                + formato_dinero(
                    item.get("presupuesto")
                )
            )

            st.write(
                "**Fecha de cierre:** "
                + str(
                    item.get("fecha_cierre")
                    or "Por verificar"
                )
            )

            st.write(
                "**Municipio registrado:** "
                + str(
                    item.get("localidad")
                    or "Sin determinar"
                )
            )

        st.caption(
            "La ubicación puede corresponder "
            "a la entidad contratante y no al "
            "lugar de ejecución del contrato."
        )


# ============================================================
# FORMULARIO DE COMPONENTE
# ============================================================

def formulario_componente(
    identificador,
    nombre_componente,
    titulo,
    campos,
):

    analisis = cargar_analisis()

    if analisis is None:
        return

    datos = analisis.get(
        nombre_componente, {}
    )

    sufijo = (
        identificador_seguro(identificador)
        + "_"
        + nombre_componente
    )

    st.markdown(f"#### {titulo}")

    with st.form(
        key=f"form_{sufijo}"
    ):

        estado = st.selectbox(
            "Estado de evaluación",
            OPCIONES_ESTADO,
            index=indice_opcion(
                OPCIONES_ESTADO,
                datos.get("estado", "Pendiente")
            ),
            key=f"estado_{sufijo}",
        )

        cumplimiento = st.selectbox(
            "Cumplimiento verificado",
            OPCIONES_CUMPLIMIENTO,
            index=indice_opcion(
                OPCIONES_CUMPLIMIENTO,
                valor_cumplimiento(
                    datos.get("cumplimiento")
                )
            ),
            help=(
                "Marca Cumple o No cumple "
                "únicamente cuando exista "
                "soporte documental."
            ),
            key=f"cumplimiento_{sufijo}",
        )

        nuevos_datos = {
            "estado": estado,
            "cumplimiento": convertir_cumplimiento(
                cumplimiento
            ),
        }

        for campo, etiqueta in campos:

            nuevos_datos[campo] = st.text_area(
                etiqueta,
                value=str(
                    datos.get(campo, "") or ""
                ),
                height=110,
                key=f"{campo}_{sufijo}",
            )

        if nombre_componente == "analisis_juridico":

            consorcio = st.selectbox(
                "¿Los pliegos permiten consorcio "
                "o unión temporal?",
                OPCIONES_CONSORCIO,
                index=indice_opcion(
                    OPCIONES_CONSORCIO,
                    valor_consorcio(
                        datos.get("permite_consorcio")
                    )
                ),
                key=f"consorcio_{sufijo}",
            )

            nuevos_datos[
                "permite_consorcio"
            ] = convertir_consorcio(
                consorcio
            )

        enviar = st.form_submit_button(
            "Guardar evaluación",
            type="primary",
            use_container_width=True,
        )

    if enviar:

        actualizado = cargar_analisis()

        if actualizado is None:

            st.error(
                "No hay una convocatoria activa."
            )

            return

        if (
            actualizado.get("identificador")
            != identificador
        ):

            st.error(
                "Cambió el expediente activo. "
                "La información no fue guardada."
            )

            return

        actualizado[
            nombre_componente
        ].update(nuevos_datos)

        correcto, mensaje = guardar_analisis(
            actualizado
        )

        mostrar_resultado(
            mensaje, correcto
        )


# ============================================================
# EVALUACIÓN TÉCNICA
# ============================================================

def evaluacion_tecnica(identificador):

    formulario_componente(
        identificador,
        "analisis_tecnico",
        "Evaluación técnica",
        [
            (
                "experiencia_requerida",
                "Experiencia exigida por los pliegos",
            ),
            (
                "experiencia_acreditada",
                "Experiencia contractual acreditada "
                "por INTILED",
            ),
            (
                "capacidad_operativa",
                "Capacidad técnica y operativa",
            ),
            (
                "observaciones",
                "Observaciones técnicas",
            ),
        ],
    )


# ============================================================
# EVALUACIÓN JURÍDICA
# ============================================================

def evaluacion_juridica(identificador):

    formulario_componente(
        identificador,
        "analisis_juridico",
        "Evaluación jurídica",
        [
            (
                "requisitos_habilitantes",
                "Requisitos jurídicos habilitantes",
            ),
            (
                "documentos_pendientes",
                "Documentos por verificar o subsanar",
            ),
            (
                "observaciones",
                "Observaciones jurídicas",
            ),
        ],
    )


# ============================================================
# EVALUACIÓN FINANCIERA
# ============================================================

def evaluacion_financiera(identificador):

    formulario_componente(
        identificador,
        "analisis_financiero",
        "Evaluación financiera",
        [
            (
                "indicadores_requeridos",
                "Indicadores financieros exigidos",
            ),
            (
                "capacidad_financiera",
                "Capacidad financiera de INTILED",
            ),
            (
                "garantias",
                "Garantías y condiciones económicas",
            ),
            (
                "observaciones",
                "Observaciones financieras",
            ),
        ],
    )


# ============================================================
# EVALUACIÓN COMERCIAL
# ============================================================

def evaluacion_comercial(identificador):

    formulario_componente(
        identificador,
        "analisis_comercial",
        "Evaluación comercial",
        [
            (
                "competidores",
                "Competidores identificados",
            ),
            (
                "aliados_potenciales",
                "Aliados estratégicos potenciales",
            ),
            (
                "riesgos",
                "Riesgos comerciales y operativos",
            ),
            (
                "observaciones",
                "Observaciones comerciales",
            ),
        ],
    )


# ============================================================
# RECOMENDACIÓN Y DECISIÓN
# ============================================================

def seccion_decision(identificador):

    st.markdown(
        '<div class="inti-analysis-heading">'
        '04. Recomendación de participación'
        '</div>',
        unsafe_allow_html=True,
    )

    analisis = cargar_analisis()

    if analisis is None:
        return

    recomendacion = recomendar_participacion(
        analisis
    )

    with st.container(border=True):

        st.markdown(
            "**Resultado preliminar del sistema**"
        )

        st.info(
            recomendacion["resultado"]
        )

        st.write(
            recomendacion["justificacion"]
        )

        st.caption(
            "Esta recomendación utiliza los "
            "cumplimientos registrados por el usuario. "
            "No verifica automáticamente el contenido "
            "de los pliegos ni certifica requisitos."
        )

    decision_actual = analisis.get(
        "decision", {}
    )

    sufijo = identificador_seguro(
        identificador
    )

    with st.form(
        key=f"decision_form_{sufijo}"
    ):

        resultado = st.selectbox(
            "Decisión de seguimiento",
            OPCIONES_DECISION,
            index=indice_opcion(
                OPCIONES_DECISION,
                decision_actual.get(
                    "resultado",
                    "Pendiente de verificación"
                )
            ),
            key=f"decision_resultado_{sufijo}",
        )

        justificacion = st.text_area(
            "Justificación de la decisión",
            value=str(
                decision_actual.get(
                    "justificacion", ""
                )
            ),
            height=140,
            key=f"decision_justificacion_{sufijo}",
        )

        responsable = st.text_input(
            "Responsable de la evaluación",
            value=str(
                decision_actual.get(
                    "responsable", ""
                )
            ),
            key=f"decision_responsable_{sufijo}",
        )

        guardar = st.form_submit_button(
            "Guardar decisión",
            type="primary",
            use_container_width=True,
        )

    if guardar:

        activo = oportunidad_activa()

        if (
            activo is None
            or activo["id"] != identificador
        ):

            st.error(
                "La convocatoria activa cambió. "
                "No se guardó la decisión."
            )

            return

        correcto, mensaje = actualizar_decision(
            resultado,
            justificacion,
            responsable,
        )

        mostrar_resultado(
            mensaje,
            correcto,
        )


# ============================================================
# HISTORIAL
# ============================================================

def seccion_historial():

    st.markdown(
        '<div class="inti-analysis-heading">'
        '05. Historial del análisis'
        '</div>',
        unsafe_allow_html=True,
    )

    analisis = cargar_analisis()

    if analisis is None:
        return

    historial = analisis.get(
        "historial", []
    )

    if not historial:

        st.info(
            "Todavía no existen registros "
            "de análisis guardados."
        )

        return

    for evento in reversed(
        historial[-25:]
    ):

        with st.container(border=True):

            st.write(
                "**Fecha:** "
                + str(
                    evento.get("fecha", "")
                )
            )

            st.write(
                evento.get("evento", "")
            )


# ============================================================
# RESUMEN GENERAL
# ============================================================

def resumen_general():

    st.markdown(
        '<div class="inti-analysis-heading">'
        '06. Resumen de evaluaciones'
        '</div>',
        unsafe_allow_html=True,
    )

    registros = resumen_analisis()

    if not registros:

        st.info(
            "No existen evaluaciones "
            "guardadas todavía."
        )

        return

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Convocatorias evaluadas",
        len(registros),
    )

    c2.metric(
        "Pendientes de verificación",
        sum(
            registro["decision"]
            == "Pendiente de verificación"
            for registro in registros
        ),
    )

    c3.metric(
        "Alianzas por evaluar",
        sum(
            registro["decision"]
            == "Evaluar alianza"
            for registro in registros
        ),
    )

    for registro in registros:

        with st.expander(
            str(
                registro.get("convocatoria")
                or "Sin título"
            )[:100]
        ):

            st.write(
                "**Entidad:** "
                + str(
                    registro.get("entidad", "")
                )
            )

            st.write(
                "**Decisión:** "
                + str(
                    registro.get("decision", "")
                )
            )

            st.write(
                "**Última actualización:** "
                + str(
                    registro.get(
                        "ultima_actualizacion"
                    ) or "Sin dato"
                )
            )


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def mostrar_analisis_intiled():

    iniciar_workspace()
    sincronizar_legacy()

    estilos_analisis()
    mostrar_encabezado()

    if not selector_expedientes():
        return

    expediente = oportunidad_activa()

    if expediente is None:
        return

    identificador = expediente["id"]

    ficha_convocatoria(expediente)

    st.markdown(
        '<div class="inti-analysis-heading">'
        '03. Evaluación de requisitos'
        '</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Cada evaluación queda asociada al "
        "identificador de la convocatoria activa."
    )

    tabs = st.tabs([
        "Técnico",
        "Jurídico",
        "Financiero",
        "Comercial",
    ])

    with tabs[0]:
        evaluacion_tecnica(identificador)

    with tabs[1]:
        evaluacion_juridica(identificador)

    with tabs[2]:
        evaluacion_financiera(identificador)

    with tabs[3]:
        evaluacion_comercial(identificador)

    seccion_decision(identificador)

    with st.expander(
        "Consultar historial y resumen",
        expanded=False,
    ):
        seccion_historial()
        resumen_general()

    st.divider()

    st.caption(
        "INTI Projects Enterprise · "
        "INTILED SAS BIC · "
        "Evaluación preliminar por expediente."
    )


# Alias para compatibilidad con nombres
# alternativos utilizados en app.py.

def mostrar_analisis():
    return mostrar_analisis_intiled()


def mostrar_analisis_inti():
    return mostrar_analisis_intiled()
