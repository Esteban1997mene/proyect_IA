
# ============================================================
# INTI PROJECTS ENTERPRISE
# INTILED SAS BIC
#
# ARCHIVO: modules/intiled_analysis.py
#
# ANALISIS AUTOMATICO DE VIABILIDAD CON GOOGLE GEMINI
#
# Version: 3.0
#
# Funciones:
# - Seleccionar expedientes independientes
# - Consultar documentos cargados
# - Analizar automaticamente con Gemini
# - Mostrar evaluacion tecnica, juridica y financiera
# - Recomendar participacion, alianza o descarte
# - Guardar resultados por convocatoria
# - Exportar informe de evaluacion
# ============================================================

import hashlib
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from services.opportunity_workspace import (
    iniciar_workspace,
    listar_oportunidades,
    oportunidad_activa,
    activar_oportunidad,
    sincronizar_legacy,
    guardar_datos_modulo,
    obtener_datos_modulo,
    actualizar_estado,
)

from services.ai_viability import (
    api_configurada,
    documentos_del_expediente,
    evaluar_con_ia,
    DECISIONES,
)


# ============================================================
# CONFIGURACION GENERAL
# ============================================================

MODULO_IA = "analisis_intiled_ia"

ZONA = ZoneInfo("America/Bogota")

ESTADOS_IA = {
    "FAVORABLE": "Favorable preliminar",
    "RIESGO": "Requiere revision",
    "NO_CUMPLE": "Incumplimiento identificado",
    "SIN_EVIDENCIA": "Sin evidencia suficiente",
}

ESTADOS_GESTION = {
    "INDIVIDUAL": "En evaluación",
    "ALIANZA": "Evaluando alianza",
    "NO_PARTICIPAR": "No participar",
    "PENDIENTE": "Por revisar",
}


# ============================================================
# FUNCIONES DE UTILIDAD
# ============================================================

def codigo_seguro(valor):
    return hashlib.sha256(
        str(valor).encode("utf-8")
    ).hexdigest()[:14]


def fecha_actual():
    return datetime.now(ZONA).isoformat(
        timespec="seconds"
    )


def formato_presupuesto(valor, moneda="COP"):
    if valor is None:
        return "No informado"

    try:
        return (
            f"{moneda} "
            f"${float(valor):,.0f}"
        )

    except (ValueError, TypeError):
        return "No informado"


def texto_seguro(valor, defecto="No informado"):
    if valor is None:
        return defecto

    texto = str(valor).strip()

    return texto if texto else defecto


def titulo_corto(texto, limite=110):
    texto = str(texto or "Sin titulo")

    if len(texto) > limite:
        return texto[:limite] + "..."

    return texto


def guardar_resultado(expediente, resultado):
    """
    Protege el expediente activo.
    No guarda resultados en otra convocatoria.
    """

    activo = oportunidad_activa()

    if activo is None:
        return False

    if activo["id"] != expediente["id"]:
        return False

    if resultado.get("expediente_id") != (
        expediente["id"]
    ):
        return False

    correcto = guardar_datos_modulo(
        MODULO_IA,
        resultado,
    )

    if not correcto:
        return False

    decision = resultado.get(
        "decision", "PENDIENTE"
    )

    estado = ESTADOS_GESTION.get(
        decision, "Por revisar"
    )

    actualizar_estado(
        expediente["id"],
        estado,
    )

    return True


def cargar_resultado():
    expediente = oportunidad_activa()

    if expediente is None:
        return None

    resultado = obtener_datos_modulo(
        MODULO_IA,
        defecto=None,
    )

    if not isinstance(resultado, dict):
        return None

    if resultado.get("expediente_id") != (
        expediente["id"]
    ):
        return None

    return resultado


# ============================================================
# ESTILOS CORPORATIVOS
# ============================================================

def estilos_intiled():

    st.markdown(
        """
        <style>

        /* Estilos exclusivos del modulo */

        .inti-ai-result {
            background: #FFFFFF;
            border: 1px solid #E5EAF0;
            border-left: 5px solid #F47721;
            border-radius: 13px;
            padding: 22px;
            margin: 12px 0 20px 0;
        }

        .inti-ai-result-title {
            color: #242C39;
            font-size: 22px;
            font-weight: 800;
            margin-bottom: 10px;
        }

        .inti-ai-result-text {
            color: #566273;
            font-size: 15px;
            line-height: 1.75;
        }

        .inti-ai-divider {
            height: 3px;
            width: 65px;
            background: #F47721;
            border-radius: 3px;
            margin: 12px 0 20px 0;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# ENCABEZADO
# ============================================================

def mostrar_encabezado():
    """
    Se utilizan elementos nativos Streamlit
    para evitar que el HTML aparezca como texto.
    """

    with st.container(border=True):

        st.caption(
            "INTILED SAS BIC | INTI PROJECTS ENTERPRISE"
        )

        st.title(
            "Analisis de viabilidad"
        )

        st.markdown(
            "Evaluacion asistida por **Google Gemini** "
            "para determinar la conveniencia de "
            "participar en convocatorias de Colombia."
        )

        st.write(
            "El sistema analiza la informacion "
            "disponible, identifica riesgos "
            "y recomienda una ruta de participacion."
        )

        st.markdown(
            '<div class="inti-ai-divider"></div>',
            unsafe_allow_html=True,
        )


# ============================================================
# SELECTOR DE CONVOCATORIAS
# ============================================================

def seleccionar_convocatoria():

    st.subheader(
        "01. Seleccionar convocatoria"
    )

    expedientes = listar_oportunidades()

    if not expedientes:

        st.warning(
            "Todavia no existen convocatorias "
            "guardadas. Ingresa al Radar "
            "y guarda una oportunidad."
        )

        return None

    activo = oportunidad_activa()

    opciones = [
        expediente["id"]
        for expediente in expedientes
    ]

    nombres = {}

    for expediente in expedientes:

        oportunidad = expediente.get(
            "oportunidad", {}
        )

        codigo = texto_seguro(
            oportunidad.get("codigo"),
            "Sin codigo",
        )

        titulo = titulo_corto(
            oportunidad.get("titulo"),
            95,
        )

        nombres[expediente["id"]] = (
            codigo + " | " + titulo
        )

    posicion = 0

    if activo and activo["id"] in opciones:
        posicion = opciones.index(
            activo["id"]
        )

    c1, c2 = st.columns([3, 1])

    with c1:

        seleccionado = st.selectbox(
            "Expediente de trabajo",
            opciones,
            index=posicion,
            format_func=lambda valor: (
                nombres.get(valor, valor)
            ),
            key=(
                "inti_ai_selector_"
                + codigo_seguro(
                    activo["id"]
                    if activo else "sin_activo"
                )
            ),
        )

    with c2:

        st.write("")
        st.write("")

        if st.button(
            "Activar expediente",
            type="primary",
            use_container_width=True,
            key="inti_ai_activar",
        ):

            if activar_oportunidad(
                seleccionado
            ):

                sincronizar_legacy()

                st.rerun()

            else:

                st.error(
                    "No fue posible activar "
                    "el expediente seleccionado."
                )

    if activo is None:

        st.info(
            "Selecciona una convocatoria "
            "y presiona Activar expediente."
        )

        return None

    return activo


# ============================================================
# FICHA DE CONVOCATORIA ACTIVA
# ============================================================

def mostrar_convocatoria(expediente):

    st.subheader(
        "02. Informacion de la convocatoria"
    )

    oportunidad = expediente.get(
        "oportunidad", {}
    )

    with st.container(border=True):

        st.markdown(
            "### "
            + texto_seguro(
                oportunidad.get("titulo"),
                "Convocatoria sin titulo",
            )
        )

        st.write(
            "**Entidad contratante:** "
            + texto_seguro(
                oportunidad.get("entidad")
            )
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Presupuesto",
                formato_presupuesto(
                    oportunidad.get("presupuesto"),
                    oportunidad.get(
                        "moneda", "COP"
                    ),
                ),
            )

        with col2:

            st.metric(
                "Departamento",
                texto_seguro(
                    oportunidad.get("region")
                ),
            )

        with col3:

            st.metric(
                "Fecha de cierre",
                texto_seguro(
                    oportunidad.get("fecha_cierre"),
                    "Por verificar",
                ),
            )

        st.write(
            "**Codigo del proceso:** "
            + texto_seguro(
                oportunidad.get("codigo")
            )
        )

        st.write(
            "**Municipio registrado:** "
            + texto_seguro(
                oportunidad.get("localidad")
            )
        )

        st.write(
            "**Estado oficial registrado:** "
            + texto_seguro(
                oportunidad.get("estado")
            )
        )

        st.caption(
            "Los datos territoriales pueden "
            "corresponder a la entidad contratante. "
            "La fecha de cierre y la vigencia "
            "deben confirmarse en SECOP II."
        )

        enlace = oportunidad.get(
            "enlace", ""
        )

        if (
            isinstance(enlace, str)
            and enlace.startswith(
                ("https://", "http://")
            )
        ):

            st.link_button(
                "Consultar proceso oficial",
                enlace,
                use_container_width=True,
            )


# ============================================================
# VERIFICAR DOCUMENTACION DISPONIBLE
# ============================================================

def mostrar_documentos(expediente):

    st.subheader(
        "03. Documentacion disponible"
    )

    documentos = documentos_del_expediente(
        expediente
    )

    total_caracteres = sum(
        documento.get("caracteres", 0)
        for documento in documentos
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Documentos legibles",
            len(documentos),
        )

    with col2:

        st.metric(
            "Caracteres extraidos",
            f"{total_caracteres:,}",
        )

    if not documentos:

        st.warning(
            "No se han incorporado pliegos "
            "ni anexos legibles a esta convocatoria."
        )

        st.info(
            "Gemini puede revisar el objeto "
            "contractual disponible, pero "
            "sin los pliegos no puede verificar "
            "los requisitos habilitantes."
        )

    else:

        st.success(
            "Se encontro documentacion "
            "asociada a esta convocatoria."
        )

        with st.expander(
            "Consultar documentos disponibles"
        ):

            for documento in documentos:

                st.markdown(
                    "**"
                    + documento["nombre"]
                    + "**"
                )

                st.caption(
                    texto_seguro(
                        documento.get("tipo"),
                        "Documento",
                    )
                    + " | "
                    + str(
                        documento.get(
                            "caracteres", 0
                        )
                    )
                    + " caracteres"
                )

        if len(documentos) > 6:

            st.warning(
                "El motor actual procesa "
                "como maximo seis documentos "
                "por ejecucion."
            )

    st.caption(
        "Los documentos se cargan desde "
        "la pestaña Analisis documental. "
        "La IA empleara el texto extraido "
        "que se encuentra en el expediente."
    )

    return documentos


# ============================================================
# EJECUTAR GEMINI
# ============================================================

def ejecutar_analisis(expediente):

    st.subheader(
        "04. Evaluacion automatica con Gemini"
    )

    conectado = api_configurada()

    if conectado:

        st.success(
            "El motor Google Gemini "
            "tiene una clave API configurada."
        )

    else:

        st.error(
            "No se encuentra configurada "
            "la clave GEMINI_API_KEY."
        )

        st.caption(
            "Configura la clave en "
            "Streamlit Cloud > Settings > Secrets."
        )

    st.write(
        "El sistema examinara los datos "
        "de la convocatoria y los documentos "
        "disponibles para proponer una decision "
        "comercial fundamentada."
    )

    st.caption(
        "Cada ejecucion puede consumir cuota "
        "o generar cargos en Google Gemini."
    )

    boton = st.button(
        "Analizar viabilidad con Gemini",
        type="primary",
        use_container_width=True,
        disabled=not conectado,
        key=(
            "inti_ai_ejecutar_"
            + codigo_seguro(
                expediente["id"]
            )
        ),
    )

    if not boton:
        return

    activo = oportunidad_activa()

    if (
        activo is None
        or activo["id"] != expediente["id"]
    ):

        st.error(
            "El expediente cambio antes "
            "de ejecutar el analisis."
        )

        return

    with st.spinner(
        "Gemini esta evaluando los requisitos "
        "y la viabilidad de la convocatoria..."
    ):

        resultado, error = evaluar_con_ia(
            expediente
        )

    if error:

        st.error(
            "No fue posible completar "
            "el analisis."
        )

        st.warning(error)

        return

    if not isinstance(resultado, dict):

        st.error(
            "Gemini no devolvio "
            "un resultado valido."
        )

        return

    if resultado.get(
        "expediente_id"
    ) != expediente["id"]:

        st.error(
            "El identificador de la respuesta "
            "no coincide con la convocatoria."
        )

        return

    correcto = guardar_resultado(
        expediente,
        resultado,
    )

    if correcto:

        st.success(
            "El analisis fue realizado "
            "y guardado en el expediente."
        )

        st.rerun()

    else:

        st.error(
            "No se pudo guardar el resultado "
            "en el expediente activo."
        )


# ============================================================
# COMPONENTES DE ANALISIS
# ============================================================

def mostrar_componentes(resultado):

    st.subheader(
        "06. Evaluacion por componentes"
    )

    componentes = resultado.get(
        "componentes", []
    )

    if not componentes:

        st.info(
            "No hay componentes disponibles."
        )

        return

    for componente in componentes:

        criterio = texto_seguro(
            componente.get("criterio"),
            "Criterio sin nombre",
        )

        estado = componente.get(
            "estado",
            "SIN_EVIDENCIA",
        )

        etiqueta = ESTADOS_IA.get(
            estado,
            "Por verificar",
        )

        with st.expander(
            criterio + " | " + etiqueta,
            expanded=estado != "FAVORABLE",
        ):

            st.markdown(
                "**Analisis del especialista**"
            )

            st.write(
                texto_seguro(
                    componente.get("analisis"),
                    "No disponible",
                )
            )

            st.markdown(
                "**Evidencia utilizada**"
            )

            st.write(
                texto_seguro(
                    componente.get("evidencia"),
                    "No aportada",
                )
            )

            st.markdown(
                "**Accion recomendada**"
            )

            st.write(
                texto_seguro(
                    componente.get("accion"),
                    "Revisar documentacion",
                )
            )


# ============================================================
# LISTAS DE RESULTADOS
# ============================================================

def mostrar_lista(titulo, elementos):

    st.markdown(
        "#### " + titulo
    )

    if not isinstance(elementos, list):
        elementos = []

    if not elementos:

        st.caption(
            "Sin elementos registrados."
        )

        return

    for elemento in elementos:

        st.markdown(
            "- " + str(elemento)
        )


# ============================================================
# MOSTRAR RECOMENDACION
# ============================================================

def mostrar_decision(resultado):

    st.subheader(
        "05. Recomendacion de Gemini"
    )

    decision = resultado.get(
        "decision",
        "PENDIENTE",
    )

    etiqueta = DECISIONES.get(
        decision,
        "Informacion insuficiente",
    )

    st.markdown(
        '<div class="inti-ai-result">'
        '<div class="inti-ai-result-title">'
        'Resultado del analisis'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        "## " + etiqueta
    )

    resumen = texto_seguro(
        resultado.get("resumen"),
        "Sin resumen",
    )

    st.write(resumen)

    st.markdown(
        "**Justificacion de la recomendacion**"
    )

    st.write(
        texto_seguro(
            resultado.get("justificacion"),
            "Sin justificacion",
        )
    )

    confianza = resultado.get(
        "confianza",
        "BAJA",
    )

    st.caption(
        "Confianza declarada por Gemini: "
        + str(confianza)
    )

    st.caption(
        "Fecha del analisis: "
        + texto_seguro(
            resultado.get("fecha"),
            "Sin fecha",
        )
    )

    st.caption(
        "Modelo utilizado: "
        + texto_seguro(
            resultado.get("modelo"),
            "Google Gemini",
        )
    )

    st.info(
        "Esta evaluacion es preliminar. "
        "La recomendacion debe contrastarse "
        "con los pliegos oficiales y la "
        "experiencia contractual acreditada "
        "por INTILED."
    )


# ============================================================
# PLAN DE ACCION
# ============================================================

def mostrar_plan_accion(resultado):

    st.subheader(
        "07. Plan de accion recomendado"
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "Requisitos pendientes",
        "Riesgos",
        "Alianzas",
        "Proximos pasos",
    ])

    with tab1:

        mostrar_lista(
            "Requisitos pendientes",
            resultado.get(
                "requisitos_pendientes", []
            ),
        )

    with tab2:

        mostrar_lista(
            "Riesgos identificados",
            resultado.get(
                "riesgos", []
            ),
        )

    with tab3:

        mostrar_lista(
            "Aliados estrategicos requeridos",
            resultado.get(
                "alianzas_recomendadas", []
            ),
        )

    with tab4:

        mostrar_lista(
            "Proximas actividades",
            resultado.get(
                "proximos_pasos", []
            ),
        )


# ============================================================
# FUENTES Y LIMITACIONES
# ============================================================

def mostrar_fuentes(resultado):

    with st.expander(
        "Fuentes revisadas y limitaciones"
    ):

        mostrar_lista(
            "Documentos considerados",
            resultado.get(
                "fuentes_revisadas", []
            ),
        )

        mostrar_lista(
            "Limitaciones de la evaluacion",
            resultado.get(
                "limitaciones", []
            ),
        )


# ============================================================
# EXPORTAR RESULTADO
# ============================================================

def exportar_analisis(expediente, resultado):

    st.subheader(
        "08. Descargar informe de evaluacion"
    )

    oportunidad = expediente.get(
        "oportunidad", {}
    )

    informe = {
        "organizacion": "INTILED SAS BIC",
        "plataforma": "INTI Projects Enterprise",
        "motor": "Google Gemini",
        "expediente_id": expediente["id"],
        "fecha_exportacion": fecha_actual(),
        "convocatoria": oportunidad,
        "analisis": resultado,
        "advertencia": (
            "Evaluacion preliminar asistida por IA. "
            "Requiere validacion humana y documental."
        ),
    }

    contenido = json.dumps(
        informe,
        ensure_ascii=False,
        indent=2,
        default=str,
    )

    archivo = (
        "INTILED_Analisis_"
        + codigo_seguro(expediente["id"])
        + ".json"
    )

    st.download_button(
        "Descargar informe de viabilidad",
        data=contenido,
        file_name=archivo,
        mime="application/json",
        use_container_width=True,
        key=(
            "inti_ai_descargar_"
            + codigo_seguro(
                expediente["id"]
            )
        ),
    )

    st.caption(
        "El archivo JSON contiene la "
        "evaluacion estructurada. "
        "No es una propuesta contractual "
        "ni reemplaza los soportes originales."
    )


# ============================================================
# MOSTRAR RESULTADO DEL EXPEDIENTE
# ============================================================

def mostrar_analisis_guardado(expediente):

    resultado = cargar_resultado()

    if resultado is None:

        st.info(
            "Esta convocatoria todavia "
            "no tiene un analisis de Gemini. "
            "Presiona el boton Analizar "
            "viabilidad con Gemini."
        )

        return

    st.divider()

    mostrar_decision(resultado)

    mostrar_componentes(resultado)

    mostrar_plan_accion(resultado)

    mostrar_fuentes(resultado)

    exportar_analisis(
        expediente,
        resultado,
    )


# ============================================================
# FUNCION PRINCIPAL
# ============================================================

def mostrar_analisis_intiled():

    iniciar_workspace()

    sincronizar_legacy()

    estilos_intiled()

    mostrar_encabezado()

    expediente = seleccionar_convocatoria()

    if expediente is None:
        return

    mostrar_convocatoria(expediente)

    mostrar_documentos(expediente)

    ejecutar_analisis(expediente)

    mostrar_analisis_guardado(
        expediente
    )

    st.divider()

    st.caption(
        "INTI Projects Enterprise | "
        "INTILED SAS BIC | "
        "Analisis de viabilidad con Google Gemini"
    )


# ============================================================
# ALIAS DE COMPATIBILIDAD
# ============================================================

def mostrar_analisis():
    return mostrar_analisis_intiled()


def mostrar_analisis_inti():
    return mostrar_analisis_intiled()
